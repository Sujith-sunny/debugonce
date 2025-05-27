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

# Remove all handlers before adding our file handler to avoid accidental stdout/stderr logging
for handler in list(logger.handlers):
    logger.removeHandler(handler)

handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def debugonce(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import unittest.mock
        file_access_log = []
        http_request_log = []

        def normalize_url(method, url):
            try:
                return requests.Request(method, url).prepare().url
            except Exception:
                return url

        exception = None
        result = None
        import builtins as _builtins
        # Get the current open and request (may be a mock) at call time
        def get_wrapped_open():
            real_open = _builtins.open
            def open_wrapper(file, mode='r', *a, **k):
                if any(m in mode for m in ['w', 'a', 'x']):
                    operation = 'write'
                elif 'r' in mode:
                    operation = 'read'
                else:
                    operation = 'other'
                file_access_log.append({
                    "file": file,
                    "mode": mode,
                    "operation": operation,
                    "timestamp": datetime.now().isoformat()
                })
                return real_open(file, mode, *a, **k)
            return open_wrapper
        def get_wrapped_request():
            real_request = sessions.Session.request
            def request_wrapper(self, method, url, *a, **k):
                response = real_request(self, method, url, *a, **k)
                http_request_log.append({
                    "method": method,
                    "url": normalize_url(method, url),
                    "status_code": getattr(response, 'status_code', None),
                    "timestamp": datetime.now().isoformat()
                })
                return response
            return request_wrapper
        with unittest.mock.patch('builtins.open', new=get_wrapped_open()):
            with unittest.mock.patch.object(sessions.Session, 'request', new=get_wrapped_request()):
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    exception = e
                    result = None
        # Save state, but never let it swallow the original exception
        try:
            capture_state(
                func, args, kwargs,
                result=result,
                exception=exception,
                file_access_log=file_access_log,
                request_log=http_request_log
            )
        except Exception:
            logger.exception("Error capturing state in debugonce decorator")
        logger.info(f"Captured state for function {func.__name__} at {datetime.now().isoformat()}")
        if exception is not None:
            raise exception
        return result
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

    save_state(state)

def save_state(state):
    # Save the state to a file
    os.makedirs(".debugonce", exist_ok=True)
    file_path = os.path.join(".debugonce", f"session_{int(datetime.now().timestamp())}.json")
    with open(file_path, "w") as f:
        json.dump(state, f, indent=4)