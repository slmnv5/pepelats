from __future__ import annotations

import os
import random
from abc import abstractmethod

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from drum._patternloader import PatternLoader
from drum._sampleloader import SampleLoader
from drum.basedrum import BaseDrum
from utils.utillog import get_my_log
from utils.utilother import FileFinder

my_log = get_my_log(__name__)


class PatternDrum(BaseDrum, WrapBuffer):
    """Pattern based drum"""

    def __init__(self, dname: str):
        # drum patterns from INI file
        assert os.path.isdir(dname)
        BaseDrum.__init__(self)
        WrapBuffer.__init__(self, self._bar_len)
        self._dname = dname
        self._ff = FileFinder(self._dname, True, ".ini")
        assert self._ff.selected_item()
        self._names: list[str] = list()  # names of patterns
        self._volumes: list[float] = list()  # intensity of patterns

    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        self.stop_drum()
        if config:
            k = self._ff.find_item_idx(config)
            self._ff.select_idx(k)
        bar_len = self._bar_len if bar_len is None else bar_len
        self._set_bar_len(bar_len)

    def change_volume(self, chg: float) -> None:
        SampleLoader.change_volume(chg)  # change all sound samples

    def get_volume(self) -> float:
        return SampleLoader.get_volume()

    def _set_bar_len(self, bar_len: int) -> None:
        super()._set_bar_len(bar_len)
        self.new_buff(self._bar_len)
        pl = PatternLoader(self._ff.get_full_name(), self.load_one_ptn, self.convert_one_ptn)
        self._ptn_lst = pl.get_patterns(bar_len)
        self._names = pl.get_names()
        self._volumes = pl.get_volumes()

    @staticmethod
    @abstractmethod
    def load_one_ptn(ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, any]) -> None:
        pass

    @staticmethod
    @abstractmethod
    def convert_one_ptn(bar_len: int, ptn_dic: dict[str, any], ptn_list: list[tuple]) -> None:
        pass

    def show_drum_param(self) -> str:
        base_info = super().show_drum_param()
        intensity = self._volumes[self._ptn_idx]
        name = self._names[self._ptn_idx]
        return f"{base_info}\nintensity: {intensity:.3F}\nname:{name}"

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self.is_silent or not self._bar_len:
            return
        data_len = len(out_data)
        pos1 = idx % self._bar_len
        pos2 = pos1 + data_len
        sound_lst = self._ptn_lst[self._ptn_idx]
        for pos, skip_prob, is_accent, sound in [x for x in sound_lst if pos1 <= x[0] < pos2]:
            if skip_prob > 0 and random.random() < skip_prob:
                continue
            sound = SampleLoader.get_sound(sound, is_accent)
            self._record_samples(sound, pos)

        self.play_samples(out_data, idx, True)

    def stop_drum(self) -> None:
        self.set_silent(True)

    def start_drum(self) -> None:
        self.set_silent(False)

    def show_drum_config(self) -> str:
        return self._ff.get_str()

    def iterate_drum_config(self, steps: int) -> None:
        self._ff.iterate(steps)
