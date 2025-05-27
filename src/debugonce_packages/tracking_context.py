import builtins
from requests import sessions
import unittest.mock
from datetime import datetime
import requests

class TrackingContext:
    def __init__(self):
        self.file_access_log = []
        self.http_request_log = []

    def __enter__(self):
        self._original_open = builtins.open
        self._original_request = sessions.Session.request

        def open_wrapper(file, mode='r', *a, **k):
            if any(m in mode for m in ['w', 'a', 'x']):
                operation = 'write'
            elif 'r' in mode:
                operation = 'read'
            else:
                operation = 'other'
            self.file_access_log.append({
                "file": file,
                "mode": mode,
                "operation": operation,
                "timestamp": datetime.now().isoformat()
            })
            return self._original_open(file, mode, *a, **k)
        self._open_patch = unittest.mock.patch('builtins.open', new=open_wrapper)
        self._open_patch.start()

        def normalize_url(method, url):
            try:
                return requests.Request(method, url).prepare().url
            except Exception:
                return url

        def request_wrapper(this, method, url, *a, **k):
            response = self._original_request(this, method, url, *a, **k)
            self.http_request_log.append({
                "method": method,
                "url": normalize_url(method, url),
                "status_code": getattr(response, 'status_code', None),
                "timestamp": datetime.now().isoformat()
            })
            return response
        self._request_patch = unittest.mock.patch.object(sessions.Session, 'request', new=request_wrapper)
        self._request_patch.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._open_patch.stop()
        self._request_patch.stop()
