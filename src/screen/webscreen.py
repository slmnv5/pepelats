from http.server import HTTPServer
from multiprocessing import Queue, Event
from time import time

from screen.menuclient import MenuClient
from screen.webhandler import WebHandler
from utils.util_config import LOCAL_IP, LOCAL_PORT
from utils.util_log import MY_LOG
from utils.util_screen import get_default_dict


class WebScreen(MenuClient, HTTPServer):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        # noinspection PyTypeChecker
        HTTPServer.__init__(self, ("", LOCAL_PORT), WebHandler)
        self.request_queue_size = 0  # 1 request at a time
        self.__dic: dict = dict()
        self._has_update: Event = Event()
        self._client_redraw(get_default_dict())
        MY_LOG.warning(f"To control looper connect to:\nhttp://{LOCAL_IP}:{LOCAL_PORT}")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            self.server_close()

    def _client_log(self, msg: str) -> None:
        self.__dic["description"] = msg
        self._has_update.set()

    def service_actions(self):
        if not self._alive:
            raise KeyboardInterrupt("stopped")

    def _client_redraw(self, dic: dict) -> None:
        self.__dic = dic
        self.__dic["update_tm"] = time()
        self._has_update.set()

    def get_update(self) -> dict[str, str | float]:
        self._has_update.wait()
        self._has_update.clear()
        return self.__dic


if __name__ == "__main__":
    scr = WebScreen(Queue(), )
    scr.client_start()
