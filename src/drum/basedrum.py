import logging
import pickle
import random
from abc import ABC
from abc import abstractmethod
from threading import Timer
from typing import Dict, Any
from typing import List

import numpy as np

from drum._utildrum import load_all_patterns, bpm_from_length
from utils.utilconfig import SD_RATE, ROOT_DIR
from utils.utilother import FileFinder


# noinspection PyMethodMayBeStatic
class ProtoDrum(FileFinder):
    """ Prototype or interface, default implemFentation of somes methods """

    _MUTE = 0
    _LEVEL1 = 1
    _LEVEL2 = 2
    _BREAK = 3

    def __init__(self):
        FileFinder.__init__(self, "config/drum", False, "")
        self._length: int = 0
        self._bpm: float = 0
        self._sounds: Dict = dict()
        self._ptn_l1: List[Dict[str, Any]] = []
        self._ptn_l2: List[Dict[str, Any]] = []
        self._ptn_bk: List[Dict[str, Any]] = []
        self._intensity: int = ProtoDrum._MUTE
        self._is_break_pending: bool = False
        self._name: str = self.get_item()

    def clear_drum(self) -> None:
        self._length = 0
        self._bpm = 0
        self._intensity = ProtoDrum._MUTE

    def get_length(self) -> int:
        return self._length

    @abstractmethod
    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        pass

    @abstractmethod
    def prepare_drum(self, length: int) -> None:
        pass

    def _randomize(self):
        pass

    def _load_all(self) -> None:
        directory: str = self.get_full_name()
        lst1 = ["drum_level1", "drum_level2", "drum_break"]
        lst2 = [self._ptn_l1, self._ptn_l2, self._ptn_bk]
        for k in range(3):
            logging.info(f"Loaded patterns from directory: {directory}, file: {lst1[k]}")
            load_all_patterns(directory, lst1[k], lst2[k], self._sounds)

    def load_drum_name(self, drum_name: str) -> None:
        if self._name == drum_name:
            return
        self.set_id(self.find_item(drum_name))
        self._name = self.get_item()
        self._load_all()

    def change_intensity(self, change_by: int) -> None:
        if not self._length:
            self._intensity = ProtoDrum._MUTE
            return

        i = self._intensity + change_by
        i = 0 if i > 3 else i
        i = 3 if i < 0 else i
        self._intensity = i

    def play_break_now(self) -> None:
        if not self._length:
            return

        if self._intensity == ProtoDrum._MUTE:
            self._intensity = ProtoDrum._LEVEL1

        def revert():
            self._intensity = ProtoDrum._LEVEL1
            self._is_break_pending = False

        self._randomize()
        self._intensity = ProtoDrum._BREAK
        Timer((self._length // 2) / SD_RATE, revert).start()

    def play_break_later(self, part_len: int, idx: int) -> None:
        if self._is_break_pending:
            return
        samples = self._length // 2
        idx %= part_len
        start_at = (part_len - idx) - samples
        if start_at > 0:
            self._is_break_pending = True
            Timer(start_at / SD_RATE, self.play_break_now).start()


class SimpleDrum(ProtoDrum, ABC):
    """ load drum patterns, drum sounds, genrate audio bufferes with
    drum tracks using volume and swing parameters """

    def __init__(self):
        ProtoDrum.__init__(self)
        self._volume: float = 1.0  # from 0 to 1
        self._max_volume: float = 1.0  # from 0 to 1
        self._swing: float = 0.75
        self._snd_l1 = self._snd_l2 = self._snd_bk = []
        self._l1 = self._l2 = self._bk = []
        self._il1 = self._il2 = self._ibk = 0
        self.__load()

    def save(self) -> None:
        # noinspection PyBroadException
        try:
            full_name = ROOT_DIR + "/" + self.__class__.__name__
            with open(full_name, 'wb') as f:
                pickle.dump((self._volume, self._swing, self._name), f)
        except Exception:
            pass

    def __load(self) -> None:
        # noinspection PyBroadException
        try:
            full_name = ROOT_DIR + "/" + self.__class__.__name__
            with open(full_name, 'rb') as f:
                self._volume, self._swing, name = pickle.load(f)

            self.load_drum_name(name)
        except Exception:
            pass

    def prepare_drum(self, length: int) -> None:
        if not length:
            return
        self._max_volume = 0
        self._length = length
        self._intensity = ProtoDrum._MUTE  # keep it until sound load is done
        self._bpm = bpm_from_length(length)
        self._snd_l1 = [self._prepare_one(p) for p in self._ptn_l1]
        self._snd_l2 = [self._prepare_one(p) for p in self._ptn_l2]
        self._snd_bk = [self._prepare_one(p) for p in self._ptn_bk]
        self._l1 = self._l2 = self._bk = self._snd_l1[0]
        self._length = length
        self._intensity = ProtoDrum._LEVEL1
        self._bpm = bpm_from_length(length)

    def _prepare_one(self, pattern) -> Any:
        pass

    def change_volume(self, change_factor: float) -> None:
        self._volume = round(self._volume * change_factor, 2)
        self._volume = min(1.0, self._volume)
        self._volume = max(0.03, self._volume)
        self.prepare_drum(self._length)

    def change_swing(self, change_by: float) -> None:
        self._swing += change_by
        if self._swing > 0.75:
            self._swing = 0.5
        elif self._swing < 0.5:
            self._swing = 0.75
        self.prepare_drum(self._length)

    def change_intensity(self, change_by: int) -> None:
        if not self._length:
            return
        change_by = (1 if change_by > 0 else -1)
        self._intensity += change_by
        self._intensity %= (ProtoDrum._BREAK + 1)

    def change_index(self, change_by: int) -> None:
        if not self._length:
            return
        change_by = (1 if change_by > 0 else -1)
        self._il1 += change_by
        self._il2 += change_by
        self._ibk += change_by
        self._il1 %= (len(self._snd_l1))
        self._il2 %= (len(self._snd_l2))
        self._ibk %= (len(self._snd_bk))
        self.__set_drums()

    def show_drum_param(self) -> str:
        return f"{str(self)} int: {self._intensity}" \
               f"\nindex: {self._il1}/{len(self._snd_l1)}  " \
               f"{self._il2}/{len(self._snd_l2)}  " \
               f"{self._ibk}/{len(self._snd_bk)}" \
               f"\nvolume(0.0-1.0):{self._get_volume():.2F}\n" \
               f"swing(0.5-0.75):{self._swing:.2F}"

    @abstractmethod
    def _get_volume(self) -> float:
        pass

    def _randomize(self):
        if not self._length:
            return
        self._il1 += random.randint(1, len(self._snd_l1) - 1)
        self._il2 += random.randint(1, len(self._snd_l2) - 1)
        self._ibk += random.randint(1, len(self._snd_bk) - 1)
        self._il1 %= (len(self._snd_l1))
        self._il2 %= (len(self._snd_l2))
        self._ibk %= (len(self._snd_bk))
        self.__set_drums()

    def __set_drums(self):
        self._l1 = self._snd_l1[self._il1]
        self._l2 = self._snd_l2[self._il2]
        self._bk = self._snd_bk[self._ibk]

    def get_info(self):
        return f"{self.__class__.__name__} " \
               f"patterns: {len(self._ptn_l1)}/{len(self._ptn_l2)}/{len(self._ptn_bk)}" \
               f", sounds: {len(self._snd_l1)}/{len(self._snd_l2)}/{len(self._snd_bk)}"

    def __str__(self):
        return f"{self.__class__.__name__}:{self._name}:{self._bpm:.2F}"


if __name__ == "__main__":
    pass
