import json
from http.server import HTTPServer
from multiprocessing import Queue, Event
from threading import Thread

from mvc.menuclient import MenuClient
from serv.webhandler import WebHandler
from utils.util_config import IP_ADDR
from utils.util_log import MY_LOG
from utils.util_screen import get_screen_dict, get_default_dict


class WebScreen(MenuClient, HTTPServer):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        self.__dic: dict = get_screen_dict(get_default_dict())
        # noinspection PyTypeChecker
        HTTPServer.__init__(self, ('', 8000), WebHandler)
        WebHandler.get_updates = self.get_updates
        self._has_updates: Event = Event()
        self._update_json: str = ''
        MY_LOG.warning(f"To control looper connect to:\nhttp://{IP_ADDR}:8000")
        Thread(target=self.serve_forever, name="updater", daemon=True).start()

    def _client_log(self, msg: str) -> None:
        self.__dic["description"] = msg
        self._update_json = json.dumps(self.__dic)
        self._has_updates.set()

    def _client_stop(self) -> None:
        super()._client_stop()
        self.shutdown()

    def _client_redraw(self, dic: dict) -> None:
        self.__dic = get_screen_dict(dic)
        self._update_json = json.dumps(self.__dic)
        self._has_updates.set()

    def get_updates(self) -> str:
        self._has_updates.wait()
        self._has_updates.clear()
        return self._update_json


if __name__ == "__main__":
    scr = WebScreen(Queue())
    scr.client_start()
