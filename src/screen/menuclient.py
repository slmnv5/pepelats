from abc import abstractmethod, ABC
from multiprocessing import Queue

from pubsub.sub import Sub
from utils.util_log import MY_LOG


class MenuClient(Sub, ABC):
    def __init__(self, queue: Queue):
        Sub.__init__(self, queue)

    @abstractmethod
    def _client_redraw(self, dic: dict) -> None:
        pass

    @abstractmethod
    def _client_log(self, msg: str) -> None:
        pass

    def _client_enqueue(self, command: list) -> None:
        self.__queue.put(command)
        MY_LOG.debug(f"Added to queue command: {command}")

    def _client_clear_queue(self) -> None:
        self.__queue.empty()
