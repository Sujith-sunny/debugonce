"""
This is the debugonce package, which provides a utility for capturing and reproducing bugs effortlessly.
"""

from .decorator import debugonce
from .cli import cli
from .utils import (
    get_environment_variables,
    get_current_working_directory,
    get_python_version,  # Ensure this is imported
)
from .storage import StorageManager  # Example storage manager import

__all__ = ['debugonce', 'cli', 'some_utility_function', 'StorageManager']