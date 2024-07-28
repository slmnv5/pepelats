from http.server import BaseHTTPRequestHandler
from threading import Event

from utils.util_web import send_headers, UPDATE_PAGE_B, FAVICON_B, UPDATE_CODE_B


class WebHandler(BaseHTTPRequestHandler):
    has_updates: Event = Event()
    updates_b: bytes = b""
    waiting_clients: set = set()

    def _process_update(self) -> None:
        client = self.address_string()
        if client not in WebHandler.waiting_clients:
            WebHandler.waiting_clients.add(client)
            WebHandler.has_updates.wait()
            WebHandler.waiting_clients.remove(client)
        else:
            self.wfile.write(WebHandler.updates_b)  # if same client already waiting send past data

        if not WebHandler.waiting_clients:
            WebHandler.has_updates.clear()

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path == "/update":
            send_headers(self, 'application/json')
            client = self.address_string()
            if client not in WebHandler.waiting_clients:
                WebHandler.waiting_clients.add(client)
                WebHandler.has_updates.wait()
                WebHandler.waiting_clients.remove(client)

            self.wfile.write(WebHandler.updates_b)  # if same client already waiting send past data
            if not WebHandler.waiting_clients:
                WebHandler.has_updates.clear()
        elif self.path == "/update_page.js":
            send_headers(self, 'text/javascript')
            self.wfile.write(UPDATE_CODE_B)
        elif self.path == "/favicon.ico":
            send_headers(self, 'application/octet-stream')
            self.wfile.write(FAVICON_B)
        else:
            send_headers(self)
            self.wfile.write(UPDATE_PAGE_B)
