from __future__ import annotations

import random
from math import ceil

import numpy as np

from drum._sampleloader import SampleLoader
from drum.patterndrum import PatternDrum
from utils.utilconfig import find_path
from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class AudioDrum(PatternDrum):
    """Has additional property self._par. Values from 0 to 1 match swing values from 50% to 75% """

    def __init__(self):
        PatternDrum.__init__(self, find_path("config/drum/audio"))
        self._par: float = 0.6
        self._set_bar_len(0)

    def get_config(self) -> str:
        return self._ff.selected_item()

    @staticmethod
    def load_one_ptn(ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, any]) -> None:
        """One Drum pattern put into dictionary"""
        sound_lst = SampleLoader.get_sound_names()
        max_steps: int = max([len(v) for k, v in sect_dic.items() if k in sound_lst])
        accents: str = sect_dic.get("ac", ".")
        accents = (accents * ceil(max_steps / len(accents)))[:max_steps]
        assert type(accents) == str and len(accents) == max_steps
        ptn_dic["accents"] = accents
        for sname, notes in [(k, v) for (k, v) in sect_dic.items() if k in sound_lst and v]:
            assert type(notes) == str and len(notes) > 0
            notes = (notes * ceil(max_steps / len(notes)))[:max_steps]
            ptn_dic[sname] = notes
        my_log.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")

    @staticmethod
    def convert_one_ptn(bar_len: int, ptn_dic: dict[str, any], ptn_list: list[tuple]) -> None:
        """One Drum pattern converted into play list of (buff_position, skip_prob, is_accent, sound_name)"""
        accents: str = ptn_dic["accents"]
        steps = len(accents)
        step_len = bar_len / steps
        sound_lst = SampleLoader.get_sound_names()
        for sound, notes in [(k, v) for k, v in ptn_dic.items() if k in sound_lst]:
            assert steps == len(notes)
            for k in range(steps):
                if notes[k] not in "123456789!":
                    continue
                step_prob = "0123456789!".index(notes[k]) / 10
                idx = round(k * step_len)
                skip_prob = round(1 - step_prob, 2)
                is_accent = accents[k] != "."
                swing_factor: int = round(step_len) if (k % 2 != 0) else 0
                ptn_list.append((idx, skip_prob, is_accent, swing_factor, sound))
        my_log.debug(f"Converted drum pattern:\n{ptn_list}")

    def random_drum(self) -> None:
        super().random_drum()

    def change_drum_level(self, chg: int) -> None:
        super().change_drum_level(chg)

    def set_par(self, par: float) -> None:
        self._par = round(par, 2)
        self._par = min(1.0, self._par)
        self._par = max(0.0, self._par)

    def get_par(self) -> float:
        return self._par

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

    def show_drum(self) -> str:
        base_info = super().show_drum()
        intensity = f"intens.: {self._volumes[self._ptn_idx]:.3F} swing: {self._par}"
        name = self._names[self._ptn_idx]
        return f"{base_info}\n{intensity}\nname:{name}"
