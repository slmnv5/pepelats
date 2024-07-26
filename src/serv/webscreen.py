import json
from http.server import HTTPServer
from multiprocessing import Queue, Event
from threading import Thread
from time import sleep

from mvc.menuclient import MenuClient
from serv.webhandler import WebHandler
from utils.util_config import LOCAL_IP, LOCAL_PORT
from utils.util_log import MY_LOG
from utils.util_screen import get_screen_dict, get_default_dict


class WebScreen(MenuClient):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        self.__dic: dict = get_screen_dict(get_default_dict())
        WebHandler.get_updates = self.get_updates
        # noinspection PyTypeChecker
        self._server = HTTPServer(("", LOCAL_PORT), WebHandler)
        self._has_updates: Event = Event()
        self._updates_b: bytes = b" "
        MY_LOG.warning(f"To control looper connect to:\nhttp://{LOCAL_IP}:{LOCAL_PORT}")
        Thread(target=self.__update(), name="update", daemon=True).start()

    def __update(self) -> None:
        try:
            self._server.serve_forever()
        except KeyboardInterrupt:
            self._server.server_close()

    def _client_log(self, msg: str) -> None:
        self.__dic["description"] = msg
        self._updates_b = json.dumps(self.__dic).encode()
        self._has_updates.set()

    def _client_stop(self) -> None:
        self._updates_b = b"stop"
        self._has_updates.set()
        sleep(2)
        super()._client_stop()

    def _client_redraw(self, dic: dict) -> None:
        self.__dic = get_screen_dict(dic)
        self._updates_b = json.dumps(self.__dic).encode()
        self._has_updates.set()

    def get_updates(self) -> bytes:
        self._has_updates.wait()
        self._has_updates.clear()
        return self._updates_b


if __name__ == "__main__":
    scr = WebScreen(Queue())
    scr.client_start()
