from abc import abstractmethod, ABC
from multiprocessing import Queue

from pubsub.client import Client


class MenuClient(Client, ABC):
    def __init__(self, queue: Queue):
        Client.__init__(self, queue)

    @abstractmethod
    def _client_redraw(self, dic: dict) -> None:
        pass

    @abstractmethod
    def _client_log(self, msg: str) -> None:
        pass
