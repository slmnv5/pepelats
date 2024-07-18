from http.server import BaseHTTPRequestHandler
from typing import Callable

from utils.utilweb import UPDATE_PAGE


class WebHandler(BaseHTTPRequestHandler):
    get_updates: Callable[[], str] = None

    def _send_redirect(self) -> None:
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/')  # This will navigate to the original page
        self.end_headers()

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(UPDATE_PAGE)
        elif self.path == "/update":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            json_str = self.get_updates()
            self.wfile.write(json_str.encode())
        else:
            pass
