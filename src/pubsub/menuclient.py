from abc import abstractmethod, ABC
from multiprocessing import Queue

from pubsub.sub import Sub


class MenuClient(Sub, ABC):
    def __init__(self, queue: Queue):
        Sub.__init__(self, queue)

    @abstractmethod
    def _client_redraw(self, dic: dict) -> None:
        pass

    @abstractmethod
    def _client_log(self, msg: str) -> None:
        pass
