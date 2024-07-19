from http.server import BaseHTTPRequestHandler
from typing import Callable

from utils.utillog import MyLog
from utils.utilweb import send_headers, load_file


class WebHandler(BaseHTTPRequestHandler):
    get_updates: Callable[[], str] = None

    def _send_redirect(self) -> None:
        self.send_response(303)
        self.send_header('Content-type', 'text/html')
        self.send_header('Location', '/')  # This will navigate to the original page
        self.end_headers()

    # noinspection PyPep8Naming
    def do_GET(self):
        MyLog().info(f"path:{self.path}\nheaders:{self.headers}")
        if self.path == "/":
            send_headers(self)
            self.wfile.write(load_file("html/update_page.html").encode())
        elif self.path == "/update":
            send_headers(self, 'application/json')
            json_str = self.get_updates()
            self.wfile.write(json_str.encode())
        elif self.path == "/update_page.js":
            send_headers(self, 'text/javascript')
            self.wfile.write(load_file("html/update_page.js").encode())
        elif self.path == "/favicon.ico":
            send_headers(self, 'application/octet-stream')
            self.wfile.write(load_file('favicon.ico').encode())
        else:
            self.send_error(400, "Not found", f"Not found: {self.path}")
