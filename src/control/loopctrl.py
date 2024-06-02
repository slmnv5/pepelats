from abc import ABC, abstractmethod
from multiprocessing import Queue
from threading import Event

from drum.basedrum import BaseDrum
from mvc.menuclient import MenuClient
from utils.utilconfig import HUGE_INT


class LoopCtrl(MenuClient, ABC):
    """class with events to control one loop, has playback index and drum"""

    # 5k is about 0.1 second. May be late by this time without going to next full cycle
    _LATE_SAMPLES: int = 5000

    def __init__(self, queue: Queue, drum_type: str):
        super().__init__(queue)
        self.idx: int = 0
        self._drum_type: str = drum_type
        self._drum: BaseDrum = BaseDrum()
        self._start_rec_idx: int = 0
        self.__is_rec: bool = False
        self.__stop_len: int = 0
        self.__stop_event: Event = Event()
        self.stop_never()

    # noinspection PyMethodMayBeStatic

    @abstractmethod
    def _drum_create(self, drum_info: dict[str, any]) -> None:
        pass

    def _song_stop(self, wait: int = 0) -> None:
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
        self.__stop_len = HUGE_INT
        self.__stop_event.clear()

    def stop_at_bound(self, bound_value: int) -> None:
        over: int = self.idx % bound_value if bound_value else 0
        if over < LoopCtrl._LATE_SAMPLES:
            self.__stop_len = 0
            self.__stop_event.set()
        else:
            self.__stop_len = self.idx + (bound_value - over)

    def __str__(self):
        return f"IsRec:{self.get_is_rec()} " \
               f"StopLen: {self.__stop_len} Stop: {self.__stop_event.is_set()} " \
               f"Idx: {self.idx}"

    # ===================== drum methods

    def _drum_iterate_config(self, steps: int) -> None:
        self._drum.iterate_config(steps)

    def _drum_get_config(self) -> str:
        return self._drum.get_config(True)

    def _drum_set_par(self, chg: float) -> None:
        chg = 0.2 if chg > 0 else -0.2
        self._drum.set_par(self._drum.get_par() + chg)

    def _drum_set_volume(self, chg: float) -> None:
        volume = self._drum.get_volume()
        volume *= (1.2 if chg > 0 else 0.83)
        self._drum.set_volume(volume)

    def _drum_show_param(self) -> str:
        return self._drum.show_param()

    def _drum_randomize(self) -> None:
        self._drum.randomize()

    def _drum_play_fill(self) -> None:
        self._drum.play_fill(self.idx)

    def _drum_stop(self) -> None:
        self._drum.stop()

    def _drum_set_config(self, config: str = None) -> None:
        self._drum.set_config(config)

    def get_start_rec_idx(self) -> int:
        return self._start_rec_idx

    def get_drum(self) -> BaseDrum:
        return self._drum
