from abc import abstractmethod
from threading import Event, Timer

from drum.basedrum import SimpleDrum
from utils.utilconfig import MAX_32_INT, ENV_SD_RATE


class OneLoopCtrl:
    """class with events to control one loop, has playback index"""

    __late_sec = 0.1
    __delay_redraw = 0.15
    __late_samples: int = round(__late_sec * ENV_SD_RATE)

    def __init__(self, drum: SimpleDrum):
        self.__drum: SimpleDrum = drum
        self.__is_rec: bool = False
        self.idx: int = 0
        self.__stop_len: int = MAX_32_INT
        self.__stop_event: Event = Event()

    def get_drum(self) -> SimpleDrum:
        return self.__drum

    def _set_drum(self, drum: SimpleDrum) -> None:
        self.__drum = drum

    @abstractmethod
    def _redraw(self) -> None:
        pass

    def get_is_rec(self) -> bool:
        return self.__is_rec

    def set_is_rec(self, is_rec) -> None:
        self.__is_rec = is_rec

    def is_stop_len_set(self) -> bool:
        return self.__stop_len < MAX_32_INT

    def get_stop_len(self) -> int:
        return self.__stop_len

    def get_stop_event(self) -> Event:
        return self.__stop_event

    def _stop_never(self) -> None:
        self.__stop_len = MAX_32_INT

    def stop_at_bound(self, bound_value: int) -> None:
        over: int = self.idx % bound_value if bound_value else 0
        if over < OneLoopCtrl.__late_samples:
            self.__stop_event.set()
            delay = OneLoopCtrl.__delay_redraw
        else:
            self.__stop_len = self.idx - over + bound_value
            delay = self.__stop_len / ENV_SD_RATE + OneLoopCtrl.__delay_redraw
        Timer(delay, self._redraw).start()

    def __str__(self):
        return f"{self.__class__.__name__} Stop:{self.__stop_len} Drum:{self.get_drum()} IsRec:{self.get_is_rec()}"


if __name__ == "__main__":
    pass
