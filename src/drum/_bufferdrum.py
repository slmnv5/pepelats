from __future__ import annotations

import os
from abc import ABC, abstractmethod
from random import choice, choices, sample, random
from threading import Timer

import numpy as np

from drum._patternloader import PatternLoader
from drum._sampleloader import SampleLoader
from drum.basedrum import BaseDrum
from utils.utilaudio import SD_RATE
from utils.utilconfig import find_path
from utils.utillog import MyLog
from utils.utilnumpy import play_buffer
from utils.utilother import FileFinder

my_log = MyLog()


class BufferDrum(BaseDrum, ABC):

    def __init__(self, ptnrn_dir: str):
        BaseDrum.__init__(self)
        self._sl = SampleLoader()
        self._sl.set_volume(self._volume)
        self.__drum_play_lst: list[np.ndarray] = list()  # play patterns
        self.__drum_modif_lst = self.__drum_play_lst  # midified patterns
        self.__drum_name: str = ""
        self.__drum_intensity: str = ""
        # Used to skip some drum sounds from patterns
        self._DR_COUNT_LST: list[int] = [2, 3, 4, 5]
        self._DR_COUNT_WGHT: list[int] = [1, 5, 5, 2]
        self._DR_MODIF_PROB: float = 0.2

        tmp: str = find_path(ptnrn_dir)
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
        self.randomize()

    def show_config(self) -> str:
        return self._ff.get_str()

    def iterate_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        self._sl.set_volume(self._volume)  # change all sound samples
        self._pl.prepare_patterns(self._bar_len, self._par)

    def set_par(self, par: float) -> None:
        super().set_par(par)
        self._pl.prepare_patterns(self._bar_len, self._par)

    @abstractmethod
    def _load(self, ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        return

    @abstractmethod
    def _convert(self, bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        """All Drum patterns converted into play list """
        return list()

    @abstractmethod
    def _intensity(self, ptn_dic: dict[str, str]) -> str:
        """ Calculate pattern intensity """
        return "0.0"

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped or not self._bar_len:
            return
        if idx % self._bar_len == 0:
            if random() < self._DR_MODIF_PROB:
                self.modify()
        for buff in self.__drum_modif_lst:
            play_buffer(buff, out_data, idx)

    def __str__(self) -> str:
        return f"{super()}:{self.__drum_name}"

    def randomize(self) -> None:
        self.__drum_play_lst, self.__drum_name, self.__drum_intensity \
            = choice(self._pl.get_quiet_patterns())
        self.__drum_modif_lst = self.__drum_play_lst

    def modify(self) -> None:
        dr_count: int = choices(self._DR_COUNT_LST, weights=self._DR_COUNT_WGHT, k=1)[0]
        max_count: int = len(self.__drum_play_lst)
        if dr_count >= max_count:
            self.__drum_modif_lst = self.__drum_play_lst
        else:
            idx_lst: list[int] = sample(range(max_count), k=dr_count)
            self.__drum_modif_lst = [self.__drum_play_lst[x] for x in idx_lst]

    def play_fill(self, idx: int) -> None:
        self.__drum_play_lst, self.__drum_name, self.__drum_intensity \
            = choice(self._pl.get_loud_patterns())
        self.__drum_modif_lst = self.__drum_play_lst
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()
