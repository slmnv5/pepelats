from __future__ import annotations

import numpy as np

from drum._bufferdrum import BufferDrum
from utils.utillog import MYLOG
from utils.utilnumpy import from_data_to_buff
from utils.utilother import EuclidSlicer


class EuclidDrum(BufferDrum):
    _BAR_STEPS: int = 16  # each bar has so many steps

    def __init__(self):
        BufferDrum.__init__(self, "config/drum/euclid")

    def _load(self, ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        for sname, euclid_str in sect_dic.items():
            ptn_lst = [int(x) for x in euclid_str.split(",")]
            if ptn_lst[0] and ptn_lst[1]:
                ptn_dic[sname] = EuclidSlicer(ptn_lst[0], ptn_lst[1], ptn_lst[2], ptn_lst[3]).get_ptrn_str()
        MYLOG.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")

    def _convert(self, bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        result = list()
        for sname, notes in ptn_dic.items():
            new_len = round(bar_len * len(notes) / EuclidDrum._BAR_STEPS)
            buff = self.make_drum_buffer(new_len)
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
                from_data_to_buff(buff, sound_arr, idx)

        return result

    def _intensity(self, ptn_dic: dict[str, str]) -> str:
        """ Calculate pattern intensity """
        result: float = 0.0
        for sname, notes in ptn_dic.items():
            for s in notes:
                if s not in "+*":
                    continue
                is_accent = s == '*'
                result += self._sl.get_energy(sname, is_accent) / len(notes)
        return f"{round(result, 1)}"
