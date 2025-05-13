# tests/test_cli.py
import unittest
import subprocess
import sys
import os
import json

class TestDebugOnceCLI(unittest.TestCase):
    def setUp(self):
        """Set up a temporary .debugonce directory for testing."""
        self.session_dir = ".debugonce"
        os.makedirs(self.session_dir, exist_ok=True)
        self.session_file = os.path.join(self.session_dir, "session.json")
        with open(self.session_file, "w") as f:
            json.dump({"input": [1, 2, 3]}, f)

    def tearDown(self):
        """Clean up the temporary .debugonce directory."""
        if os.path.exists(self.session_dir):
            for file in os.listdir(self.session_dir):
                os.remove(os.path.join(self.session_dir, file))
            os.rmdir(self.session_dir)

    def test_replay(self):
        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "replay", self.session_file],
            capture_output=True,
            text=True
        )
        self.assertIn("Replaying function with input", result.stdout)

    def test_export(self):
        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "export", self.session_file],
            capture_output=True,
            text=True
        )
        self.assertIn("Exported bug reproduction script", result.stdout)

    def test_list(self):
        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "list"],
            capture_output=True,
            text=True
        )
        self.assertIn("Captured sessions", result.stdout)

    def test_clean(self):
        result = subprocess.run(
            [sys.executable, "src/debugonce_packages/cli.py", "clean"],
            capture_output=True,
            text=True
        )
        self.assertIn("Cleared all captured sessions", result.stdout)

if __name__ == "__main__":
    unittest.main()