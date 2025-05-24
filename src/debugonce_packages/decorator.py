import functools
import inspect
import requests
from requests import sessions
import json
import os
import sys
import traceback
from datetime import datetime
import builtins  # To override the built-in open function
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
log_file = os.path.join(".debugonce", "debugonce.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logger = logging.getLogger("debugonce")
logger.setLevel(logging.DEBUG)

# Create a rotating file handler
handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def debugonce(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Capture the original open function
        original_open = builtins.open
        file_access_log = []
        request_log = [] # Add request log

        # Define a custom open function to track file access
        def custom_open(file, mode='r', *args, **kwargs):
            filepath = os.path.abspath(file)
            if not filepath.startswith(os.path.abspath(".debugonce")):
                operation = "read" if "r" in mode else "write"
                file_access_log.append({"file": filepath, "operation": operation})
            return original_open(file, mode, *args, **kwargs)

        # Replace the built-in open function with the custom one
        builtins.open = custom_open

        # Define a function to log request/response information
        def log_request_response(response, *args, **kwargs):
            request = response.request
            request_data = {
                "url": request.url,
                "method": request.method,
                "headers": dict(request.headers),
                "body": request.body.decode('utf-8') if request.body else None,
                "status_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_content": response.content.decode('utf-8', errors='ignore')[:500] if response.content else None, #Limiting content to 500 chars
            }
            request_log.append(request_data)
            return response

        # Patch the requests.Session.request method
        original_request = sessions.Session.request
        def new_request(self, *args, **kwargs):
            response = original_request(self, *args, **kwargs)
            response = log_request_response(response)
            return response

        sessions.Session.request = new_request

        try:
            # Execute the function and capture the result
            result = func(*args, **kwargs)
            capture_state(func, args, kwargs, result, file_access_log=file_access_log, request_log=request_log) #Pass request log
            return result
        except Exception as e:
            # Capture the state in case of an exception
            capture_state(func, args, kwargs, exception=e, file_access_log=file_access_log, request_log=request_log) #Pass request log
            raise
        finally:
            # Restore the original open function
            builtins.open = original_open
            # Unpatch the requests.Session.request method
            sessions.Session.request = original_request

    return wrapper

def capture_state(func, args, kwargs, result=None, exception=None, file_access_log=None, request_log=None):
    state = {
        "function": func.__name__,
        "args": list(args),  # Convert args to a list
        "kwargs": kwargs,
        "result": result,
        "exception": str(exception) if exception else None,
        "environment_variables": dict(os.environ),
        "current_working_directory": os.getcwd(),
        "python_version": sys.version,
        "timestamp": datetime.now().isoformat(),
        "file_access": file_access_log or [],  # Add file access log
        "http_requests": request_log or [] # Added http requests
    }

    if exception:
        state["stack_trace"] = traceback.format_exc()

    # Temporarily restore the original open function to avoid logging save_state operations
    original_open = builtins.open
    save_state(state)
    builtins.open = original_open

def save_state(state):
    # Save the state to a file
    os.makedirs(".debugonce", exist_ok=True)
    file_path = os.path.join(".debugonce", f"session_{int(datetime.now().timestamp())}.json")
    with open(file_path, "w") as f:
        json.dump(state, f, indent=4)

    # Log the state capture
    logger.info(f"Captured state for function {state['function']} at {state['timestamp']}")
