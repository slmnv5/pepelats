from http.server import BaseHTTPRequestHandler
from typing import Callable

from utils.util_web import send_headers, UPDATE_PAGE_B, FAVICON_B, UPDATE_CODE_B


class WebHandler(BaseHTTPRequestHandler):
    get_updates: Callable[[], bytes] = None

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/update":
            send_headers(self, 'application/json')
            updates: bytes = self.get_updates()
            if updates == b"stop":
                raise KeyboardInterrupt("Stopped web server")
            self.wfile.write(updates)
        elif self.path == "/update_page.js":
            send_headers(self, 'text/javascript')
            self.wfile.write(UPDATE_CODE_B)
        elif self.path == "/favicon.ico":
            send_headers(self, 'application/octet-stream')
            self.wfile.write(FAVICON_B)
        else:
            send_headers(self)
            self.wfile.write(UPDATE_PAGE_B)
