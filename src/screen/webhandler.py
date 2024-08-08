from threading import Event
from typing import Callable

from screen.confighandler import ConfigHandler
from utils.util_web import UPDATE_PATH


class UpdateState:
    def __init__(self):
        self.id: int = 0
        self.bytes: bytes = b""
        self.ready: Event = Event()
        self.ready.clear()


class WebHandler(ConfigHandler):
    def __init__(self, get_state: Callable, *args, **kwargs):
        self._get_state: Callable = get_state
        self._MAX_WAIT_SEC = 10
        # BaseHTTPRequestHandler calls do_GET inside __init__
        # So we have to call super().__init__ after setting attributes.
        super().__init__(*args, **kwargs)

    # noinspection PyPep8Naming
    def do_GET(self):
        unknown_path: str = super()._process_get()
        if unknown_path:
            unknown_path = self._process_get()
        assert not unknown_path

    def _process_get(self) -> str | None:
        if self.path.startswith(UPDATE_PATH):
            state: UpdateState = self._get_state()
            hdr_dic: dict = {'Content-type': 'application/json', 'update_id': str(state.id)}
            request_id: int = int(self.path[len(UPDATE_PATH):])
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
        else:
            pass
        return None


if __name__ == "__main__":
    pass
