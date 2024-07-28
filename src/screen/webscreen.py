import json
from http.server import HTTPServer
from multiprocessing import Queue
from threading import Thread

from screen.menuclient import MenuClient
from screen.webhandler import WebHandler
from utils.util_config import LOCAL_IP, LOCAL_PORT
from utils.util_log import MY_LOG
from utils.util_screen import get_screen_dict, get_default_dict


class WebScreen(MenuClient, HTTPServer):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        # noinspection PyTypeChecker
        HTTPServer.__init__(self, ("", LOCAL_PORT), WebHandler, )
        self.__dic: dict = get_screen_dict(get_default_dict())
        Thread(target=self.__update, name="update", daemon=True).start()

    def __update(self) -> None:
        MY_LOG.warning(f"To control looper connect to:\nhttp://{LOCAL_IP}:{LOCAL_PORT}")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            self.server_close()

    def _client_log(self, msg: str) -> None:
        self.__dic["description"] = msg
        WebHandler.updates_b = json.dumps(self.__dic).encode()
        WebHandler.has_updates.set()

    def service_actions(self):
        if not self._alive:
            raise KeyboardInterrupt("stopped")

    def _client_redraw(self, dic: dict) -> None:
        self.__dic = get_screen_dict(dic)
        WebHandler.updates_b = json.dumps(self.__dic).encode()
        WebHandler.has_updates.set()


if __name__ == "__main__":
    scr = WebScreen(Queue(), )
    scr.client_start()
