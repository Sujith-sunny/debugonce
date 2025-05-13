import os
import json
import pytest
from debugonce_packages.utils import save_capture, load_capture

def test_save_capture_creates_file(tmp_path):
    capture_data = {
        "args": [1, 2, 3],
        "env": os.environ.copy(),
        "cwd": os.getcwd(),
        "python_version": "3.8.10"
    }
    file_path = tmp_path / ".debugonce" / "capture.json"
    save_capture(capture_data, file_path)

    assert file_path.exists()
    with open(file_path) as f:
        saved_data = json.load(f)
    assert saved_data == capture_data

def test_load_capture_returns_data(tmp_path):
    capture_data = {
        "args": [1, 2, 3],
        "env": os.environ.copy(),
        "cwd": os.getcwd(),
        "python_version": "3.8.10"
    }
    file_path = tmp_path / ".debugonce" / "capture.json"
    os.makedirs(file_path.parent, exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(capture_data, f)

    loaded_data = load_capture(file_path)
    assert loaded_data == capture_data

def test_load_capture_raises_file_not_found(tmp_path):
    file_path = tmp_path / ".debugonce" / "non_existent.json"
    with pytest.raises(FileNotFoundError):
        load_capture(file_path)