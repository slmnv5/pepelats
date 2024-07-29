import json
from http.server import BaseHTTPRequestHandler
from threading import Event

from utils.util_web import send_headers, FAVICON_B, UPDATE_CODE_B, UPDATE_PAGE


class WebHandler(BaseHTTPRequestHandler):
    def __init__(self, update_b: bytes, *args, **kwargs):
        self.update_b = update_b
        # BaseHTTPRequestHandler calls do_GET inside __init__
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/update":
            send_headers(self, 'application/json')
            self.wfile.write(self.update_b)
        elif self.path == "/update_page.js":
            send_headers(self, 'text/javascript')
            self.wfile.write(UPDATE_CODE_B)
        elif self.path == "/favicon.ico":
            send_headers(self, 'application/octet-stream')
            self.wfile.write(FAVICON_B)
        else:
            send_headers(self)
            self.wfile.write(UPDATE_PAGE.encode())
