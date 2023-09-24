from __future__ import annotations

import traceback
from abc import abstractmethod
from multiprocessing import Queue

from utils.utillog import get_my_log
from utils.utilother import DrawInfo

my_log = get_my_log(__name__)


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
            except Exception:
                my_log.error(f"Error: {traceback.format_exc()} command: {command}")

    @abstractmethod
    def _redraw(self, draw_info: DrawInfo | None) -> None:
        pass

    def add_command(self, command: list) -> None:
        self.__queue.put(command)
        my_log.debug(f"Added command: {command}")
