from __future__ import annotations

import os
from abc import ABC
from random import choice, random
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
        # Used to skip some drum sounds from patterns
        self.DRUM_SKIP_PROB: float = 0.2
        self.__drum_skip_lst: list[int] = list()
        self.__drum_play_lst: list[np.ndarray] = list()  # play patterns
        self.__drum_name: str = ""
        self.__drum_intensity: str = ""

        tmp: str = find_path(dname)
        assert os.path.isdir(tmp)
        self._ff = FileFinder(tmp, True, ".ini")
        assert self._ff.get_item()
        self._pl: PatternLoader \
            = PatternLoader(self._load, self._convert, self._intensity)

    def show_param(self) -> str:
        base_info = super().show_param()
        return f"{base_info}\nintensity: {self.__drum_intensity}\nname: {self.__drum_name}"

    def get_config(self) -> str:
        return self._ff.get_item()

    def set_config(self, config=None) -> None:
        if config:
            self._ff.idx_from_item(config)
        self._pl.load_patterns(self._ff.get_full_name())

    def set_bar_len(self, bar_len: int) -> None:
        super().set_bar_len(bar_len)
        self._pl.prepare_patterns(self._bar_len, self._par)

    def show_config(self) -> str:
        return self._ff.get_str()

    def iterate_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        SampleLoader.set_volume(self._volume)  # change all sound samples
        self._pl.prepare_patterns(self._bar_len, self._par)
        self.randomize()

    def set_par(self, par: float) -> None:
        super().set_par(par)
        self._pl.prepare_patterns(self._bar_len, self._par)

    @staticmethod
    def _load(ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        pass

    @staticmethod
    def _convert(bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        """All Drum patterns converted into play list """
        pass

    @staticmethod
    def _intensity(ptn_dic: dict[str, str]) -> str:
        """ Calculate pattern intensity """
        return "0.0"

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped or not self._bar_len:
            return
        for buff in [x for x in self.__drum_play_lst if id(x) not in self.__drum_skip_lst]:
            play_buffer(buff, out_data, idx)

    def get_header(self) -> str:
        return super().get_header() + f":{self.__drum_name}"

    def randomize(self) -> None:
        self.__drum_play_lst, self.__drum_name, self.__drum_intensity \
            = choice(self._pl.get_quiet_patterns())
        assert self.__drum_play_lst
        self.__drum_skip_lst.clear()
        for drum in self.__drum_play_lst:
            if random() < self.DRUM_SKIP_PROB:
                self.__drum_skip_lst.append(id(drum))

    def play_fill(self, idx: int) -> None:
        self.__drum_play_lst, self.__drum_name, self.__drum_intensity \
            = choice(self._pl.get_loud_patterns())
        assert self.__drum_play_lst
        self.__drum_skip_lst.clear()
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()
