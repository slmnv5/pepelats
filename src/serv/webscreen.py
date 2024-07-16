from http.server import HTTPServer
from multiprocessing import Queue, Event
from threading import Thread

from mvc.drawinfo import DrawInfo
from mvc.menuclient import MenuClient
from serv.webhandler import WebHandler
from utils.utilconfig import IP_ADDR


class WebScreen(MenuClient, HTTPServer):
    def __init__(self, q: Queue):
        MenuClient.__init__(self, q)
        # noinspection PyTypeChecker
        HTTPServer.__init__(self, ('', 8000), WebHandler)
        self.handler_class: type = WebHandler
        WebHandler.get_updates = self.get_updates
        self._has_updates: Event = Event()
        print(f"To control looper connect to:\nhttp://{IP_ADDR}:8000")
        Thread(target=self.serve_forever(), name="updater", daemon=True).start()

    def _client_stop(self) -> None:
        super()._client_stop()
        self.shutdown()

    def _client_redraw(self, di: DrawInfo) -> None:
        super()._client_redraw(di)
        self._has_updates.set()

    def get_updates(self) -> DrawInfo:
        self._has_updates.wait()
        self._has_updates.clear()
        return self._di


if __name__ == "__main__":
    WebScreen(Queue())
