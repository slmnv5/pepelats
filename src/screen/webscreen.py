import json
from functools import partial
from http.server import HTTPServer
from multiprocessing import Queue
from time import time

from screen.menuclient import MenuClient
from screen.webhandler import WebHandler
from utils.util_config import LOCAL_IP, LOCAL_PORT
from utils.util_log import MY_LOG
from utils.util_screen import get_default_dict


class WebScreen(MenuClient, HTTPServer):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        self.__dic: dict = dict()
        self._updates_b: bytes = b""
        handler_class = partial(WebHandler, self._updates_b)
        HTTPServer.__init__(self, ("", LOCAL_PORT), handler_class)
        self._client_redraw(get_default_dict())
        MY_LOG.warning(f"To control looper connect to:\nhttp://{LOCAL_IP}:{LOCAL_PORT}")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            self.server_close()

    def _client_log(self, msg: str) -> None:
        self.__dic["description"] = msg
        self._updates_b = json.dumps(self.__dic).encode()

    def service_actions(self):
        if not self._alive:
            raise KeyboardInterrupt("stopped")

    def _client_redraw(self, dic: dict) -> None:
        self.__dic = dic
        self.__dic["update_tm"] = time()
        self._updates_b = json.dumps(self.__dic).encode()


if __name__ == "__main__":
    scr = WebScreen(Queue())
    scr.client_start()
