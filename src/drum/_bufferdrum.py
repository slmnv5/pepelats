from __future__ import annotations

import os.path
from abc import ABC
from random import choices, random
from threading import Timer

import numpy as np

from drum._euclidptrnloader import EuclidPtrnLoader
from drum._oldptrnloader import OldPtrnLoader
from drum._patternloader import PatternLoader, DrumLoader
from drum.basedrum import BaseDrum
from utils.utilconfig import SD_RATE, HUGE_INT
from utils.utilnumpy import from_buff_to_data


class BufferDrum(BaseDrum, ABC):
    # Used to skip some drum sounds
    _COUNT_LST: list[int] = [2, 3, 4, 5]
    _COUNT_WGHT: list[int] = [1, 5, 5, 2]
    _DR_MODIF_PROB: float = 0.2

    def __init__(self, drum_loader: DrumLoader):
        BaseDrum.__init__(self)
        self._pl = PatternLoader(drum_loader)
        self._ff = drum_loader.ff
        self._play_lst: list[np.ndarray] = list()  # list to play sounds, changed by randomize
        self._play_count: int = HUGE_INT  # how many arrays will play in the play list, changed by modify
        self._name: str = ""  # pattern name
        self._energy: float = 0  # pattern energy
        self._idx: float = 0  # pattern index
        self._par = 0.5  # for this drum it controls swing
        self._stale: bool = True  # if stale it needs pattern re-loading and re-generation
        self.set_config()

    def show_param(self) -> str:
        base_info = super().show_param()
        return f"{base_info}\nidx: {self._idx}, energy: {self._energy:.2F}\nname: {self._name}"

    def get_config(self, include_all=False) -> str:
        return self._ff.get_item() if not include_all else self._ff.get_str()

    def set_config(self, config=None) -> None:
        """ if config changes re-load and re-generate patterns """
        if config:
            self._ff.idx_from_item(config)
            assert os.path.isfile(self._ff.get_full_name()), f"Not found file: {self._ff.get_full_name()}"
        self._pl.load_patterns(self._ff.get_full_name())
        self._stale = True

    def set_bar_len(self, bar_len: int) -> None:
        """ setting bar_len needs patern generation """
        assert bar_len > 0 and self._bar_len == 0, "Method set_bar_len must be called only once"
        super().set_bar_len(bar_len)
        self._stale = True

    def iterate_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        self._stale = True

    def set_par(self, par: float) -> None:
        super().set_par(par)
        self._stale = True

    def _modify(self) -> None:
        self._play_count = choices(self._COUNT_LST, weights=self._COUNT_WGHT, k=1)[0]

    def randomize(self) -> None:
        if self._stale:
            self.stop()
            self._pl.prepare_patterns(self._bar_len, self._volume, self._par)
            self._stale = False
        self._play_lst, self._name, self._energy, self._idx = self._pl.random_quiet()
        self._modify()
        self.start()

    def play_fill(self, idx: int) -> None:
        self._play_lst, self._name, self._energy, self._idx = self._pl.random_loud()
        self._play_count = HUGE_INT
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0 and random() < self._DR_MODIF_PROB:
            self._modify()
        for buff in self._play_lst[:self._play_count]:
            from_buff_to_data(buff, out_data, idx)


class EuclidPtrnDrum(BufferDrum):
    def __init__(self):
        BufferDrum.__init__(self, EuclidPtrnLoader())

    def __str__(self) -> str:
        return f"E:{self._name}:{self._bpm:.2F}"


class OldPtrnDrum(BufferDrum):
    def __init__(self):
        BufferDrum.__init__(self, OldPtrnLoader())

    def __str__(self) -> str:
        return f"O:{self._name}:{self._bpm:.2F}"
