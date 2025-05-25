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
        try:
            # Initialize exception as None
            exception = None
            
            # Capture environment variables
            env_vars = dict(os.environ)
            
            # Capture function name and arguments
            func_name = func.__name__
            
            # Capture current working directory
            cwd = os.getcwd()
            
            # Capture HTTP requests
            http_requests = []
            
            # Capture file access
            file_access = []
            
            # Execute function and capture result/exception
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                exception = str(e)
                result = None
            
            # Create state data
            data = {
                "function": func_name,
                "args": args,
                "kwargs": kwargs,
                "env_vars": env_vars,
                "current_working_directory": cwd,
                "http_requests": http_requests,
                "file_access": file_access,
                "exception": exception,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Ensure the .debugonce directory exists
            os.makedirs(".debugonce", exist_ok=True)
            
            # Save the state to a file in the .debugonce directory
            session_file = os.path.join(".debugonce", f"{func_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(session_file, "w") as f:
                json.dump(data, f, default=str)
            
            logger.info(f"Captured state for function {func_name} at {inspect.getfile(func)}")
            
            return result
        except Exception as e:
            logger.error(f"Error capturing state for function {func_name}: {e}")
            raise
    return wrapper

def capture_state(func, args, kwargs, result=None, exception=None, file_access_log=None, request_log=None):
    # Get function source code and imports
    try:
        func_source = inspect.getsource(func)
        module = inspect.getmodule(func)
        imports = [line for line in inspect.getsource(module).split('\n') if line.startswith('import') or line.startswith('from')]
    except Exception as e:
        func_source = f"def {func.__name__}(*args, **kwargs):\n    raise NotImplementedError('Source code not available')"
        imports = []

    state = {
        "function": func.__name__,
        "args": list(args),
        "kwargs": kwargs,
        "result": result,
        "exception": str(exception) if exception else None,
        "environment_variables": dict(os.environ),
        "current_working_directory": os.getcwd(),
        "python_version": sys.version,
        "timestamp": datetime.now().isoformat(),
        "file_access": file_access_log or [],
        "http_requests": request_log or [],
        "function_source": func_source,
        "imports": imports
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
