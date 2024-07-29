from http.server import BaseHTTPRequestHandler

from utils.util_web import send_headers, FAVICON_B, UPDATE_CODE_B, UPDATE_PAGE


class WebHandler(BaseHTTPRequestHandler):
    def __init__(self, update_b: bytes, *args, **kwargs):
        self._update_b = update_b
        print(11111111111, self._update_b)
        # BaseHTTPRequestHandler calls do_GET inside __init__
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    # noinspection PyPep8Naming
    def do_GET(self):
        if not self._update_b:
            self.send_error(500, "server stopped")
            raise KeyboardInterrupt("server stopped")
        elif self.path == "/update":
            send_headers(self, 'application/json')
            self.wfile.write(self._update_b)
        elif self.path == "/update_page.js":
            send_headers(self, 'text/javascript')
            self.wfile.write(UPDATE_CODE_B)
        elif self.path == "/favicon.ico":
            send_headers(self, 'application/octet-stream')
            self.wfile.write(FAVICON_B)
        else:
            send_headers(self)
            self.wfile.write(UPDATE_PAGE.encode())
