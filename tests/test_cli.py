import subprocess
import sys
import os
import json
import unittest
import re

class TestDebugOnceCLI(unittest.TestCase):
    def setUp(self):
        """Set up a temporary .debugonce directory for testing."""
        self.session_dir = ".debugonce"
        os.makedirs(self.session_dir, exist_ok=True)
        self.session_file = os.path.join(self.session_dir, "session.json")
        with open(self.session_file, "w") as f:
            json.dump({"function": "test_function","args": [1, 2, 3]}, f)

    def tearDown(self):
        """Clean up the temporary .debugonce directory."""
        if os.path.exists(self.session_dir):
            for file in os.listdir(self.session_dir):
                os.remove(os.path.join(self.session_dir, file))
            os.rmdir(self.session_dir)

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
        self.assertIn("Result: 6", result.stdout)  # Adjust the expected output as needed

    def test_export(self):
        """Test the export command."""
        export_file = os.path.splitext(self.session_file)[0] + "_replay.py"
        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "export", self.session_file],
            capture_output=True,
            text=True
        )
        self.assertIn(f"Exported bug reproduction script to {export_file}", result.stdout)
        self.assertTrue(os.path.exists(export_file))

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