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
    export_file = os.path.splitext(session_file)[0] + "_replay.py"

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
@click.argument('session_file', type=click.Path(exists=True))
def export(session_file):
    """Export a bug reproduction script."""
    try:
        with open(session_file, "r") as f:
            session_data = json.load(f)
    except json.JSONDecodeError as e:
        click.echo(f"Error reading session file: {e}", err=True)
        sys.exit(1)

    if not session_data:
        click.echo("Error: Invalid session file.", err=True)
        sys.exit(1)

    function_name = session_data.get("function")
    args = session_data.get("args", [])
    kwargs = session_data.get("kwargs", {})
    exception = session_data.get("exception")
    script_content = f"""# Bug Reproduction Script
import json
import os
import sys
def test_function(a, b, c):
    return a + b + c

def replay_function():
    input_args = {args}
    input_kwargs = {kwargs}
    try:
        result = test_function(*input_args, **input_kwargs)
        print(f"Result: {{result}}")
    except Exception as e:
        print("Exception occurred during replay:", e)

if __name__ == "__main__":
    replay_function()
"""

    export_file = os.path.splitext(session_file)[0] + "_replay.py"
    with open(export_file, 'w') as f:
        f.write(script_content)
    click.echo(f"Exported bug reproduction script to {export_file}")

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