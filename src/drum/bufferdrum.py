from __future__ import annotations

import os
from abc import ABC
from math import ceil, floor
from random import randrange, choice
from threading import Timer

import numpy as np

from drum._patternloader import PatternLoader
from drum._sampleloader import SampleLoader
from drum.basedrum import BaseDrum
from utils.utilconfig import find_path, SD_RATE
from utils.utillog import get_my_log
from utils.utilnumpy import play_buffer
from utils.utilother import FileFinder

my_log = get_my_log(__name__)


class BufferDrum(BaseDrum, ABC):

    def __init__(self, dname: str):
        BaseDrum.__init__(self)
        # patterns sorted by energy. Low enrgy patterns used for rythm, high enegry for drum fills/breaks
        self.QUIET_PTRN_FRACTION: float = 0.7
        # Used to skip some drum sounds
        self.DRUM_COUNT_LIST: list[int] = [5, 5, 4, 4, 4, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 2, 2]
        # Fill/break can not be too short, if short is extended by half a bar
        self.SMALLEST_FILL_FRACTION: float = 0.1

        self._ptn_idx: int = 0  # pattern/sound index
        self._ptn_lst: list[list[np.ndarray]] = list()  # play patterns
        tmp: str = find_path(dname)
        assert os.path.isdir(tmp)
        self._ff = FileFinder(tmp, True, ".ini")
        assert self._ff.get_item()
        self._pl: PatternLoader \
            = PatternLoader(self._pattern_load, self._pattern_convert, self._pattern_intensity)

    def show_param(self) -> str:
        base_info = super().show_param()
        intensity = self._pl.get_intensity(self._ptn_idx)
        name = self._pl.get_pattern_name(self._ptn_idx)
        return f"{base_info}\nintensity: {intensity}\nname: {name}"

    def get_config(self) -> str:
        return self._ff.get_item()

    def set_config(self, config=None) -> None:
        if config:
            self._ff.idx_from_item(config)
        self._pl.load_patterns(self._ff.get_full_name())

    def set_bar_len(self, bar_len: int) -> None:
        super().set_bar_len(bar_len)
        self._ptn_lst = self._pl.get_patterns(self._bar_len, self._par)
        assert self._ptn_lst

    def show_config(self) -> str:
        return self._ff.get_str()

    def iterate_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        SampleLoader.set_volume(self._volume)  # change all sound samples
        self.stop()
        self._ptn_lst = self._pl.get_patterns(self._bar_len, self._par)
        self.start()

    def set_par(self, par: float) -> None:
        super().set_par(par)
        self.stop()
        self._ptn_lst = self._pl.get_patterns(self._bar_len, self._par)
        self.start()

    @staticmethod
    def _pattern_load(ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        pass

    @staticmethod
    def _pattern_convert(bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        """All Drum patterns converted into play list """
        pass

    @staticmethod
    def _pattern_intensity(ptn_dic: dict[str, str]) -> str:
        """ Calculate pattern intensity """
        return "0.0"

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped or not self._bar_len:
            return
        for buff in self._ptn_lst[self._ptn_idx][0:self._play_drum_count]:
            play_buffer(buff, out_data, idx)

    def get_header(self) -> str:
        name = self._pl.get_pattern_name(self._ptn_idx)
        return super().get_header() + ":" + name

    def randomize(self) -> None:
        self._is_fill = False
        self._play_drum_count = choice(self.DRUM_COUNT_LIST)
        lst_len: int = len(self._ptn_lst)
        assert lst_len > 0
        lst_split: int = ceil(lst_len * self.QUIET_PTRN_FRACTION)
        self._ptn_idx = randrange(0, lst_split)
        self.start()

    def play_fill(self, idx: int) -> None:
        if self._is_fill or not self._bar_len:
            return
        self._is_fill = True
        self._play_drum_count = 5
        lst_len: int = len(self._ptn_lst)
        lst_split: int = floor(lst_len * self.QUIET_PTRN_FRACTION)
        self._ptn_idx = randrange(lst_split, lst_len)

        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()

    def start(self) -> None:
        self._ptn_idx = 0
        self._is_stopped = False
