from multiprocessing import Queue

from mvc.drawinfo import DrawInfo
from utils.utillog import MyLog


class MenuClient:
    def __init__(self, queue: Queue):
        self.__queue: Queue = queue
        self._alive: bool = True
        self._di: DrawInfo = DrawInfo()

    def _client_stop(self) -> None:
        self._alive = False

    def menu_client_start(self):
        while self._alive:
            command = self.__queue.get()
            method_name, *params = command
            print(444444444444444, id(self.__queue), command)
            # noinspection PyBroadException
            try:
                method = getattr(self, method_name)
                method(*params)
            except Exception as ex:
                MyLog().exception(ex)

    def _client_redraw(self, di: DrawInfo) -> None:
        di.recalculate()
        self._di = di

    def menu_client_queue(self, command: list) -> None:
        self.__queue.put(command)
        MyLog().debug(f"Added to queue command: {command}")
