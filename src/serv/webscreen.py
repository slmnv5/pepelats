from http.server import HTTPServer
from multiprocessing import Queue, Event
from threading import Thread

from mvc.drawinfo import DrawInfo
from mvc.menuclient import MenuClient
from serv.webhandler import WebHandler
from utils.utilconfig import IP_ADDR


class WebScreen(MenuClient, HTTPServer):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        # noinspection PyTypeChecker
        HTTPServer.__init__(self, ('', 8000), WebHandler)
        WebHandler.get_updates = self.get_updates
        self._has_updates: Event = Event()
        self._update_json: str = ''
        print(f"To control looper connect to:\nhttp://{IP_ADDR}:8000")
        Thread(target=self.serve_forever, name="updater", daemon=True).start()

    def _client_stop(self) -> None:
        super()._client_stop()
        self.shutdown()

    def _client_redraw(self, di: DrawInfo) -> None:
        self._update_json = di.to_json()
        self._has_updates.set()

    def get_updates(self) -> str:
        self._has_updates.wait()
        self._has_updates.clear()
        return self._update_json


if __name__ == "__main__":
    pass
