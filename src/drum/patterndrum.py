from __future__ import annotations

import os
from abc import abstractmethod

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

    def set_volume(self, volume: float) -> None:
        SampleLoader.set_volume(volume)  # change all sound samples

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

    def stop_drum(self) -> None:
        self.set_silent(True)

    def start_drum(self) -> None:
        self.set_silent(False)

    def show_drum_config(self) -> str:
        return self._ff.get_str()

    def iterate_drum_config(self, steps: int) -> None:
        self._ff.iterate(steps)
