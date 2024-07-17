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

    def _send_update(self) -> None:
        self.send_response(200)
        self.send_header('Content-type', "application/json")
        self.end_headers()
        self.wfile.write(WebHandler.get_updates().encode())

    def _send_page(self, page: bytes) -> None:
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(page)

    # noinspection PyPep8Naming
    def do_GET(self):
        print(self.path, 1111111111111111, self.headers)
        if self.path == "/":
            self._send_page(UPDATE_PAGE)
        else:
            self._send_redirect()
