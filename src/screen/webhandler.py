import json
from http.server import BaseHTTPRequestHandler

from utils.util_web import send_headers, FAVICON_B, UPDATE_CODE_B, UPDATE_PAGE


class WebHandler(BaseHTTPRequestHandler):
    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/update":
            send_headers(self, 'application/json')
            # noinspection PyUnresolvedReferences
            dic: dict = self.server.wait_update()
            self.wfile.write(json.dumps(dic).encode())
        elif self.path == "/update_page.js":
            send_headers(self, 'text/javascript')
            self.wfile.write(UPDATE_CODE_B)
        elif self.path == "/favicon.ico":
            send_headers(self, 'application/octet-stream')
            self.wfile.write(FAVICON_B)
        else:
            send_headers(self)
            dic: dict = self.server.nowait_update()
            s = UPDATE_PAGE.format(header=dic["header"], description=dic["description"], content=dic["content"])
            self.wfile.write(s.encode())
