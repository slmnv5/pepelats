import os.path
from abc import abstractmethod, ABC
from configparser import ConfigParser
from math import ceil
from random import randrange

import numpy as np

from drum._sampleloader import SampleLoader
from utils.util_log import MY_LOG
from utils.util_other import FileFinder


# noinspection PyUnusedLocal
class PtrnLoader(ABC):
    """ Load drum pattern from INI patterns and create playable lists numpy arrays """
    sample_loader: SampleLoader = SampleLoader()

    def __init__(self):
        self.break_marker: str = ""

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

    @abstractmethod
    def get_file_finder(self) -> FileFinder:
        pass


class PtrnManager:
    """Load patterns from INI file. Logic to load, convert and calculate intensity is passed as 3 methods.
    Loaded patterns are converted to playable patterns - ready to play sound """

    # patterns sorted by energy. Low energy patterns used for rhythm, high energy for drum fills/breaks
    _BREAK_FRACTION: float = 0.2

    def __init__(self, drum_loader: PtrnLoader):
        self.__quiet: list[tuple[list[np.ndarray], str, float]] = list()  # normal drums
        self.__loud: list[tuple[list[np.ndarray], str, float]] = list()  # list for breaks
        self._drum_loader = drum_loader
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
            self._drum_loader.fn_load(ptn_name, dic[ptn_name], ptn_dic)
            assert ptn_dic, f"Empty pattern name: {ptn_name} in file: {fname}"
            l1.append(ptn_dic)
            l2.append(ptn_name)
            l3.append(self._drum_loader.fn_intensity(ptn_dic))  # pattern energy
        if not l1:
            raise RuntimeError(f"No patterns found in file: {fname}")
        # sort patterns by intensity
        self.__ptn = sorted(zip(l1, l2, l3), key=lambda x: x[2])
        MY_LOG.debug(f"Done loading from: {fname}\n{self.__ptn}")

    def prepare_patterns(self, bar_len: int, volume: float, par: float) -> None:
        self.__snd.clear()
        self._drum_loader.sample_loader.set_volume(volume)
        assert self.__ptn, "Empty patterns!"
        # INI patterns are already sorted by intensity
        for ptn_dic, name, energy in self.__ptn:
            self.__snd.append(self._drum_loader.fn_convert(bar_len, par, ptn_dic))
            # MY_LOG.debug(f"Converted pattern name: {name}, intensity: {energy}")

        if self._drum_loader.break_marker:
            self._separate_by_name()
        else:
            self._separate_by_energy()

    def random_quiet(self) -> tuple[list[np.ndarray], str, float, int]:
        """ get random quiet sound, it's name, energy and index.  """
        self.__idx = randrange(len(self.__quiet))
        snd, name, energy = self.__quiet[self.__idx]
        return snd, name, energy, self.__idx

    def random_loud(self) -> tuple[list[np.ndarray], str, float, int]:
        """ get random loud sound, it's name, energy and index. """
        self.__idx = randrange(len(self.__loud))
        snd, name, energy = self.__loud[self.__idx]
        return snd, name, energy, self.__idx

    def _separate_by_name(self) -> None:
        marker = self._drum_loader.break_marker
        self.__quiet = [(self.__snd[k], x[1], x[2]) for k, x in enumerate(self.__ptn) if marker not in x[1]]
        self.__loud = [(self.__snd[k], x[1], x[2]) for k, x in enumerate(self.__ptn) if marker in x[1]]

    def _separate_by_energy(self) -> None:
        split_idx = ceil((1 - self._BREAK_FRACTION) * len(self.__snd))
        self.__quiet = [(self.__snd[k], x[1], x[2]) for k, x in enumerate(self.__ptn) if k < split_idx]
        self.__loud = [(self.__snd[k], x[1], x[2]) for k, x in enumerate(self.__ptn) if k < split_idx]
