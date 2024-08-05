from abc import abstractmethod, ABC
from multiprocessing import Queue

from utils.util_log import MY_LOG


class MenuClient(ABC):
    def __init__(self, queue: Queue):
        self.__queue: Queue = queue
        self._alive: bool = True

    def _client_stop(self) -> None:
        self._alive = False

    def client_start(self):
        while self._alive:
            command = self.__queue.get()
            method_name, *params = command
            MY_LOG.debug(f"{self.__class__.__name__} got command: {method_name}")
            # noinspection PyBroadException
            try:
                method = getattr(self, method_name)
                method(*params)
            except Exception as ex:
                MY_LOG.exception(ex)

    @abstractmethod
    def _client_redraw(self, dic: dict) -> None:
        raise RuntimeError("This method should NOT be called()")

    def _client_enqueue(self, command: list) -> None:
        self.__queue.put(command)
        MY_LOG.debug(f"Added to queue command: {command}")

    def _client_clear_queue(self) -> None:
        self.__queue.empty()
