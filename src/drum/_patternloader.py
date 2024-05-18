import os.path
from configparser import ConfigParser
from typing import Callable

import numpy as np

from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class PatternLoader:
    """Load patterns from INI file. Logic to load, convert and calculate intensity is passed as 3 methods.
    Loaded patterns are converted to playable patterns - ready to play sound """

    def __init__(self, fname: str,
                 fn_load: Callable[[str, dict[str, str], dict[str, str]], None],
                 fn_convert: Callable[[int, float, dict[str, str]], list[np.ndarray]],
                 fn_intensity: Callable[[dict[str, str]], str]):
        assert os.path.isfile(fname)
        self._fname = fname
        self._fn_convert = fn_convert
        # patterns from INI file
        self._ini_patterns: list[dict[str, any]] = list()
        # patterns ready to play
        self._patterns: list[list[tuple]] = list()
        self._ini_names: list[str] = list()
        self._ini_intensities: list[float] = list()

        cfg = ConfigParser()
        cfg.read(fname)
        dic = {s: dict(cfg.items(s)) for s in cfg.sections()}
        for ptn_name in dic:
            ptn_dic = dict()
            assert dic[ptn_name], "Empty section in INI file: {fname}, section: {ptn_name}"
            fn_load(ptn_name, dic[ptn_name], ptn_dic)
            ptn_dic["name"] = ptn_name
            ptn_dic["intensity"] = fn_intensity(ptn_dic)  # add volume info
            self._ini_patterns.append(ptn_dic)
        assert len(self._ini_patterns) > 0
        # sort INI patterns by intensity
        self._ini_patterns.sort(key=lambda x: x["intensity"])
        self._ini_names = [x["name"] for x in self._ini_patterns]
        self._ini_intensities = [x["intensity"] for x in self._ini_patterns]
        my_log.debug(f"Loaded from: {fname}:\nnames: {self._ini_names}\nintensities: {self._ini_intensities}")

    def get_patterns(self, bar_len: int, par: float) -> list[list[np.ndarray]]:
        result: list[list[np.ndarray]] = list()
        # INI patterns already sorted by intensity
        for ptn_dic in self._ini_patterns:
            result.append(self._fn_convert(bar_len, par, ptn_dic))
        return result

    def get_names(self) -> list[str]:
        return self._ini_names

    def get_intensities(self) -> list[float]:
        return self._ini_intensities
