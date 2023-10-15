from __future__ import annotations

import numpy as np

from drum._patternloader import PatternLoader
from drum._sampleloader import SampleLoader
from drum.basedrum import BaseDrum
from utils.utilalsa import make_zero_buffer
from utils.utilconfig import find_path
from utils.utillog import get_my_log
from utils.utilnumpy import play_buffer
from utils.utilother import FileFinder, EuclidSlicer

my_log = get_my_log(__name__)


class EuclidDrum(BaseDrum):

    def __init__(self):
        BaseDrum.__init__(self)
        self._silent: bool = True
        self._dname = find_path("config/drum/euclid")
        self._ff = FileFinder(self._dname, True, ".ini")
        assert self._ff.selected_item()
        self._names: list[str] = list()  # names of patterns
        self._intensities: list[str] = list()

    def stop_drum(self) -> None:
        self._silent = True

    def start_drum(self) -> None:
        self._silent = False

    def show_drum_param(self) -> str:
        base_info = super().show_drum_param()
        intensity = self._intensities[self._ptn_idx]
        name = self._names[self._ptn_idx]
        return f"{base_info}\nintensity: {intensity}\nname: {name}"

    def get_config(self) -> str:
        return self._ff.selected_item()

    def show_drum_config(self) -> str:
        return self._ff.get_str()

    def iterate_drum_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        self.stop_drum()
        if config:
            k = self._ff.find_item_idx(config)
            self._ff.select_idx(k)
        bar_len = self._bar_len if bar_len is None else bar_len
        self._set_bar_len(bar_len)

    def _set_bar_len(self, bar_len: int) -> None:
        super()._set_bar_len(bar_len)
        pl = PatternLoader(self._ff.get_full_name(), self._load_one_ptn, self._convert_one_ptn, self._ptn_intensity)
        self._ptn_lst = pl.get_patterns(bar_len)
        self._names = pl.get_names()
        self._intensities = pl.get_intensities()

    def random_drum(self) -> None:
        super().random_drum()

    def change_drum_level(self, chg: int) -> None:
        super().change_drum_level(chg)

    @staticmethod
    def _load_one_ptn(ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        sound_lst = SampleLoader.get_sound_names()
        for sname, euclid_str in [(k, v) for (k, v) in sect_dic.items() if k in sound_lst]:
            euclid_lst = [int(x) for x in euclid_str.split(",")]
            assert len(euclid_lst) == 4
            notes = EuclidSlicer(euclid_lst[0], euclid_lst[1], euclid_lst[2], euclid_lst[3]).get_ptrn_str()
            ptn_dic[sname] = notes
        my_log.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")

    @staticmethod
    def _convert_one_ptn(bar_len: int, ptn_dic: dict[str, str], ptn_list: list[np.ndarray]) -> None:
        """One Drum pattern converted into play list of (buff_position, skip_prob, is_accent, sound_name)"""
        sound_lst = SampleLoader.get_sound_names()
        max_steps: int = max([len(v) for k, v in ptn_dic.items() if k in sound_lst])
        step_len: float = bar_len / max_steps
        for sname, notes in [(k, v) for k, v in ptn_dic.items() if k in sound_lst]:
            buff = make_zero_buffer(round(step_len * len(notes)))
            ptn_list.append(buff)
            for k, s in enumerate(notes):
                if s not in "+*":
                    continue
                idx = round(k * step_len)
                is_accent = s == "*"
                sound_arr = SampleLoader.get_sound(sname, is_accent)
                play_buffer(sound_arr, buff, idx)

        my_log.debug(f"Converted drum patterns: {len(ptn_list)}")

    @staticmethod
    def _ptn_intensity(ptn_dic: dict[str, str]) -> str:
        """ Calculate pattern intensity """
        sound_lst = SampleLoader.get_sound_names()
        max_steps: int = max([len(v) for k, v in ptn_dic.items() if k in sound_lst])
        result: float = 0.0
        for sname, notes in [(k, v) for (k, v) in ptn_dic.items() if k in sound_lst]:
            for k, s in enumerate(notes):
                if s not in "+*":
                    continue
                result += 1
        return f"{round(result / max_steps, 1)}"

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._silent or not self._bar_len:
            return
        sound_lst = self._ptn_lst[self._ptn_idx]
        for buff in sound_lst:
            play_buffer(buff, out_data, idx)
