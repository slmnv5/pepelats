from __future__ import annotations

import os
from abc import ABC, abstractmethod
from random import choice, choices, sample, random
from threading import Timer

import numpy as np

from drum._patternloader import PatternLoader
from drum._sampleloader import SampleLoader
from drum.basedrum import BaseDrum
from utils.utilaudio import Audio, AUDIO
from utils.utilconfig import find_path, SD_RATE
from utils.utilnumpy import from_buff_to_data
from utils.utilother import FileFinder

audio = Audio()


class BufferDrum(BaseDrum, ABC):
    # Used to skip some drum sounds
    _COUNT_LST: list[int] = [2, 3, 4, 5]
    _COUNT_WGHT: list[int] = [1, 5, 5, 2]
    _DR_MODIF_PROB: float = 0.2

    def __init__(self, ptnrn_dir: str):
        BaseDrum.__init__(self)
        self._sl = SampleLoader()
        self._sl.set_volume(self._volume)
        self.__play_lst: list[np.ndarray] = list()  # list to play sounds, changed by randomizes
        self.__modif_lst = self.__play_lst  # midified with some sounds removed
        self.__name: str = ""
        self.__intensity: str = ""
        self._par = 0.5  # for this drum it controls swing

        tmp: str = find_path(ptnrn_dir)
        assert os.path.isdir(tmp)
        self._ff = FileFinder(tmp, True, ".ini")
        assert self._ff.get_item()
        self._pl: PatternLoader \
            = PatternLoader(self._load, self._convert, self._intensity)

    @staticmethod
    def make_drum_buffer(bar_len) -> np.ndarray:
        return np.zeros((bar_len, AUDIO.SD_CH), AUDIO.SD_TYPE)

    def show_param(self) -> str:
        base_info = super().show_param()
        return f"{base_info}\nintensity: {self.__intensity}\nname: {self.__name}"

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
        for buff in self.__modif_lst:
            from_buff_to_data(buff, out_data, idx)

    def __str__(self) -> str:
        return f"{super().__str__()}:{self.__name}"

    def randomize(self) -> None:
        self.__play_lst, self.__name, self.__intensity \
            = choice(self._pl.get_quiet_patterns())
        self.__modif_lst = self.__play_lst

    def modify(self) -> None:
        play_count: int = choices(self._COUNT_LST, weights=self._COUNT_WGHT, k=1)[0]
        max_count: int = len(self.__play_lst)
        if play_count >= max_count:
            self.__modif_lst = self.__play_lst
        else:
            idx_lst: list[int] = sample(range(max_count), k=play_count)
            self.__modif_lst = [self.__play_lst[x] for x in idx_lst]

    def play_fill(self, idx: int) -> None:
        self.__play_lst, self.__name, self.__intensity \
            = choice(self._pl.get_loud_patterns())
        self.__modif_lst = self.__play_lst
        tmp: int = idx % self._bar_len
        if tmp < self.SMALLEST_FILL_FRACTION * self._bar_len:
            tmp = tmp + self._bar_len // 2
        # return to normal level
        Timer(tmp / SD_RATE, self.randomize).start()
