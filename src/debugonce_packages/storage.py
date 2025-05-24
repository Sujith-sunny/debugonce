import os
import json

class StorageManager:
    """Manages storage for captured sessions."""

    def __init__(self, storage_dir=".debugonce"):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def save_session(self, session_name, data):
        """Save session data to a file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{session_name}.json")
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            return file_path
        except Exception as e:
            raise IOError(f"Failed to save session: {e}")

    def load_session(self, session_name):
        """Load session data from a file."""
        try:
            file_path = os.path.join(self.storage_dir, f"{session_name}.json")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Session file '{file_path}' not found.")
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception as e:
            raise IOError(f"Failed to load session: {e}")

    def list_sessions(self):
        """List all saved sessions."""
        try:
            return [
                f for f in os.listdir(self.storage_dir)
                if f.endswith(".json")
            ]
        except Exception as e:
            raise IOError(f"Failed to list sessions: {e}")

    def clean_sessions(self):
        """Delete all saved sessions."""
        try:
            for file in self.list_sessions():
                os.remove(os.path.join(self.storage_dir, file))
        except Exception as e:
            raise IOError(f"Failed to clean sessions: {e}")