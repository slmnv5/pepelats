import json
from multiprocessing import Queue
from socket import socket, gethostbyname, getfqdn
from threading import Thread
from time import sleep

from mvc.menuclient import MenuClient
from utils.util_config import SOCK_PORT
from utils.util_log import MY_LOG
from utils.util_screen import get_screen_dict, get_default_dict

_GATEWAY_IP = gethostbyname(getfqdn())


class SocScreen(MenuClient):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        self.__dic: dict = get_screen_dict(get_default_dict())
        self._update_json: bytes = b""
        MY_LOG.warning(f"To control looper connect to:\nhttp://{_GATEWAY_IP}:{SOCK_PORT}")
        Thread(target=self.__updater, name="updater", daemon=True).start()

    def _client_stop(self) -> None:
        super()._client_stop()

    def _client_log(self, msg: str) -> None:
        self.__dic["description"] = msg

    def _client_redraw(self, dic: dict) -> None:
        self.__dic = get_screen_dict(dic)
        self._update_json = json.dumps(self.__dic)

    def __updater(self):
        s = socket()
        s.connect((_GATEWAY_IP, SOCK_PORT))
        MY_LOG.warning(f"Connect to {_GATEWAY_IP}:{SOCK_PORT}")
        while self._alive:
            sleep(self.__dic["sleep_tm"])
            s.send(self._update_json)
        s.close()
