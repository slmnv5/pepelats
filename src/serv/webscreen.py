from http.server import HTTPServer
from multiprocessing import Queue, Event
from threading import Thread

from mvc.drawinfo import DrawInfo
from mvc.menuclient import MenuClient
from serv.webhandler import WebHandler
from utils.utilconfig import IP_ADDR


_END_ALL: str = '</span>'
_REV_CLR: str = '<span id="rev_span" style="red"'
_RED_CLR: str = '<span id="red_span" style="color: red;">'
_YEL_CLR: str = f"\x1b[1;{_YELLOW}m"
_GRN_CLR: str = f"\x1b[1;{_GREEN}m"
_BLU_CLR: str = f"\x1b[1;{_BLUE}m"


class WebScreen(MenuClient, HTTPServer):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        # noinspection PyTypeChecker
        HTTPServer.__init__(self, ('', 8000), WebHandler)
        WebHandler.get_updates = self.get_updates
        self._has_updates: Event = Event()
        print(f"To control looper connect to:\nhttp://{IP_ADDR}:8000")
        Thread(target=self.serve_forever, name="updater", daemon=True).start()

    def _client_stop(self) -> None:
        super()._client_stop()
        self.shutdown()

    def __add_color(self, line: str) -> str:
        if line[0] == "*":
            if self._di.is_rec:
                return _RED_CLR + line + _END_ALL
            else:
                return _GRN_CLR + line + _END_ALL
        elif line[0] == "~":
            return _YEL_CLR + line + _END_ALL
        else:
            return line

    def _client_redraw(self, di: DrawInfo) -> None:
        self._di = di

        self._has_updates.set()

    def get_updates(self) -> DrawInfo:
        self._has_updates.wait()
        self._has_updates.clear()
        return self._di


if __name__ == "__main__":
    pass
