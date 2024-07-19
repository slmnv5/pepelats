from http.server import BaseHTTPRequestHandler
from typing import Callable

from utils.utillog import MyLog
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
        MyLog().info(f"path:{self.path}\nheaders:{self.headers}")
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
        elif self.path == "/update_page.js":
            self.send_response(200)
            self.send_header('Content-type', 'text/javascript')
            self.end_headers()
            with open("./html/update_page.js", 'r') as f:
                self.wfile.write(f.read().encode())
        elif self.path == "/favicon.ico":
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()
            with open("./favicon.ico", 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_error(400, "Not found", f"Not found: {self.path}")
