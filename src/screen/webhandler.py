import json
from http.server import BaseHTTPRequestHandler
from threading import Event
from typing import Callable

from utils.util_web import send_headers, FAVICON_B, UPDATE_CODE_B, UPDATE_PAGE_B


class WebHandler(BaseHTTPRequestHandler):
    def __init__(self, get_event: Callable[[], Event], get_update: Callable[[], bytes], *args, **kwargs):
        self._get_event: Callable[[], Event] = get_event
        self._get_update: Callable[[], bytes] = get_update
        self._WAIT_SEC = 5
        self._empty_update: bytes = json.dumps(dict()).encode()
        # BaseHTTPRequestHandler calls do_GET inside __init__
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/update":
            if self._get_event().wait(self._WAIT_SEC):
                send_headers(self, 'application/json')
                self.wfile.write(self._get_update())
                print(11111111)
            else:
                print(99999999999999999)
                send_headers(self, 'application/json, 400')
                self.wfile.write(self._empty_update)
        elif self.path == "/update_page.js":
            send_headers(self, 'text/javascript')
            self.wfile.write(UPDATE_CODE_B)
        elif self.path == "/favicon.ico":
            send_headers(self, 'application/octet-stream')
            self.wfile.write(FAVICON_B)
        else:
            send_headers(self)
            self.wfile.write(UPDATE_PAGE_B)
