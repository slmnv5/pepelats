from __future__ import annotations

import os
import random
from math import ceil

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from drum._patternloader import PatternLoader
from drum._sampleloader import SampleLoader, ACCENT_FACTOR
from drum.basedrum import BaseDrum
from utils.utilconfig import find_path
from utils.utillog import get_my_log
from utils.utilother import FileFinder

my_log = get_my_log(__name__)


class PatternDrum(BaseDrum, WrapBuffer):
    """Pattern based drum"""

    def __init__(self):
        # drum patterns from INI file
        BaseDrum.__init__(self)
        WrapBuffer.__init__(self, self._bar_len)
        self._dname = find_path("config/drum/pattern")
        assert os.path.isdir(self._dname)
        self._ff = FileFinder(self._dname, True, ".ini")
        assert self._ff.selected_item()
        self._names: list[str] = list()  # names of patterns
        self._intensities: list[str] = list()

    def random_drum(self) -> None:
        super().random_drum()

    def change_drum_level(self, chg: int) -> None:
        super().change_drum_level(chg)

    def get_config(self) -> str:
        return self._ff.selected_item()

    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        self.stop_drum()
        if config:
            k = self._ff.find_item_idx(config)
            self._ff.select_idx(k)
        bar_len = self._bar_len if bar_len is None else bar_len
        self._set_bar_len(bar_len)

    def set_volume(self, volume: float) -> None:
        super().set_volume(volume)
        SampleLoader.set_volume(self._volume)  # change all sound samples

    def _set_bar_len(self, bar_len: int) -> None:
        super()._set_bar_len(bar_len)
        self.new_buff(self._bar_len)
        pl = PatternLoader(self._ff.get_full_name(), self._pattern_load, self._pattern_convert, self._pattern_intensity)
        self._ptn_lst = pl.get_patterns(bar_len)
        self._names = pl.get_names()
        self._intensities = pl.get_intensities()

    def stop_drum(self) -> None:
        self.set_silent(True)
        super().stop_drum()

    def start_drum(self) -> None:
        self.set_silent(False)

    def show_drum_config(self) -> str:
        return self._ff.get_str()

    def iterate_drum_config(self, steps: int) -> None:
        self._ff.iterate(steps)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self.is_silent or not self._bar_len:
            return
        data_len = len(out_data)
        pos1 = idx % self._bar_len
        pos2 = pos1 + data_len
        sound_lst = self._ptn_lst[self._ptn_idx]
        for tpl in [x for x in sound_lst if pos1 <= x[0] < pos2]:
            pos, skip_prob, is_accent, swing_factor, sound = tpl
            if skip_prob > 0 and random.random() < skip_prob:
                continue
            sound_arr = SampleLoader.get_sound(sound, is_accent)
            if swing_factor:
                chg = round(swing_factor * self._par * 0.25)
                pos += chg
            self.record_samples(sound_arr, pos)

        self.play_samples(out_data, idx, True)

    def show_drum_param(self) -> str:
        base_info = super().show_drum_param()
        intensity = self._intensities[self._ptn_idx]
        name = self._names[self._ptn_idx]
        return f"{base_info}\nintensity: {intensity}\nname: {name}"

    @staticmethod
    def _pattern_load(ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        sound_lst = SampleLoader.get_sound_names()
        max_steps: int = max([len(v) for k, v in sect_dic.items() if k in sound_lst])
        accents: str = sect_dic.get("ac", ".")
        accents = (accents * ceil(max_steps / len(accents)))[:max_steps]
        assert type(accents) == str and len(accents) == max_steps
        ptn_dic["accents"] = accents
        for sname, notes in [(k, v) for (k, v) in sect_dic.items() if k in sound_lst and v]:
            assert type(notes) == str and len(notes) > 0
            try:
                notes = (notes * ceil(max_steps / len(notes)))[:max_steps]
                ptn_dic[sname] = notes
                my_log.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")
            except Exception as ex:
                my_log.error(f"Error {ex} in drum pattern: {ptn_name}\n{ptn_dic}")

    @staticmethod
    def _pattern_convert(bar_len: int, ptn_dic: dict[str, str], ptn_list: list[tuple]) -> None:
        """One Drum pattern converted into play list of (buff_position, skip_prob, is_accent, sound_name)"""
        accents: str = ptn_dic["accents"]
        steps = len(accents)
        step_len = bar_len / steps
        sound_lst = SampleLoader.get_sound_names()
        for sname, notes in [(k, v) for k, v in ptn_dic.items() if k in sound_lst]:
            assert steps == len(notes)
            for k, s in enumerate(notes):
                if s not in "123456789!":
                    continue
                step_prob = "0123456789!".index(notes[k]) / 10
                idx = round(k * step_len)
                skip_prob = round(1 - step_prob, 2)
                is_accent = accents[k] != "."
                swing_factor: int = round(step_len) if (k % 2 != 0) else 0
                ptn_list.append((idx, skip_prob, is_accent, swing_factor, sname))

        my_log.debug(f"Converted drum patterns: {len(ptn_list)}")

    @staticmethod
    def _pattern_intensity(ptn_dic: dict[str, str]) -> str:
        """ Calculate pattern intensity """
        result: float = 0.0
        sound_lst = SampleLoader.get_sound_names()
        accents = ptn_dic["accents"]
        for sname, notes in [(k, v) for (k, v) in ptn_dic.items() if k in sound_lst]:
            for k, s in enumerate(notes):
                if s not in "123456789!":
                    continue
                step_prob = "0123456789!".index(s) / 10
                result += step_prob * (1 if accents[k] != '!' else ACCENT_FACTOR)
        return f"{round(result, 1)}"

    def get_drum_header(self) -> str:
        return super().get_drum_header() + ":" + self._names[self._ptn_idx]
