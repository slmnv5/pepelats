from __future__ import annotations

import os
from abc import ABC
from random import choice

import numpy as np

from drum._patternloader import PatternLoader
from drum._sampleloader import SampleLoader
from drum.basedrum import BaseDrum
from utils.utilconfig import find_path
from utils.utillog import get_my_log
from utils.utilnumpy import play_buffer
from utils.utilother import FileFinder

my_log = get_my_log(__name__)


class BufferDrum(BaseDrum, ABC):
    # Used to skip some drum sounds for the whole bar
    DRUM_COUNT_LIST: list[int] = [4, 4, 4, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2, 2, 1]

    def __init__(self, dname: str):
        BaseDrum.__init__(self)
        self._drum_count: int = 5
        tmp: str = find_path(dname)
        assert os.path.isdir(tmp)
        self._ff = FileFinder(tmp, True, ".ini")
        assert self._ff.get_item()
        self._pl: PatternLoader \
            = PatternLoader(self._pattern_load, self._pattern_convert, self._pattern_intensity)

    def randomize(self) -> None:
        super().randomize()

    def show_param(self) -> str:
        base_info = super().show_param()
        intensity = self._pl.get_intensities()[self._ptn_idx]
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
        if idx % self._bar_len == 0:
            self._drum_count = choice(self.DRUM_COUNT_LIST)
        for buff in self._ptn_lst[self._ptn_idx][0:self._drum_count]:
            play_buffer(buff, out_data, idx)

    def get_header(self) -> str:
        name = self._pl.get_pattern_name(self._ptn_idx)
        return super().get_header() + ":" + name
