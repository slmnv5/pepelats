from http.server import BaseHTTPRequestHandler
from threading import Event

from utils.util_config import get_params
from utils.util_web import FAVICON_B, UPDATE_CODE_B, UPDATE_PAGE_B


class UpdateState:
    def __init__(self):
        self.id: int = 0
        self.bytes: bytes = b""
        self.ready: Event = Event()
        self.ready.clear()


class WebHandler(BaseHTTPRequestHandler):
    def __init__(self, state: UpdateState, *args, **kwargs):
        self._state: UpdateState = state
        self._MAX_WAIT_SEC = 5
        # BaseHTTPRequestHandler calls do_GET inside __init__
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    def send_hdr(self, status: int = 200, **kwargs) -> None:
        dic: dict = {'Content-type': 'text/html'}
        dic.update(kwargs)
        self.send_response(status)
        for k, v in dic.items():
            self.send_header(k, v)
        self.end_headers()

    # noinspection PyPep8Naming
    def do_GET(self):
        self.parse_request()
        if self.path.startswith("/update"):
            hdr_dic: dict = {'Content-type': 'application/json', 'update_id': self._state.id}
            dic = get_params(self.path)
            request_id = dic["id"]
            print(88888888888, id, self._state.bytes.decode())
            if request_id < self._state.id:
                self.send_hdr(**hdr_dic)
                self.wfile.write(self._state.bytes)
            else:
                if self._state.ready.wait(self._MAX_WAIT_SEC):
                    self.send_hdr(**hdr_dic)
                    self.wfile.write(self._state.bytes)
                    print(11111111)
                else:
                    print(99999999999999999)
                    self.send_hdr(400, **hdr_dic)
                    self.wfile.write(b"")
        elif self.path == "/update_page.js":
            self.send_hdr(**{'Content-type': 'text/javascript'})
            self.wfile.write(UPDATE_CODE_B)
        elif self.path == "/favicon.ico":
            self.send_hdr(**{'Content-type': 'application/octet-stream'})
            self.wfile.write(FAVICON_B)
        else:
            self.send_hdr()
            self.wfile.write(UPDATE_PAGE_B)
