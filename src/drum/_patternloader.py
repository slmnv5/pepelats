import os.path
from configparser import ConfigParser
from typing import Callable

from utils.utillog import get_my_log

my_log = get_my_log(__name__)


class PatternLoader:
    """Load patterns from INI file. Logic to load and convert passed as two methods.
    Loaded patterns are converted to play patterns - ready to play sound in pattern callback function """

    _loaded: dict[str, list[dict]] = dict()

    def __init__(self, fname: str, fn_load: Callable, fn_conv: Callable, fn_volume: Callable):
        assert os.path.isfile(fname)
        self._fname = fname
        self._fn_conv = fn_conv
        # patterns from INI file
        self._ini_patterns: list[dict[str, any]] = list()
        # patterns ready to play
        self._patterns: list[list[tuple]] = list()
        self._names: list[str] = list()
        self._volumes: list[float] = list()

        if fname in PatternLoader._loaded:
            self._ini_patterns = PatternLoader._loaded[fname]
            self._names = [x["name"] for x in self._ini_patterns]
            self._volumes = [x["volume"] for x in self._ini_patterns]
            my_log.debug(f"Reuse of sorted patterns for: {fname}")
            return

        cfg = ConfigParser()
        cfg.read(fname)
        dic = {s: dict(cfg.items(s)) for s in cfg.sections()}
        for ptn_name in dic:
            ptn_dic = dict()
            assert dic[ptn_name], "Empty section in INI file: {fname}, section: {ptn_name}"
            fn_load(ptn_name, dic[ptn_name], ptn_dic)
            ptn_dic["name"] = ptn_name
            ptn_dic["volume"] = fn_volume(ptn_dic)  # add volume info
            self._ini_patterns.append(ptn_dic)
        assert len(self._ini_patterns) > 0
        # sort INI patterns by volume
        self._ini_patterns.sort(key=lambda x: x["volume"])
        self._names = [x["name"] for x in self._ini_patterns]
        self._volumes = [x["volume"] for x in self._ini_patterns]
        my_log.debug(f"Loaded from: {fname}:\nnames: {self._names}\nvolumes: {self._volumes}")
        PatternLoader._loaded[fname] = self._ini_patterns  # save for later reuse

    def get_patterns(self, bar_len: int) -> list[list[tuple]]:
        result = list()
        # INI patterns already sorted by volume
        for ptn_dic in self._ini_patterns:
            ptn_lst: list[tuple] = list()
            self._fn_conv(bar_len, ptn_dic, ptn_lst)
            result.append(ptn_lst)
        return result

    def get_names(self) -> list[str]:
        return self._names

    def get_volumes(self) -> list[float]:
        return self._volumes
