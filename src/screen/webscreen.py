import json
from functools import partial
from http.server import HTTPServer
from multiprocessing import Queue
from threading import Thread

from screen.basescreen import BaseScreen
from menu.menuclient import MenuClient
from screen.webhandler import WebHandler, UpdateState
from utils.util_config import LOCAL_IP, LOCAL_PORT
from utils.util_log import MY_LOG
from utils.util_name import AppName


class WebScreen(BaseScreen, MenuClient):
    def __init__(self, queue: Queue):
        BaseScreen.__init__(self)
        MenuClient.__init__(self, queue)
        self._state: UpdateState = UpdateState()
        handler_class = partial(WebHandler, self._get_state)
        self._serv = HTTPServer(("", LOCAL_PORT), handler_class)
        self._t: Thread = Thread(target=self.__update, name="update", daemon=True)
        self._t.start()
        MY_LOG.warning(f"To control looper connect to:\nhttp://{LOCAL_IP}:{LOCAL_PORT}")

    def __update(self) -> None:
        self._serv.serve_forever()

    def _get_state(self) -> UpdateState:
        return self._state

    def _client_stop(self) -> None:
        self._alive = False
        self._serv.shutdown()
        assert not self._t.is_alive()

    def _client_log(self, msg: str) -> None:
        dic = self._get_dic()
        dic[AppName.description] = msg
        self._client_redraw(dic)

    def _client_redraw(self, dic: dict) -> None:
        self._state.bytes = json.dumps(self._recalc_dic(dic)).encode()
        self._state.id += 1
        self._state.ready.set()
        self._state.ready.clear()


if __name__ == "__main__":
    scr = WebScreen(Queue())
    scr.sub_start()
