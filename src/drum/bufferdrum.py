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
        self._intensities: list[str] = list()

    def stop_drum(self) -> None:
        super().stop_drum()
        self._set_silent(True)

    def start_drum(self) -> None:
        super().start_drum()
        self._set_silent(False)

    def random_drum(self) -> None:
        super().random_drum()

    def show_drum_param(self) -> str:
        base_info = super().show_drum_param()
        intensity = self._intensities[self._ptn_idx]
        name = self._names[self._ptn_idx]
        return f"{base_info}\nintensity: {intensity}\nname: {name}"

    def get_config(self) -> str:
        return self._ff.get_item()

    def show_drum_config(self) -> str:
        return self._ff.get_str()

    def iterate_drum_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        self.stop_drum()
        if config:
            self._ff.get_idx(config)

        bar_len = self._bar_len if bar_len is None else bar_len
        self._set_bar_len(bar_len)

    def _set_bar_len(self, bar_len: int) -> None:
        super()._set_bar_len(bar_len)
        self._pl = PatternLoader(self._ff.get_full_name(), self._pattern_load, self._pattern_convert,
                                 self._pattern_intensity)
        self._ptn_lst = self._pl.get_patterns()
        self._names = self._pl.get_names()
        self._intensities = self._pl.get_intensities()

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        SampleLoader.set_volume(self._volume)  # change all sound samples
        self._set_silent(True)
        self._ptn_lst = self._pl.get_patterns()
        self._set_silent(False)

    def set_par(self, par: float) -> None:
        super().set_par(par)
        self._set_silent(True)
        self._ptn_lst = self._pl.get_patterns()
        self._set_silent(False)

    @staticmethod
    def _pattern_load(ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        pass

    def _pattern_convert(self, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        """All Drum patterns converted into play list """
        pass

    @staticmethod
    def _pattern_intensity(ptn_dic: dict[str, str]) -> str:
        """ Calculate pattern intensity """
        return "0.0"

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_silent() or not self._bar_len:
            return
        for buff in self._ptn_lst[self._ptn_idx]:
            play_buffer(buff, out_data, idx)

    def get_drum_header(self) -> str:
        return super().get_drum_header() + ":" + self._names[self._ptn_idx]
