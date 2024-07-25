import json
from multiprocessing import Queue
from socket import socket
from threading import Thread
from time import sleep

from mvc.menuclient import MenuClient
from utils.util_config import SOCK_PORT, GATEWAY_IP
from utils.util_log import MY_LOG, ConfigError
from utils.util_name import AppName
from utils.util_screen import get_screen_dict, get_default_dict


class SocScreen(MenuClient):
    def __init__(self, queue: Queue):
        MenuClient.__init__(self, queue)
        self.__dic: dict = get_screen_dict(get_default_dict())
        self._update_json: bytes = b""
        self._soc = socket()
        addr_str = f"{GATEWAY_IP}:{SOCK_PORT}"
        try:
            self._soc.connect((GATEWAY_IP, SOCK_PORT))
        except Exception as ex:
            MY_LOG.error(ex)
            raise ConfigError(f"Can not connect to: {addr_str}. "
                              f"Change config {AppName.screen_type} to use terminal")

        MY_LOG.warning(f"To control looper connect to:\nhttp://{GATEWAY_IP}:{SOCK_PORT}")
        Thread(target=self.__updater, name="updater", daemon=True).start()

    def _client_stop(self) -> None:
        super()._client_stop()

    def _client_log(self, msg: str) -> None:
        self.__dic["description"] = msg

    def _client_redraw(self, dic: dict) -> None:
        self.__dic = get_screen_dict(dic)
        self._update_json = json.dumps(self.__dic)

    def __updater(self):
        while self._alive:
            sleep(self.__dic["sleep_tm"])
            self._soc.send(self._update_json)
        self._soc.close()
