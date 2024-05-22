import os.path
from configparser import ConfigParser
from typing import Callable

import numpy as np

from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class PatternLoader:
    """Load patterns from INI file. Logic to load, convert and calculate intensity is passed as 3 methods.
    Loaded patterns are converted to playable patterns - ready to play sound """

    def __init__(self, fn_load: Callable[[str, dict[str, str], dict[str, str]], None],
                 fn_convert: Callable[[int, float, dict[str, str]], list[np.ndarray]],
                 fn_intensity: Callable[[dict[str, str]], str]):
        self.__fn_load = fn_load
        self.__fn_convert = fn_convert
        self.__fn_intensity = fn_intensity

        # patterns from INI file
        self.__patterns: list[dict[str, str]] = list()
        self.__names: list[str] = list()
        self.__intensities: list[str] = list()

    def load_patterns(self, fname: str) -> None:
        assert os.path.isfile(fname)
        cfg = ConfigParser()
        cfg.read(fname)
        dic: dict[str, dict[str, str]] = {s: dict(cfg.items(s)) for s in cfg.sections()}
        self.__patterns.clear()
        self.__names.clear()
        self.__intensities.clear()
        for ptn_name in dic:
            ptn_dic: dict[str, str] = dict()
            assert dic[ptn_name], "Empty section in INI file: {fname}, section: {ptn_name}"
            self.__fn_load(ptn_name, dic[ptn_name], ptn_dic)
            ptn_dic["name"] = ptn_name
            ptn_dic["intensity"] = self.__fn_intensity(ptn_dic)  # add volume info
            self.__patterns.append(ptn_dic)
        assert len(self.__patterns) > 0
        # sort INI patterns by intensity
        self.__patterns.sort(key=lambda x: x["intensity"])
        self.__names = [x["name"] for x in self.__patterns]
        self.__intensities = [x["intensity"] for x in self.__patterns]
        my_log.debug(f"Loaded from: {fname}:\nnames: {self.__names}\nintensities: {self.__intensities}")

    def get_patterns(self, bar_len: int, par: float) -> list[list[np.ndarray]]:
        tmp: list[list[np.ndarray]] = list()
        # INI patterns already sorted by intensity
        for ptn_dic in self.__patterns:
            tmp.append(self.__fn_convert(bar_len, par, ptn_dic))
        return tmp

    def get_pattern_name(self, idx: int) -> str:
        return self.__names[idx] if 0 <= idx < len(self.__names) else ""

    def get_intensity(self, idx: int) -> str:
        return self.__intensities[idx] if 0 <= idx < len(self.__intensities) else ""
