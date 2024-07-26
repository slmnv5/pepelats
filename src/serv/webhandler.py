from http.server import BaseHTTPRequestHandler

from utils.util_web import send_headers, UPDATE_PAGE_B, FAVICON_B, UPDATE_CODE_B


class WebHandler(BaseHTTPRequestHandler):
    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/update":
            send_headers(self, 'application/json')
            # noinspection PyUnresolvedReferences
            updates: bytes = self.server.get_updates()
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
