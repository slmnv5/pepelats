import os.path
from abc import ABC
from random import choices, random
from threading import Timer

import numpy as np

from basic.audioinfo import AudioInfo
from drum._euclidptrnloader import EuclidPtrnLoader
from drum._ptrnloader import PtrnManager, PtrnLoader
from drum._styleptrnloader import StylePtrnLoader
from drum.basedrum import BaseDrum
from utils.util_numpy import from_buff_to_data


class BufferDrum(BaseDrum, ABC):
    # Used to skip some drum sounds
    _COUNT_LST: list[int] = [2, 3, 4, 5, 6]
    _COUNT_WEIGHT: list[int] = [3, 5, 5, 2, 2]
    _MAX_COUNT: int = max([2, 3, 4, 5, 6])
    _DR_MODIFY_PROB: float = 0.2

    def __init__(self, ptrn_loader: PtrnLoader):
        BaseDrum.__init__(self)
        self._pm = PtrnManager(ptrn_loader)
        self._ff = ptrn_loader.ff
        self._play_lst: list[np.ndarray] = list()  # list to play sounds, changed by randomize
        self._play_count: int = self._MAX_COUNT  # how many drums will play in the play list, changed by modify
        self._name: str = ""  # pattern name
        self._energy: float = 0  # pattern energy
        self._idx: float = 0  # pattern index
        self._par = 0.5  # for this drum it controls swing

        self.set_config()

    def show_param(self) -> str:
        base_info = super().show_param()
        return f"{base_info}\nidx: {self._idx}, energy: {self._energy:.2F}\nname: {self._name}"

    def get_config(self, include_all=False) -> str:
        return self._ff.get_item() if not include_all else self._ff.get_str()

    def set_config(self, config=None) -> None:
        """ if config changes re-load and re-generate patterns """
        if config:
            self._ff.add_item(config)
            assert os.path.isfile(self._ff.get_full_name()), f"Not found file: {self._ff.get_full_name()}"
        self._pm.load_patterns(self._ff.get_full_name())
        self._regenerate()

    def set_bar_len(self, bar_len: int) -> None:
        super().set_bar_len(bar_len)
        self._regenerate()

    def iterate_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        self._regenerate()

    def set_par(self, par: float) -> None:
        super().set_par(par)
        self._regenerate()

    def randomize(self) -> None:
        self._play_lst, self._name, self._energy, self._idx = self._pm.random_quiet()
        self.start()

    def _regenerate(self) -> None:
        """ re-generate patterns after smth changed - volume, par, etc"""
        save_stop = self._is_stopped
        self.stop()
        self._pm.prepare_patterns(self._bar_len, self._volume, self._par)
        self._play_lst, self._name, self._energy, self._idx = self._pm.random_quiet()
        if not save_stop:
            self.start()

    def play_fill(self, idx: int) -> None:
        self._play_lst, self._name, self._energy, self._idx = self._pm.random_loud()
        self._play_count = self._MAX_COUNT
        tmp: int = idx % self._bar_len if self._bar_len else 0
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / AudioInfo().SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0 and random() < self._DR_MODIFY_PROB:
            self._play_count = choices(self._COUNT_LST, weights=self._COUNT_WEIGHT, k=1)[0]
        for buff in self._play_lst[:self._play_count]:
            from_buff_to_data(buff, out_data, idx)


class EuclidDrum(BufferDrum):
    def __init__(self):
        BufferDrum.__init__(self, EuclidPtrnLoader())

    def __str__(self) -> str:
        return f"E:{self._name}:{self._bpm:.2F}"


class StyleDrum(BufferDrum):
    def __init__(self):
        BufferDrum.__init__(self, StylePtrnLoader())

    def __str__(self) -> str:
        return f"S:{self._name}:{self._bpm:.2F}"
