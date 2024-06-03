import os.path
from abc import abstractmethod
from configparser import ConfigParser
from math import floor
from random import randrange

import numpy as np

from audio.sampleloader import SMPLLOAD
from utils.utilconfig import find_path
from utils.utillog import MYLOG
from utils.utilother import FileFinder


# noinspection PyUnusedLocal
class DrumLoader:
    """ Load drum pattern from INI patterns and create playable lists numpy arrays """

    def __init__(self, ptrn_dir: str):
        tmp: str = find_path(ptrn_dir)
        self.ff = FileFinder(tmp, True, ".ini")
        if not self.ff.get_item():
            raise RuntimeError(f"No INI files found in pattern directory: {ptrn_dir}")

    @abstractmethod
    def fn_load(self, ptn_name: str, sect_dic: dict[str, str], ptn_dic: dict[str, str]) -> None:
        """One Drum pattern put into dictionary"""
        return

    @abstractmethod
    def fn_convert(self, bar_len: int, par: float, ptn_dic: dict[str, str]) -> list[np.ndarray]:
        """All Drum patterns converted into play list """
        return list()

    @abstractmethod
    def fn_intensity(self, ptn_dic: dict[str, str]) -> float:
        """ Calculate pattern intensity """
        return 0.0


class PatternLoader:
    """Load patterns from INI file. Logic to load, convert and calculate intensity is passed as 3 methods.
    Loaded patterns are converted to playable patterns - ready to play sound """

    # patterns sorted by energy. Low energy patterns used for rhythm, high energy for drum fills/breaks
    _QUIET_PTRN_FRACTION: float = 0.7

    def __init__(self, drum_loader: DrumLoader):
        self._dl = drum_loader
        # split quiet and loud patterns based on intensity
        self._quiet_slice: slice = slice(None, None)
        self._loud_slice: slice = slice(None, None)
        # dict of patterns from INI file. It has ptn dict, name, intensity. Sorted by intensity
        self.__ptn: list[tuple[dict[str, str], str, float]] = list()
        # list of patterns converted to sounds, sorted by intensity
        self.__snd: list[list[np.ndarray]] = list()
        self.__idx: int = 0

    def load_patterns(self, fname: str) -> None:
        assert os.path.isfile(fname), f"Not found file: {fname}"
        cfg = ConfigParser()
        cfg.read(fname)
        dic: dict[str, dict[str, str]] = {s: dict(cfg.items(s)) for s in cfg.sections()}
        assert dic, f"Empty INI file: {fname}"
        self.__ptn.clear()
        l1: list[dict[str, str]] = []
        l2: list[str] = []
        l3: list[float] = []
        for ptn_name in dic:
            ptn_dic: dict[str, str] = dict()
            self._dl.fn_load(ptn_name, dic[ptn_name], ptn_dic)
            assert ptn_dic, f"Empty pattern name: {ptn_name} in file: {fname}"
            l1.append(ptn_dic)
            l2.append(ptn_name)
            l3.append(self._dl.fn_intensity(ptn_dic))  # pattern energy
        if not l1:
            raise RuntimeError(f"No patterns found in file: {fname}")
        # sort patterns by intensity
        self.__ptn = sorted(zip(l1, l2, l3), key=lambda x: x[2])
        MYLOG.debug(f"Done loading from: {fname}\n{self.__ptn}")
        ptn_len = len(self.__ptn)
        split_id = floor(ptn_len * self._QUIET_PTRN_FRACTION)

        if split_id:
            self._quiet_slice = slice(0, split_id)
            self._loud_slice = slice(split_id, ptn_len)
        else:
            self._quiet_slice = self._loud_slice = slice(0, ptn_len)

    def prepare_patterns(self, bar_len: int, volume: float, par: float) -> None:
        self.__snd.clear()
        SMPLLOAD.set_volume(volume)
        assert self.__ptn, "Empty string patterns list!"
        # INI patterns are already sorted by intensity
        for ptn_dic, name, energy in self.__ptn:
            self.__snd.append(self._dl.fn_convert(bar_len, par, ptn_dic))
            MYLOG.debug(f"Converted pattern name: {name}, intensity: {energy}")

    def random_quiet(self) -> tuple[list[np.ndarray], str, float, int]:
        """ get random quiet sound, it's name, energy and index. Patterns sorted by energy   """
        self.__idx = randrange(self._quiet_slice.start, self._quiet_slice.stop)
        snd, ptn = self.__snd[self.__idx], self.__ptn[self.__idx]
        return snd, ptn[1], ptn[2], self.__idx

    def random_loud(self) -> tuple[list[np.ndarray], str, float, int]:
        """ get random loud sound, it's name, energy and index. Patterns sorted by energy  """
        self.__idx = randrange(self._loud_slice.start, self._loud_slice.stop)
        snd, ptn = self.__snd[self.__idx], self.__ptn[self.__idx]
        return snd, ptn[1], ptn[2], self.__idx
