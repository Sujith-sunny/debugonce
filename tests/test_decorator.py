import unittest
from debugonce_packages.decorator import debugonce
import json
import os, io
import requests
from requests import sessions
import unittest.mock

class TestDebugOnceDecorator(unittest.TestCase):
    def setUp(self):
        """Set up the test environment."""
        # Create the .debugonce directory if it doesn't exist
        self.debugonce_dir = ".debugonce"
        os.makedirs(self.debugonce_dir, exist_ok=True)

    def tearDown(self):
        """Clean up the test environment."""
        # Remove all files in the .debugonce directory
        if os.path.exists(self.debugonce_dir):
            for file in os.listdir(self.debugonce_dir):
                os.remove(os.path.join(self.debugonce_dir, file))
            os.rmdir(self.debugonce_dir)

    def test_capture_state(self):
        """Test capturing state with no exception."""
        @debugonce
        def add(a, b):
            return a + b

        result = add(2, 3)
        self.assertEqual(result, 5)

        # Check if the state is saved to a file
        session_files = os.listdir(self.debugonce_dir)
        self.assertTrue(len(session_files) > 0)

        # Load the state from the file
        with open(os.path.join(self.debugonce_dir, session_files[0]), "r") as f:
            state = json.load(f)

        # Check if the state is correct
        self.assertEqual(state["function"], "add")
        self.assertEqual(state["args"], [2, 3])  # Expect a list instead of a tuple
        self.assertEqual(state["kwargs"], {})
        self.assertEqual(state["result"], 5)
        self.assertIsNone(state["exception"])

    def test_capture_state_with_exception(self):
        """Test capturing state with an exception."""
        @debugonce
        def divide(a, b):
            return a / b

        with self.assertRaises(ZeroDivisionError):
            divide(2, 0)

        # Check if the state is saved to a file
        session_files = os.listdir(self.debugonce_dir)
        self.assertTrue(len(session_files) > 0)

        # Load the state from the file
        with open(os.path.join(self.debugonce_dir, session_files[0]), "r") as f:
            state = json.load(f)

        # Check if the state is correct
        self.assertEqual(state["function"], "divide")
        self.assertEqual(state["args"], [2, 0])  # Expect a list instead of a tuple
        self.assertEqual(state["kwargs"], {})
        self.assertIsNone(state["result"])
        self.assertIsNotNone(state["exception"])

    def test_file_access_tracking(self):
        """Test file access tracking."""
        @debugonce
        def file_operations():
            with open("test_file.txt", "w") as f:
                f.write("Hello, DebugOnce!")
            with open("test_file.txt", "r") as f:
                content = f.read()
            os.remove("test_file.txt")
            return content

        result = file_operations()
        self.assertEqual(result, "Hello, DebugOnce!")

        # Check if the state is saved to a file
        session_files = os.listdir(self.debugonce_dir)
        self.assertTrue(len(session_files) > 0)

        # Load the state from the file
        with open(os.path.join(self.debugonce_dir, session_files[0]), "r") as f:
            state = json.load(f)

        # Verify file access tracking
        file_access = state.get("file_access", [])
        self.assertEqual(len(file_access), 2)  # Expect exactly 2 operations: write and read
        self.assertEqual(file_access[0]["operation"], "write")
        self.assertEqual(file_access[1]["operation"], "read")
        self.assertTrue("test_file.txt" in file_access[0]["file"])
        self.assertTrue("test_file.txt" in file_access[1]["file"])
    


    #@unittest.mock.patch("requests.sessions.Session.request")
    def test_http_request_tracking(self):
        """Test HTTP request tracking."""
        # Create a mock for the request method
        with unittest.mock.patch.object(sessions.Session, 'request') as mock_request:
            # Configure the mock to return a successful response
            mock_request.return_value = requests.Response()
            mock_request.return_value.status_code = 200
            mock_request.return_value.headers = {'Content-Type': 'application/json'}

            # Create a mock raw attribute
            mock_request.return_value.raw = io.BytesIO(b'{"message": "Success!"}')

            #Create Prepared Request to avoid attribute error, mock the request attribute of the mock response
            prepared_request = requests.Request('GET', 'https://www.example.com').prepare()
            mock_request.return_value.request = prepared_request

            @debugonce
            def make_request():
                response = requests.get("https://www.example.com")
                return response.status_code

            result = make_request()
            self.assertEqual(result, 200)

            # Check if the state is saved to a file
            session_files = os.listdir(self.debugonce_dir)
            self.assertTrue(len(session_files) > 0)

            # Load the state from the file
            with open(os.path.join(self.debugonce_dir, session_files[0]), "r") as f:
                state = json.load(f)

            # Verify HTTP request tracking
            http_requests = state.get("http_requests", [])
            self.assertEqual(len(http_requests), 1)
            self.assertEqual(http_requests[0]["url"], "https://www.example.com/")
            self.assertEqual(http_requests[0]["method"], "GET")
            self.assertEqual(http_requests[0]["status_code"], 200)