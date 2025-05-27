import os
import json
import click
import inspect
import importlib
import subprocess
import sys

@click.group()
def cli():
    """CLI for DebugOnce."""
    pass

def test_function(a, b, c):
    return a + b + c

@click.command()
@click.argument('session_file', type=click.Path(exists=True))
def inspect(session_file):
    """Inspect a captured session."""
    try:
        with open(session_file, "r") as f:
            session_data = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"Error reading session file: {e}", err=True)
        sys.exit(1)

    # Extract the function name, arguments, and exception
    function_name = session_data.get("function")
    args = session_data.get("args", [])
    kwargs = session_data.get("kwargs", {})
    exception = session_data.get("exception")

    click.echo("Replaying function with input") # Added line
    click.echo(f"Replaying function: {function_name}")
    click.echo(f"Arguments: {args}")
    click.echo(f"Keyword Arguments: {kwargs}")

    if exception:
        click.echo(f"Exception occurred: {exception}")
    else:
        result = session_data.get("result")
        click.echo(f"Result: {result}")

@click.command()
@click.argument('session_file', type=click.Path(exists=True))
def replay(session_file):
    """Replay a captured session by executing the exported script."""
    export_file = os.path.splitext(session_file)[0] + ".py"

    # Check if the exported script exists
    if not os.path.exists(export_file):
        click.echo(f"Error: Exported script '{export_file}' not found. Please run 'export' first.", err=True)
        sys.exit(1)

    try:
        # Execute the exported script
        result = subprocess.run(
            [sys.executable, export_file],  # Execute with the current Python interpreter
            capture_output=True,
            text=True,
            check=True  # Raise an exception for non-zero exit codes
        )
        click.echo(result.stdout)
        if result.stderr:
            click.echo(f"Error output:\n{result.stderr}")

    except subprocess.CalledProcessError as e:
        click.echo(f"Error: Script execution failed with code {e.returncode}", err=True)
        click.echo(f"Error output:\n{e.stderr}", err=True)
        sys.exit(1)
    except FileNotFoundError:
        click.echo(f"Error: Python interpreter not found. Please ensure Python is in your PATH.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"An unexpected error occurred: {e}", err=True)
        sys.exit(1)

@click.command()
@click.argument('session_file', type=click.Path())
def export(session_file):
    """Export a bug reproduction script."""
    try:
        with open(session_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                click.echo("Error reading session file: Invalid JSON format", err=True)
                sys.exit(1)

        # Validate required fields
        if "function" not in data:
            click.echo("Error generating replay script: Missing function name", err=True)
            sys.exit(1)

        # Extract data with proper key names and defaults
        func_name = data["function"]
        args = data.get("args", [])
        kwargs = data.get("kwargs", {})
        env_vars = data.get("env_vars", {})
        cwd = data.get("current_working_directory", os.getcwd())
        http_requests = data.get("http_requests", [])
        file_access = data.get("file_access", [])
        exception = data.get("exception")
        # Use function_code if present, else function_source, else empty string
        function_code = data.get("function_code") or data.get("function_source") or ""

        # Generate script content
        script_lines = ["# Bug Reproduction Script"]
        script_lines.extend(["import json", "import os", "import sys", "import requests", ""])

        # Set environment variables
        script_lines.append("# Set environment variables")
        for key, value in env_vars.items():
            script_lines.append(f'os.environ["{key}"] = "{value}"')
        script_lines.append("")

        # Set working directory
        script_lines.append("# Set current working directory")
        script_lines.append(f'os.chdir("{cwd}")')
        script_lines.append("")

        # Make HTTP requests
        script_lines.append("# Make HTTP requests")
        for request in http_requests:
            method = request.get("method", "GET").lower()
            url = request.get("url", "")
            headers = request.get("headers", {})
            if method == "get":
                script_lines.append(f'requests.get("{url}", headers={json.dumps(headers)})')
            elif method == "post":
                body = request.get("body", "")
                script_lines.append(f'requests.post("{url}", headers={json.dumps(headers)}, data={json.dumps(body)})')
        script_lines.append("")

        # Access files
        script_lines.append("# Access files")
        for file in file_access:
            mode = file.get("mode", "r")  # Default to 'r' if mode is not specified
            script_lines.append(f'with open("{file["file"]}", "{mode}") as f:')
            script_lines.append("    pass")
        script_lines.append("")

        # Function implementation
        script_lines.append("# Function implementation")
        if function_code:
            # Remove @debugonce decorator if present
            import re
            function_code_clean = re.sub(r'@debugonce\s*\n', '', function_code)
            script_lines.append(function_code_clean)
        else:
            script_lines.append(f"def {func_name}(*args, **kwargs):\n    raise NotImplementedError('Function source not available')")
        script_lines.append("")

        # Main execution
        # Use repr() for each argument to preserve correct types (strings quoted, numbers as-is, etc.)
        arg_strs = [repr(arg) for arg in args]
        script_lines.extend([
            "if __name__ == \"__main__\":",
            "    try:",
            f"        result = {func_name}({', '.join(arg_strs)})",  # Direct function call with repr'd args
            "        print(f\"Function returned: {result}\")",
            "    except Exception as e:",
            "        print(f\"Exception occurred during replay: {e}\", file=sys.stderr)",
            "        sys.exit(1)"
        ])
        # Capture exception if present
        if exception:
            script_lines.append(f"print(\"Captured exception: {exception}\")")

        # Write script to file
        export_file = os.path.splitext(session_file)[0] + "_replay.py"
        with open(export_file, "w") as f:
            f.write("\n".join(script_lines))

        return 0

    except FileNotFoundError:
        click.echo("Error reading session file: File not found", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error generating replay script: {str(e)}", err=True)
        sys.exit(1)

@click.command()
def list():
    """List all captured sessions."""
    session_dir = ".debugonce"
    if not os.path.exists(session_dir):
        click.echo("No captured sessions found.")
        return
    sessions = os.listdir(session_dir)
    if not sessions:
        click.echo("No captured sessions found.")
    else:
        click.echo("Captured sessions:")
        for session in sessions:
            click.echo(f"- {session}")

@click.command()
def clean():
    """Clean all captured sessions."""
    session_dir = ".debugonce"
    if os.path.exists(session_dir):
        for file in os.listdir(session_dir):
            os.remove(os.path.join(session_dir, file))
        click.echo("Cleared all captured sessions.")
    else:
        click.echo("No captured sessions to clean.")

cli.add_command(inspect)
cli.add_command(replay)
cli.add_command(export)
cli.add_command(list)
cli.add_command(clean)

def main():
    """Entry point for the CLI."""
    cli()

if __name__ == '__main__':
    main()