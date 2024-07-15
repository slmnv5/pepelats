from abc import abstractmethod
from multiprocessing import Queue

from utils.utillog import MyLog
from utils.utilother import DrawInfo


class MenuClient:
    def __init__(self, queue: Queue):
        self.__queue: Queue = queue
        self._alive: bool = True

    def _client_stop(self) -> None:
        self._alive = False

    def menu_client_start(self):
        while self._alive:
            command = self.__queue.get()
            method_name, *params = command
            # noinspection PyBroadException
            try:
                method = getattr(self, method_name)
                method(*params)
            except Exception as ex:
                MyLog().exception(ex)

    @abstractmethod
    def _client_redraw(self, draw_info: DrawInfo) -> None:
        pass

    def menu_client_queue(self, command: list) -> None:
        self.__queue.put(command)
        MyLog().debug(f"Added to queue command: {command}")
