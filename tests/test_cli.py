import subprocess
import sys
import os
import json
import unittest
import re
import pytest
import shutil

class TestDebugOnceCLI(unittest.TestCase):
    def setUp(self):
        """Set up a temporary .debugonce directory for testing."""
        self.session_dir = ".debugonce"
        os.makedirs(self.session_dir, exist_ok=True)
        self.session_file = os.path.join(self.session_dir, "session.json")
        #Create a valid json file for testing
        with open(self.session_file, "w") as f:
            json.dump({"function": "test_function",
                       "args": [1, 2, 3],
                       "kwargs": {},
                       "environment_variables": {},
                       "current_working_directory": os.getcwd(),
                       "python_version": sys.version,
                       "timestamp": "2024-01-01T00:00:00"}, f) #Simplified

    def tearDown(self):
        """Clean up the temporary .debugonce directory."""
        if os.path.exists(self.session_dir):
            shutil.rmtree(self.session_dir) #Use shutil to remove non-empty directories

    def test_inspect(self):
        """Test the inspect command."""
        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "inspect", self.session_file],
            capture_output=True,
            text=True
        )
        self.assertIn("Replaying function with input", result.stdout)

    def test_replay(self):
        """Test the replay command."""
        export_file = os.path.splitext(self.session_file)[0] + "_replay.py"

        # Check if the exported script exists
        if not os.path.exists(export_file):
            # Export the script first
            export_result = subprocess.run(
                [sys.executable, "src/debugonce_packages/cli.py", "export", self.session_file],
                capture_output=True,
                text=True,
            )
            self.assertIn(f"Exported bug reproduction script to {export_file}", export_result.stdout)
            self.assertTrue(os.path.exists(export_file))

        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "replay", self.session_file],
            capture_output=True,
            text=True,
        )
        self.assertIn("Result: 6", result.stdout)

    def test_export(self):
        """Test the export command."""
        export_file = os.path.splitext(self.session_file)[0] + "_replay.py"
        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "export", self.session_file],
            capture_output=True,
            text=True
        )
        self.assertIn("Exported bug reproduction script to", result.stdout)
        # Check for schema validation errors
        self.assertNotIn("Error reading", result.stdout)
        self.assertNotIn("Failed validating", result.stdout)

        #Verify that the function source code exists
        with open(export_file, "r") as f:
            file_content = f.read()
            self.assertIn("def test_function", file_content)

        #Verify that has the right arguments
            self.assertIn("input_args = [1, 2, 3", file_content)

    def test_list(self):
        """Test the list command."""
        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "list"],
            capture_output=True,
            text=True
        )
        self.assertIn("Captured sessions", result.stdout)

    def test_clean(self):
        """Test the clean command."""
        # First, create a file in the session directory
        test_file = os.path.join(self.session_dir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test")

        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "clean"],
            capture_output=True,
            text=True
        )
        self.assertIn("Cleared all captured sessions", result.stdout)
        self.assertFalse(os.path.exists(test_file))

    # def test_export_invalid_session_file(self):
    #     """Test the export command with an invalid session file."""
    #     invalid_session_file = os.path.join(self.session_dir, "invalid_session.json")
    #     with open(invalid_session_file, "w") as f:
    #         f.write("{\"invalid\": \"json\"}")  # An actual, invalid json

    #     # Export should print the error and return exit code 1
    #     result = subprocess.run(
    #         [sys.executable, "src/debugonce_packages/cli.py", "export", invalid_session_file],
    #         capture_output=True,
    #         text=True,
    #     )
    #     self.assertEqual(result.returncode, 1)
    #     self.assertIn("Error reading session file", result.stderr)

    # def test_inspect_invalid_session_file(self):
    #     """Test the inspect command with an invalid session file."""
    #     invalid_session_file = os.path.join(self.session_dir, "invalid_session.json")
    #     with open(invalid_session_file, "w") as f:
    #         f.write("{\"invalid\": \"json\"}")  # An actual, invalid json

    #     # Inspect should print the error and return exit code 1
    #     result = subprocess.run(
    #         [sys.executable, "src/debugonce_packages/cli.py", "inspect", invalid_session_file],
    #         capture_output=True,
    #         text=True,
    #     )
    #     self.assertEqual(result.returncode, 1)
    #     self.assertIn("Error reading session file", result.stderr)

    # def test_replay_invalid_session_file(self):
    #     """Test the replay command with an invalid session file."""
    #     invalid_session_file = os.path.join(self.session_dir, "invalid_session.json")
    #     with open(invalid_session_file, "w") as f:
    #         f.write("{\"invalid\": \"json\"}")  # An actual, invalid json

    #     # Replay should print the error and return exit code 1
    #     result = subprocess.run(
    #         [sys.executable, "src/debugonce_packages/cli.py", "replay", invalid_session_file],
    #         capture_output=True,
    #         text=True,
    #     )
    #     self.assertEqual(result.returncode, 1)
    #     self.assertIn("Error reading session file", result.stderr)