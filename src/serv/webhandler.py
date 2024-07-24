from http.server import BaseHTTPRequestHandler
from typing import Callable

from utils.util_log import MY_LOG
from utils.util_web import send_headers, load_file, send_redirect, load_bin_file


class WebHandler(BaseHTTPRequestHandler):
    get_updates: Callable[[], str] = None

    # noinspection PyPep8Naming
    def do_GET(self):
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
            self.wfile.write(load_bin_file('favicon.ico'))
        else:
            send_redirect(self)

    def log_message(self, msg, *args) -> None:
        pass

    def log_error(self, msg: str, *args) -> None:
        MY_LOG.error(msg % args)
