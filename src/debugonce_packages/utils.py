import os
import json
import sys

def get_environment_variables():
    return dict(os.environ)

def get_current_working_directory():
    return os.getcwd()

def get_python_version():
    return sys.version

def save_capture(data, file_path):
    """Save captured data to a JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def load_capture(file_path):
    """Load captured data from a JSON file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r") as f:
        return json.load(f)