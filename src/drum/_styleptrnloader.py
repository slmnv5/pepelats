from math import ceil

import numpy as np

from drum._ptrnloader import PtrnLoader
from utils.util_audio import make_buffer
from utils.util_config import load_ini_section
from utils.util_name import AppName
from utils.util_numpy import from_data_to_buff


class StylePtrnLoader(PtrnLoader):
    """Pattern based drum"""

    def __init__(self, dname: str):
        PtrnLoader.__init__(self, dname)
        self.break_marker = load_ini_section("DRUM").get(AppName.style_break, "")
        # name of accent pattern
        self.__ACCENT: str = "ac"

    def fn_load(self, ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        max_steps: int = max([len(v) for k, v in sect_dic.items()])
        if self.__ACCENT not in sect_dic:
            sect_dic[self.__ACCENT] = "."
        for sname, notes in sect_dic.items():
            assert isinstance(notes, str) and len(notes) > 0
            notes = (notes * ceil(max_steps / len(notes)))[:max_steps]
            ptn_dic[sname] = notes
        # MY_LOG.debug(f"Loaded drum pattern: {ptn_name}\n{ptn_dic}")

    def fn_convert(self, bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        result = list()
        accents: str = ptn_dic[self.__ACCENT]
        steps = len(accents)
        step_len: float = bar_len / steps
        for sname, notes in [(k, v) for k, v in ptn_dic.items() if k != self.__ACCENT]:
            assert steps == len(notes), f"steps: {steps}, notes: {notes}"
            buff = make_buffer(bar_len)
            result.append(buff)
            for k, s in enumerate(notes):
                if s not in "!":
                    continue
                sound_arr = self.sample_loader.get_sound(sname, accents[k] == "!")
                idx = round(k * step_len)
                if k % 2 != 0:
                    chg = round(step_len * par * 0.25)
                    idx += chg
                from_data_to_buff(buff, sound_arr, idx)
        return result

    def fn_energy(self, ptn_dic: dict[str, str]) -> float:
        result: float = 0.0
        accents = ptn_dic[self.__ACCENT]
        for sname, notes in [(k, v) for (k, v) in ptn_dic.items() if k != self.__ACCENT]:
            for k, s in enumerate(notes):
                if s not in "!":
                    continue
                is_accent = accents[k] == '!'
                result += self.sample_loader.get_energy(sname, is_accent) / len(notes)
        return round(result, 2)
