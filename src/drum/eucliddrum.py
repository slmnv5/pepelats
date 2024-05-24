from __future__ import annotations

import numpy as np

from drum._sampleloader import ACCENT_FACTOR
from drum.bufferdrum import BufferDrum
from utils.utilalsa import make_zero_buffer
from utils.utillog import get_my_log
from utils.utilnumpy import record_buffer
from utils.utilother import EuclidSlicer

my_log = get_my_log(__name__)


class EuclidDrum(BufferDrum):
    _DRUM_STEPS: int = 16

    def __init__(self):
        BufferDrum.__init__(self, "config/drum/euclid")

    def _load(self, ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        for sname, euclid_str in sect_dic.items():
            euclid_lst = [int(x) for x in euclid_str.split(",")]
            notes = EuclidSlicer(euclid_lst[0], euclid_lst[1], euclid_lst[2], euclid_lst[3]).get_ptrn_str()
            ptn_dic[sname] = notes
        my_log.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")

    def _convert(self, bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        result = list()
        for sname, notes in ptn_dic.items():
            new_len = round(bar_len * len(notes) / EuclidDrum._DRUM_STEPS)
            buff = make_zero_buffer(new_len)
            result.append(buff)
            step_len: float = new_len / len(notes)
            for k, s in enumerate(notes):
                if s not in "+*":
                    continue
                idx = round(k * step_len)
                if k % 2 != 0:
                    chg = round(step_len * par * 0.25)
                    idx += chg
                sound_arr = self._sl.get_sound(sname, s == "*")
                record_buffer(buff, sound_arr, idx)

        my_log.debug(f"Converted all drum patterns: {len(result)}")
        return result

    def _intensity(self, ptn_dic: dict[str, str]) -> str:
        """ Calculate pattern intensity """
        result: float = 0.0
        for sname, notes in ptn_dic.items():
            for _, s in enumerate(notes):
                if s not in "+*":
                    continue
                is_accent = s == '*'
                factor = 1 if not is_accent else ACCENT_FACTOR * ACCENT_FACTOR
                result += factor * self._sl.get_power(sname) / len(notes)

        return f"{round(result, 1)}"
