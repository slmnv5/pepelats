from __future__ import annotations

from abc import abstractmethod
from multiprocessing import Queue

from utils.utillog import MYLOG
from utils.utilother import DrawInfo


class MenuClient:
    def __init__(self, queue: Queue):
        self.__queue: Queue = queue

    def start(self):
        while True:
            command = self.__queue.get()
            method_name, *params = command
            # noinspection PyBroadException
            try:
                method = getattr(self, method_name)
                method(*params)
            except Exception as ex:
                MYLOG.exception(ex)

    @abstractmethod
    def _redraw(self, draw_info: DrawInfo | None) -> None:
        pass

    def add_command(self, command: list) -> None:
        self.__queue.put(command)
        MYLOG.debug(f"Added command: {command}")
