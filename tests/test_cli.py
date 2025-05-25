import unittest
import json
import os
from click.testing import CliRunner
from src.debugonce_packages.cli import export
import subprocess
import sys

class TestDebugOnceCLI(unittest.TestCase):
    def setUp(self):
        self.session_data = {
            "function": "divide",
            "args": [4, 2],
            "kwargs": {},
            "http_requests": [
                {
                    "url": "https://example.com",
                    "method": "GET",
                    "headers": {
                        "User-Agent": "debugonce"
                    },
                    "body": None,
                    "status_code": 200,
                    "response_headers": {
                        "Content-Type": "text/html"
                    }
                }
            ],
            "python_version": "3.11.5",
            "current_working_directory": "/Users/nosinasujithjosephratnam/Documents/testing",
            "env_vars": {
                "PATH": "/usr/bin:/bin",
                "HOME": "/Users/nosinasujithjosephratnam"
            },
            "timestamp": "2025-05-20T17:55:08.035584",
            "file_access": [
                {
                    "file": "/Users/nosinasujithjosephratnam/.netrc",
                    "mode": "r",
                    "operation": "read"
                }
            ]
        }
        self.session_file = "session.json"
        with open(self.session_file, "w") as f:
            json.dump(self.session_data, f)

    def tearDown(self):
        export_file = os.path.splitext(self.session_file)[0] + "_replay.py"
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        if os.path.exists(export_file):
            os.remove(export_file)

    def test_export(self):
        runner = CliRunner()
        result = runner.invoke(export, [self.session_file])
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(os.path.exists(os.path.splitext(self.session_file)[0] + "_replay.py"))

    def test_export_script_contents(self):
        runner = CliRunner()
        runner.invoke(export, [self.session_file])
        with open(os.path.splitext(self.session_file)[0] + "_replay.py", "r") as f:
            script = f.read()
        
        # Test environment variables
        self.assertIn('os.environ["PATH"] = "/usr/bin:/bin"', script)
        self.assertIn('os.environ["HOME"] = "/Users/nosinasujithjosephratnam"', script)
        
        # Test working directory
        self.assertIn('os.chdir("/Users/nosinasujithjosephratnam/Documents/testing")', script)
        
        # Test HTTP requests
        self.assertIn('requests.get("https://example.com", headers={"User-Agent": "debugonce"})', script)
        
        # Test file access
        self.assertIn('"/Users/nosinasujithjosephratnam/.netrc"', script)
        self.assertIn('"r"', script)
        
        # Test function call
        self.assertIn('divide(4, 2)', script)

    def test_export_invalid_session_file(self):
        runner = CliRunner()
        result = runner.invoke(export, ["invalid_session_file.json"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error reading session file", result.output)

    def test_export_empty_session_file(self):
        with open(self.session_file, "w") as f:
            f.write("")
        runner = CliRunner()
        result = runner.invoke(export, [self.session_file])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error reading session file", result.output)

    def test_export_missing_function_name(self):
        del self.session_data["function"]
        with open(self.session_file, "w") as f:
            json.dump(self.session_data, f)
        runner = CliRunner()
        result = runner.invoke(export, [self.session_file])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("Error generating replay script", result.output)

if __name__ == "__main__":
    unittest.main()