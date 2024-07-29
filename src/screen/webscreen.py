import json
from functools import partial
from http.server import HTTPServer
from multiprocessing import Queue
from threading import Thread, Event
from time import time

from screen.menuclient import MenuClient
from screen.webhandler import WebHandler
from utils.util_config import LOCAL_IP, LOCAL_PORT
from utils.util_log import MY_LOG
from utils.util_name import AppName
from utils.util_screen import get_default_dict, recalc_dic


class WebScreen(MenuClient):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        self._update_event: Event = Event()
        self._update_b: bytes = b""
        self._client_redraw(get_default_dict())
        handler_class = partial(WebHandler, self._get_event, self._get_update)
        self._serv = HTTPServer(("", LOCAL_PORT), handler_class)
        Thread(target=self.__update, name="update", daemon=True).start()
        MY_LOG.warning(f"To control looper connect to:\nhttp://{LOCAL_IP}:{LOCAL_PORT}")

    def __update(self) -> None:
        self._serv.serve_forever()

    def _client_stop(self) -> None:
        super()._client_stop()
        self._serv.shutdown()

    def _client_log(self, msg: str) -> None:
        dic = get_default_dict()
        dic[AppName.description] = msg
        self._client_redraw(dic)

    def _client_redraw(self, dic: dict) -> None:
        recalc_dic(dic)
        dic["update_tm"] = time()
        print(111111111111, dic)
        self._update_b = json.dumps(dic).encode()
        self._update_event.set()
        self._update_event.clear()

    def _get_update(self) -> bytes:
        return self._update_b

    def _get_event(self) -> Event:
        return self._update_event


if __name__ == "__main__":
    scr = WebScreen(Queue())
    scr.client_start()
