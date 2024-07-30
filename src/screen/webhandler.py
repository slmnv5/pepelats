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
        self._MAX_WAIT_SEC = 10
        # BaseHTTPRequestHandler calls do_GET inside __init__
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    def send_hdr(self, status: int = 200, arg_dic=None) -> None:
        d: dict[str, any] = {'Content-type': 'text/html'}
        if arg_dic is not None:
            d.update(arg_dic)
        self.send_response(status)
        for k, v in d.items():
            assert isinstance(k, str) and isinstance(v, str), f"must be strings: k={k}, v={v}"
            self.send_header(k, v)
        self.end_headers()

    # noinspection PyPep8Naming
    def do_GET(self):
        if self.path.startswith("/update?"):
            state: UpdateState = self._get_state()
            hdr_dic: dict = {'Content-type': 'application/json', 'update_id': str(state.id)}
            request_id: int = get_params(self.path).get("update_id", 0)

            if request_id < state.id:  # client asking old version, send latest
                self.send_hdr(arg_dic=hdr_dic)
                self.wfile.write(state.bytes)
            else:
                if state.ready.wait(timeout=self._MAX_WAIT_SEC):  # client asking new version, wait for it
                    self.send_hdr(arg_dic=hdr_dic)
                    self.wfile.write(state.bytes)
                else:  # too long waiting, send nothing
                    self.send_hdr(304, arg_dic=hdr_dic)
                    self.wfile.write(b'""')
        elif self.path == "/update_page.js":
            self.send_hdr(arg_dic={'Content-type': 'text/javascript'})
            self.wfile.write(UPDATE_CODE_B)
        elif self.path == "/favicon.ico":
            self.send_hdr(arg_dic={'Content-type': 'application/octet-stream'})
            self.wfile.write(FAVICON_B)
        else:
            self.send_hdr()
            self.wfile.write(UPDATE_PAGE_B)
