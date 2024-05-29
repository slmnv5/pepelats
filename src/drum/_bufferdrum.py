from __future__ import annotations

from abc import ABC
from random import choices, random
from threading import Timer

import numpy as np

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
        self._name: str = ""
        self._intens: str = ""
        self._par = 0.5  # for this drum it controls swing
        self.set_config()

    def show_param(self) -> str:
        base_info = super().show_param()
        return f"{base_info}\nintensity: {self._intens}\nname: {self._name}"

    def get_config(self) -> str:
        return self._ff.get_item()

    def set_config(self, config=None) -> None:
        if config:
            self._ff.idx_from_item(config)
        self._pl.load_patterns(self._ff.get_full_name())

    def set_bar_len(self, bar_len: int) -> None:
        super().set_bar_len(bar_len)
        self._pl.prepare_patterns(self._bar_len, self._volume, self._par)
        self.randomize()

    def show_config(self) -> str:
        return self._ff.get_str()

    def iterate_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        self.stop()
        self._pl.prepare_patterns(self._bar_len, self._volume, self._par)
        self.randomize()

    def set_par(self, par: float) -> None:
        super().set_par(par)
        self.stop()
        self._pl.prepare_patterns(self._bar_len, self._volume, self._par)
        self.randomize()

    def randomize(self) -> None:
        self._play_lst, self._name, self._intens = self._pl.rand_quiet_ptn()
        self._modify()

    def _modify(self) -> None:
        self._play_count = choices(self._COUNT_LST, weights=self._COUNT_WGHT, k=1)[0]

    def play_fill(self, idx: int) -> None:
        self._play_lst, self._name, self._intens = self._pl.rand_loud_ptn()
        self._play_count = HUGE_INT
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped or not self._bar_len:
            return
        if idx % self._bar_len == 0 and random() < self._DR_MODIF_PROB:
            self._modify()
        for buff in self._play_lst[:self._play_count]:
            from_buff_to_data(buff, out_data, idx)
