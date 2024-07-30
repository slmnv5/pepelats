from http.server import BaseHTTPRequestHandler
from threading import Event
from typing import Callable

from utils.util_config import get_params
from utils.util_web import FAVICON_B, UPDATE_CODE_B, UPDATE_PAGE_B


class UpdateState:
    def __init__(self):
        self.id: int = 0
        self.bytes: bytes = b""
        self.ready: Event = Event()
        self.ready.clear()


class WebHandler(BaseHTTPRequestHandler):
    def __init__(self, get_state: Callable, *args, **kwargs):
        self._get_state: Callable = get_state
        self._MAX_WAIT_SEC = 5
        # BaseHTTPRequestHandler calls do_GET inside __init__
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    def send_hdr(self, status: int = 200, **kwargs) -> None:
        default_dic: dict = {'Content-type': 'text/html'}
        default_dic.update(kwargs)
        print(11111111111, "default_dic", default_dic)
        self.send_response(status)
        for k, v in default_dic.items():
            self.send_header(k, v)
        self.end_headers()

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path.startswith("/update"):
            state: UpdateState = self._get_state()
            # hdr_dic: dict = {'Content-type': 'application/json', 'update_id': state.id}
            request_id: int = get_params(self.path).get("update_id", 0)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('update_id', '111')
            self.end_headers()
            print(88888888888, state.bytes.decode(), request_id)
            if request_id < state.id:  # client asking old version, send latest
                self.wfile.write(state.bytes)
            else:
                if state.ready.wait(timeout=self._MAX_WAIT_SEC):  # client asking new version, wait for it
                    self.wfile.write(state.bytes)
                    print(11111111)
                else:  # too long waiting, send nothing
                    print(99999999999999999)
                    self.wfile.write(b"")
        elif self.path == "/update_page.js":
            self.send_hdr(**{'Content-type': 'text/javascript'})
            self.wfile.write(UPDATE_CODE_B)
        elif self.path == "/favicon.ico":
            self.send_hdr(**{'Content-type': 'application/octet-stream'})
            self.wfile.write(FAVICON_B)
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('update_id', '111')
            self.end_headers()
            self.wfile.write(UPDATE_PAGE_B)
