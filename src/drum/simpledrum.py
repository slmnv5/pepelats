import logging
from abc import ABC
from abc import abstractmethod
from random import randrange, random
from typing import Any, Tuple
from typing import List

import numpy as np

import utils
from drum._basedrum import BaseDrum
from drum._utildrum import bpm_from_length
from utils.utilconfig import ENV_SD_RATE, ENV_DRUM_SWING, ENV_DRUM_VOLUME


class SimpleDrum(BaseDrum, ABC):
    """ load drum patterns, drum sounds, genrate audio bufferes with
    drum tracks using volume and swing parameters """

    def __init__(self):
        BaseDrum.__init__(self)
        self.__step: int = 0
        self._swing: float = ENV_DRUM_SWING
        self._volume: float = ENV_DRUM_VOLUME
        self._snd_l1: List[List[Tuple[int, float, Any]]] = list()
        self._snd_l2: List[List[Tuple[int, float, Any]]] = list()
        self._snd_bk: List[List[Tuple[int, float, Any]]] = list()
        self._il1: int = 0
        self._il2: int = 0
        self._ibk: int = 0

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        sound_dict = self.get_sound_dict()
        if not sound_dict:
            return

        position = idx % self._length
        if not position:
            self.__step = 0

        position2 = position + len(out_data)
        for tuple3 in [tuple3 for tuple3 in sound_dict if position <= tuple3[0] < position2]:
            self.__step += 1
            _, step_prob, sound = tuple3
            if random() < step_prob:
                self._play_sample(sound, position, out_data)
            self._finalize_play(out_data, position)

    @abstractmethod
    def _finalize_play(self, out_data: np.ndarray, position: int) -> None:
        pass

    @abstractmethod
    def _play_sample(self, sound: Any, position: int, out_data: np.ndarray) -> None:
        pass

    def get_sound_dict(self) -> List[Tuple[int, float, Any]]:
        if self._intensity == BaseDrum._LEVEL1:
            return self._snd_l1[self._il1]
        elif self._intensity == BaseDrum._LEVEL2:
            return self._snd_l2[self._il2]
        elif self._intensity == BaseDrum._BREAK:
            return self._snd_bk[self._ibk]
        else:
            return BaseDrum._EMPTY_DRUMS

    @abstractmethod
    def drum_from_pattern(self, pattern) -> List[Tuple[int, float, Any]]:
        """ return dict: sample number -> drum_name, pattern_step_volume """
        pass

    def prepare_drum(self, length: int) -> None:
        if not length:
            return
        self._length = length
        self._intensity = BaseDrum._MUTE  # keep it until sound load is done
        self._bpm = bpm_from_length(length)
        self._snd_l1 = [self.drum_from_pattern(p) for p in self._ptn_l1]
        self._snd_l2 = [self.drum_from_pattern(p) for p in self._ptn_l2]
        self._snd_bk = [self.drum_from_pattern(p) for p in self._ptn_bk]
        self._il1 = self._il2 = self._ibk = 0
        self._length = length
        self._intensity = BaseDrum._LEVEL1
        self._bpm = bpm_from_length(length)
        logging.info(f"Prepared drum: {self}, sample length: {self._length}")

    def change_volume(self, change_factor: float) -> None:
        self._volume = round(self._volume * change_factor, 2)
        self._volume = min(1.0, self._volume)
        self._volume = max(0.05, self._volume)
        utils.utilconfig.ENV_DRUM_VOLUME = self._volume
        self.prepare_drum(self._length)

    def change_swing(self, change_by: float) -> None:
        self._swing += change_by
        if self._swing > 0.75:
            self._swing = 0.5
        elif self._swing < 0.5:
            self._swing = 0.75
        utils.utilconfig.ENV_DRUM_SWING = self._swing
        self.prepare_drum(self._length)

    def change_intensity(self, change_by: int) -> None:
        if not self._length:
            return
        change_by = (1 if change_by > 0 else -1)
        self._intensity += change_by
        self._intensity %= (BaseDrum._BREAK + 1)

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

    def show_drum_param(self) -> str:
        return f"\nmax_volume(0.0-1.0):{self.get_volume():.2F}" \
               f"\nswing(0.5-0.75):{self._swing:.2F}" \
               f"\n{str(self)} int: {self._intensity}" \
               f"\nindex: {self._il1}/{len(self._snd_l1)}  " \
               f"{self._il2}/{len(self._snd_l2)}  " \
               f"{self._ibk}/{len(self._snd_bk)}"

    def get_volume(self) -> float:
        return self._volume

    def get_swing(self) -> float:
        return self._swing

    def _randomize(self):
        if not self._length:
            return
        self._il1 += randrange(len(self._snd_l1))
        self._il2 += randrange(len(self._snd_l2))
        self._ibk += randrange(len(self._snd_bk))
        self._il1 %= (len(self._snd_l1))
        self._il2 %= (len(self._snd_l2))
        self._ibk %= (len(self._snd_bk))

    def get_info(self):
        return f"{self.__class__.__name__} " \
               f"patterns: {len(self._ptn_l1)}/{len(self._ptn_l2)}/{len(self._ptn_bk)}" \
               f", sounds: {len(self._snd_l1)}/{len(self._snd_l2)}/{len(self._snd_bk)}"

    def __str__(self):
        return f"{self.__class__.__name__}:{self._name}:{self._bpm:.2F}"


if __name__ == "__main__":
    pass
