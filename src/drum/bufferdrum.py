from __future__ import annotations

import os
from abc import ABC

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from drum._patternloader import PatternLoader
from drum._sampleloader import SampleLoader
from drum.basedrum import BaseDrum
from utils.utilconfig import find_path
from utils.utillog import get_my_log
from utils.utilnumpy import play_buffer
from utils.utilother import FileFinder

my_log = get_my_log(__name__)


class BufferDrum(BaseDrum, WrapBuffer, ABC):

    def __init__(self, dname: str):
        BaseDrum.__init__(self)
        WrapBuffer.__init__(self, self._bar_len)
        self._dname = find_path(dname)
        assert os.path.isdir(self._dname)
        self._ff = FileFinder(self._dname, True, ".ini")
        assert self._ff.get_item()
        self._names: list[str] = list()  # names of patterns
        self._pl: PatternLoader \
            = PatternLoader(self._ff.get_full_name(), self._pattern_load,
                            self._pattern_convert, self._pattern_intensity)

    def stop(self) -> None:
        super().stop()
        self.set_silent(True)

    def start(self) -> None:
        super().start()
        self.set_silent(False)

    def randomize(self) -> None:
        super().randomize()

    def show_param(self) -> str:
        base_info = super().show_param()
        intensity = self._pl.get_intensities()[self._ptn_idx]
        name = self._names[self._ptn_idx]
        return f"{base_info}\nintensity: {intensity}\nname: {name}"

    def get_config(self) -> str:
        return self._ff.get_item()

    def set_config(self, config=None) -> None:
        if config:
            self._ff.idx_from_item(config)
        self._ptn_lst = self._pl.get_patterns(self._bar_len, self._par)
        self._names = self._pl.get_names()

    def _set_bar_len(self, bar_len: int) -> None:
        super()._set_bar_len(bar_len)
        self._ptn_lst = self._pl.get_patterns(self._bar_len, self._par)
        self._names = self._pl.get_names()

    def show_config(self) -> str:
        return self._ff.get_str()

    def iterate_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        SampleLoader.set_volume(self._volume)  # change all sound samples
        self.set_silent(True)
        self._ptn_lst = self._pl.get_patterns(self._bar_len, self._par)
        self.set_silent(False)

    def set_par(self, par: float) -> None:
        super().set_par(par)
        self.set_silent(True)
        self._ptn_lst = self._pl.get_patterns(self._bar_len, self._par)
        self.set_silent(False)

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
        if self.is_silent() or not self._bar_len:
            return
        for buff in self._ptn_lst[self._ptn_idx]:
            play_buffer(buff, out_data, idx)

    def get_header(self) -> str:
        return super().get_header() + ":" + self._names[self._ptn_idx]
