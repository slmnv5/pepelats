from abc import abstractmethod
from multiprocessing import Queue
from time import sleep

from utils.util_log import MY_LOG
from utils.util_name import AppName


class Host:

    def __init__(self, queue: Queue):
        self.__queue: Queue = queue
        self.__alive: bool = True

    @abstractmethod
    def is_broken(self) -> bool:
        return False

    def _full_stop(self) -> None:
        self.__alive = False

    def pub_start(self) -> None:
        MY_LOG.info(f"Host starts")
        while self.__alive and not self.is_broken():
            sleep(5)
        self.__queue.put([AppName.full_stop])
        MY_LOG.info(f"Host stops")

    def _send_msg(self, msg: list[str | float]) -> None:
        if not msg:
            return
        MY_LOG.debug(f"{self.__class__.__name__} sending message: {msg[0]}")
        self.__queue.put(msg)
        if msg[0] == "_full_stop":
            self._full_stop()


if __name__ == "__main__":
    pass
