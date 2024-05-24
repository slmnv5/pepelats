from __future__ import annotations

from math import ceil

import numpy as np

from drum._sampleloader import SampleLoader, ACCENT_FACTOR
from drum.bufferdrum import BufferDrum
from utils.utilalsa import make_zero_buffer
from utils.utillog import get_my_log
from utils.utilnumpy import record_buffer

my_log = get_my_log(__name__)


class PatternDrum(BufferDrum):
    """Pattern based drum"""

    def __init__(self):
        # drum patterns from INI file
        BufferDrum.__init__(self, "config/drum/pattern")

    @staticmethod
    def _load(ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        sound_lst = SampleLoader.get_sound_names()
        max_steps: int = max([len(v) for k, v in sect_dic.items() if k in sound_lst])
        accents: str = sect_dic.get("ac", ".")
        accents = (accents * ceil(max_steps / len(accents)))[:max_steps]
        assert isinstance(accents, str) and len(accents) == max_steps
        ptn_dic["accents"] = accents
        for sname, notes in [(k, v) for (k, v) in sect_dic.items() if k in sound_lst and v]:
            assert isinstance(notes, str) and len(notes) > 0
            notes = (notes * ceil(max_steps / len(notes)))[:max_steps]
            ptn_dic[sname] = notes
        my_log.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")

    @staticmethod
    def _convert(bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        result = list()
        sound_lst = SampleLoader.get_sound_names()
        accents: str = ptn_dic["accents"]
        steps = len(accents)
        step_len: float = bar_len / steps
        for sname, notes in [(k, v) for k, v in ptn_dic.items() if k in sound_lst]:
            assert steps == len(notes), f"steps: {steps}, notes: {notes}"
            buff = make_zero_buffer(bar_len)
            result.append(buff)
            for k, s in enumerate(notes):
                if s not in "!":
                    continue
                sound_arr = SampleLoader.get_sound(sname, accents[k] == "!")
                idx = round(k * step_len)
                if k % 2 != 0:
                    chg = round(step_len * par * 0.25)
                    idx += chg
                record_buffer(buff, sound_arr, idx)

        my_log.debug(f"Converted all drum patterns: {len(result)}")
        return result

    @staticmethod
    def _intensity(ptn_dic: dict[str, str]) -> str:
        """ Calculate pattern intensity """
        result: float = 0.0
        sound_lst = SampleLoader.get_sound_names()
        accents = ptn_dic["accents"]
        for sname, notes in [(k, v) for (k, v) in ptn_dic.items() if k in sound_lst]:
            for k, s in enumerate(notes):
                if s not in "!":
                    continue
                is_accent = accents[k] == '!'
                factor = 1 if not is_accent else ACCENT_FACTOR * ACCENT_FACTOR
                result += factor * SampleLoader.get_power(sname) / len(notes)
        return f"{round(result, 1)}"
