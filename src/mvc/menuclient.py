

from abc import abstractmethod
from multiprocessing import Queue

from utils.utilconfig import ConfigName
from utils.utillog import MYLOG
from utils.utilother import DrawInfo


class MenuClient:
    def __init__(self, queue: Queue):
        self.__queue: Queue = queue

    def menu_client_start(self):
        while True:
            command = self.__queue.get()
            method_name, *params = command
            if method_name == ConfigName.menu_client_stop:
                break
            # noinspection PyBroadException
            try:
                method = getattr(self, method_name)
                method(*params)
            except Exception as ex:
                MYLOG.exception(ex)

    @abstractmethod
    def _menu_client_redraw(self, draw_info: DrawInfo | None) -> None:
        pass

    def menu_client_queue(self, command: list) -> None:
        self.__queue.put(command)
        MYLOG.debug(f"Added to queue command: {command}")
