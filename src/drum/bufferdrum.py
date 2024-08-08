import os.path
from abc import ABC
from random import random, choices
from threading import Timer

import numpy as np

from drum._euclidptrnloader import EuclidPtrnLoader
from drum._ptrnloader import PtrnManager, PtrnLoader
from drum._styleptrnloader import StylePtrnLoader
from drum.basedrum import BaseDrum
from utils.util_audio import AUDIO_INFO
from utils.util_config import SCR_ROWS
from utils.util_numpy import from_buff_to_data


class BufferDrum(BaseDrum, ABC):
    # Used to skip some drum sounds
    _MODIFY_PROB: float = 0.2

    def __init__(self, ptrn_loader: PtrnLoader):
        BaseDrum.__init__(self)
        self._pm = PtrnManager(ptrn_loader)
        self._ff = ptrn_loader.get_file_finder()
        self._play_lst: list[np.ndarray] = list()  # list to play sounds, changed by randomize
        self._exclude_lst: list[int] = list()  # drums to exclude, changed randomly
        self._name: str = ""  # pattern name
        self._energy: float = 0  # pattern energy
        self._idx: float = 0  # pattern index
        self._param = 0.5  # for this drum it controls swing

        self.set_config()

    def show_param(self) -> str:
        base_info = super().show_param()
        return f"{base_info}\nidx: {self._idx}, energy: {self._energy:.2F}\nname: {self._name}"

    def get_config(self, include_all=False) -> str:
        return self._ff.get_item() if not include_all else self._ff.get_str(SCR_ROWS - 5)

    def set_config(self, config=None) -> None:
        """ if config changes re-load and re-generate patterns """
        if config:
            self._ff.add_item(config)
            assert os.path.isfile(self._ff.get_full_name()), f"Not found file: {self._ff.get_full_name()}"
        self._pm.load_patterns(self._ff.get_full_name())
        self._regenerate()

    def set_bar_len(self, bar_len: int) -> None:
        super().set_bar_len(bar_len)
        self._regenerate()

    def get_next_config(self) -> str:
        return self._ff.get_next()

    def get_prev_config(self) -> str:
        return self._ff.get_prev()

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        self._regenerate()

    def set_param(self, par: float) -> None:
        super().set_param(par)
        self._regenerate()

    def randomize(self) -> None:
        self._play_lst, self._name, self._energy, self._idx = self._pm.random_quiet()
        self.start()

    def _regenerate(self) -> None:
        """ re-generate patterns after smth changed - volume, par, etc"""
        is_stopped = self._is_stopped
        self.stop()
        self._pm.prepare_patterns(self._bar_len, self._volume, self._param)
        self._play_lst, self._name, self._energy, self._idx = self._pm.random_quiet()
        if not is_stopped:
            self.start()

    def play_fill(self) -> None:
        if not self._bar_len:
            return
        self._play_lst, self._name, self._energy, self._idx = self._pm.random_loud()
        self._exclude_lst.clear()
        # return to normal drum
        Timer(self._bar_len / AUDIO_INFO.SD_RATE, self.randomize).start()

    def _modify(self) -> None:
        """ Randomly modify drum by excluding some sounds """
        m: int = len(self._play_lst)
        self._exclude_lst = choices(range(m), k=(m // 3))

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0:
            if random() < self._MODIFY_PROB:
                self._modify()
            else:
                self._exclude_lst.clear()
        for buff in [x for k, x in enumerate(self._play_lst) if k not in self._exclude_lst]:
            from_buff_to_data(buff, out_data, idx)


class EuclidDrum(BufferDrum):
    def __init__(self):
        BufferDrum.__init__(self, EuclidPtrnLoader())

    def __str__(self) -> str:
        return f"E:{self._name}:{self._bpm:.2F}"


class StyleDrum(BufferDrum):
    def __init__(self):
        BufferDrum.__init__(self, StylePtrnLoader())

    def __str__(self) -> str:
        return f"S:{self._name}:{self._bpm:.2F}"
