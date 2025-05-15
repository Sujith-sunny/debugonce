# debugonce

`debugonce` is a Python utility designed to help developers effortlessly capture and reproduce bugs by recording function calls and runtime context. With the `@debugonce` decorator, you can easily log input arguments, environment variables, and more, making it simpler to diagnose issues in your code.

## Key Features

- **@debugonce Decorator**: Capture input arguments, environment variables, current working directory, Python version, and stack traces upon exceptions.
- **Optional Logging**: Capture contents of accessed files and HTTP requests if opted-in.
- **Storage**: All captured data is stored in a `.debugonce/` folder as JSON, tracebacks, and logs.
- **Command-Line Interface**: A CLI tool (`debugonce-cli`) with commands to replay, export, list, and clean captured sessions.
- **File Access Tracking:**  Added explicit mention of file access tracking in the "Key Features" section.

## Installation

To install `debugonce`, paste the following command in your terminal or code editor. :

```bash
pip install debugonce
```
<!-- or

```bash
git clone https://github.com/Sujith-sunny/debugonce.git
cd debugonce
pip install .
``` -->

## Usage

To use the `@debugonce` decorator, simply apply it to your function:

```python
from debugonce_packages import debugonce

@debugonce
def my_function(arg1, arg2):
    # Your function logic here
```

## CLI Guide

The `debugonce-cli` provides several commands:

- **replay**: Rerun the captured function with stored input.
  
  ```bash
  debugonce-cli replay session.json
  ```

- **export**: Generate a standalone bug reproduction script. Recreate the exact same scenario that led to the error. 
  
  ```bash
  debugonce-cli export session.json

- **list**: Show all captured sessions.
  
  ```bash
  debugonce-cli list
  ```

- **clean**: Clear stored sessions.
  
  ```bash
  debugonce-cli clean
  ```

## Example Outputs

After running a function decorated with `@debugonce`, you will find the captured data in the `.debugonce/` folder. This includes:

- `session_<timestamp>.json`: Contains input arguments and environment details.
- `traceback_<timestamp>.log`: Logs the stack trace if an exception occurred.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.