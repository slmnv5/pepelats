import os.path
from configparser import ConfigParser
from typing import Callable

import numpy as np

from utils.utillog import MyLog

my_log = MyLog()


class PatternLoader:
    """Load patterns from INI file. Logic to load, convert and calculate intensity is passed as 3 methods.
    Loaded patterns are converted to playable patterns - ready to play sound """

    def __init__(self, fn_load: Callable[[str, dict[str, str], dict[str, str]], None],
                 fn_convert: Callable[[int, float, dict[str, str]], list[np.ndarray]],
                 fn_intensity: Callable[[dict[str, str]], str]):
        # patterns sorted by energy. Low enrgy patterns used for rythm, high enegry for drum fills/breaks
        self.QUIET_PTRN_FRACTION: float = 0.7
        # split quiet and loud patterns based on intencity
        self.__split_id: int = 0
        self.__fn_load = fn_load
        self.__fn_convert = fn_convert
        self.__fn_intensity = fn_intensity
        # dict of patterns from INI file, name: str, intensity: str
        self.__str_patterns: list[tuple[dict[str, str], str, str]] = list()
        # list of patterns as sounds, name: str, intesity: strs
        self.__snd_patterns: list[tuple[list[np.ndarray], str, str]] = list()

    def load_patterns(self, fname: str) -> None:
        assert os.path.isfile(fname)
        cfg = ConfigParser()
        cfg.read(fname)
        dic: dict[str, dict[str, str]] = {s: dict(cfg.items(s)) for s in cfg.sections()}
        self.__str_patterns.clear()
        for ptn_name in dic:
            ptn_dic: dict[str, str] = dict()
            assert dic[ptn_name], "Empty section in INI file: {fname}, section: {ptn_name}"
            self.__fn_load(ptn_name, dic[ptn_name], ptn_dic)
            intensity: str = self.__fn_intensity(ptn_dic)  # pattern energy
            self.__str_patterns.append((ptn_dic, ptn_name, intensity))
        assert len(self.__str_patterns) > 0
        # sort INI patterns by intensity
        self.__str_patterns.sort(key=lambda x: x[2])
        my_log.debug(f"Done loading from: {fname}")

    def prepare_patterns(self, bar_len: int, par: float) -> None:
        self.__snd_patterns.clear()
        # INI patterns are already sorted by intensity
        for ptn_dic, name, intensity in self.__str_patterns:
            self.__snd_patterns.append((self.__fn_convert(bar_len, par, ptn_dic), name, intensity))
            my_log.debug(f"Converted pattern name: {name}, intensity: {intensity}")
        self.__split_id = round(len(self.__snd_patterns) * self.QUIET_PTRN_FRACTION)

    def get_quiet_patterns(self) -> list[tuple[list[np.ndarray], str, str]]:
        return self.__snd_patterns[:self.__split_id]

    def get_loud_patterns(self) -> list[tuple[list[np.ndarray], str, str]]:
        return self.__snd_patterns[self.__split_id:]
