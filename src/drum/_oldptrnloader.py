from __future__ import annotations

from math import ceil

import numpy as np

from audio.audioinfo import make_buffer
from audio.sampleloader import SMPLLOAD
from drum._patternloader import DrumLoader
from utils.utillog import MYLOG
from utils.utilnumpy import from_data_to_buff


class OldPtrnLoader(DrumLoader):
    """Pattern based drum"""

    def __init__(self):
        # drum patterns from INI file
        DrumLoader.__init__(self, "config/drum/pattern")
        # name of accent pattern
        self.__ACNT: str = "ac"

    def fn_load(self, ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        max_steps: int = max([len(v) for k, v in sect_dic.items()])
        if self.__ACNT not in sect_dic:
            sect_dic[self.__ACNT] = "."
        for sname, notes in sect_dic.items():
            assert isinstance(notes, str) and len(notes) > 0
            notes = (notes * ceil(max_steps / len(notes)))[:max_steps]
            ptn_dic[sname] = notes
        MYLOG.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")

    def fn_convert(self, bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        result = list()
        accents: str = ptn_dic[self.__ACNT]
        steps = len(accents)
        step_len: float = bar_len / steps
        for sname, notes in [(k, v) for k, v in ptn_dic.items() if k != self.__ACNT]:
            assert steps == len(notes), f"steps: {steps}, notes: {notes}"
            buff = make_buffer(bar_len)
            result.append(buff)
            for k, s in enumerate(notes):
                if s not in "!":
                    continue
                sound_arr = SMPLLOAD.get_sound(sname, accents[k] == "!")
                idx = round(k * step_len)
                if k % 2 != 0:
                    chg = round(step_len * par * 0.25)
                    idx += chg
                from_data_to_buff(buff, sound_arr, idx)
        return result

    def fn_intensity(self, ptn_dic: dict[str, str]) -> float:
        """ Calculate pattern intensity """
        result: float = 0.0
        accents = ptn_dic[self.__ACNT]
        for sname, notes in [(k, v) for (k, v) in ptn_dic.items() if k != self.__ACNT]:
            for k, s in enumerate(notes):
                if s not in "!":
                    continue
                is_accent = accents[k] == '!'
                result += SMPLLOAD.get_energy(sname, is_accent) / len(notes)
        return result
