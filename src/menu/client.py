from multiprocessing import Queue

from utils.util_log import MY_LOG


class Client:

    def __init__(self, queue: Queue):
        self.__queue: Queue = queue
        self._alive: bool = True

    def _full_stop(self):
        self._alive = False

    def sub_start(self):
        MY_LOG.info(f"Client starts")
        while self._alive:
            msg: list[str | float] = self.__queue.get()
            # noinspection PyBroadException
            try:
                MY_LOG.debug(f"{self.__class__.__name__} got message: {msg[0]}")
                method = getattr(self, msg[0])
                method(*msg[1:])
            except Exception as ex:
                MY_LOG.exception(ex)
        MY_LOG.info(f"Client stops")

    def _add_to_queue(self, msg: list[str | float]) -> None:
        self.__queue.put(msg)

    def _clear_queue(self) -> None:
        self.__queue.empty()


if __name__ == "__main__":
    pass
