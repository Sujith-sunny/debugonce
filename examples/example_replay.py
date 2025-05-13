import os
import json
import sys
from debugonce_packages import debugonce

@debugonce
def example_function(arg1, arg2):
    # Simulate a function that may raise an exception
    if arg1 < 0:
        raise ValueError("Negative value not allowed")
    return arg1 + arg2

if __name__ == "__main__":
    # Example usage of the function
    try:
        result = example_function(int(sys.argv[1]), int(sys.argv[2]))
        print(f"Result: {result}")
    except Exception as e:
        print(f"An error occurred: {e}")
        # The debugonce decorator will handle capturing the state automatically