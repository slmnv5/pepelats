from abc import ABC
from threading import Event

from drum.basedrum import BaseDrum
from mvc.menuclient import MenuClient
from utils.utilconfig import MAX_32_INT


class LoopCtrl(MenuClient, ABC):
    """class with events to control one loop, has playback index and drum"""

    # 5k is about 0.1 second. May be late by this time without going to next full cycle
    _LATE_SAMPLES: int = 5000

    def __init__(self, drum: BaseDrum):
        super().__init__()
        self.idx: int = 0
        self.start_rec = 0
        self._drum: BaseDrum = drum
        self.__is_rec: bool = False
        self.__stop_len: int = MAX_32_INT
        self.__stop_event: Event = Event()

    def get_drum(self) -> BaseDrum:
        return self._drum

    def set_drum(self, drum: BaseDrum) -> None:
        self._drum = drum

    def _stop_song(self, wait: int = 0) -> None:
        pass

    def get_is_rec(self) -> bool:
        return self.__is_rec

    def _set_is_rec(self, is_rec) -> None:
        self.__is_rec = is_rec

    def get_stop_len(self) -> int:
        return self.__stop_len

    def get_stop_event(self) -> Event:
        return self.__stop_event

    def stop_never(self) -> None:
        self.__stop_len = MAX_32_INT
        self.__stop_event.clear()

    def stop_at_bound(self, bound_value: int) -> None:
        over: int = self.idx % bound_value if bound_value else 0
        if over < LoopCtrl._LATE_SAMPLES:
            self.__stop_len = 0
            self.__stop_event.set()
        else:
            self.__stop_len = self.idx + (bound_value - over)

    def __str__(self):
        return f"Looper: IsRec:{self.get_is_rec()} " \
               f"StopLen: {self.__stop_len} Stop: {self.__stop_event.is_set()} " \
               f"Idx: {self.idx}"

    # ===================== drum methods

    def _change_drum_volume(self, chg: float) -> None:
        self._drum.change_volume(1.2 if chg > 0 else 0.8)

    def _show_drum_param(self) -> str:
        return self._drum.show_drum_param()

    def _random_drum(self) -> None:
        self._drum.random_drum()

    def _change_drum_level(self, chg: int) -> None:
        self._drum.change_drum_level(chg)

    def _stop_drum(self) -> None:
        self._drum.stop_drum()

    def _start_drum(self) -> None:
        self._drum.start_drum()
