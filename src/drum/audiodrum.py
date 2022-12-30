import logging
from typing import Dict, Any

import numpy as np

from drum._utildrum import load_audio, drum_from_pattern
from drum.basedrum import ProtoDrum, SimpleDrum
from utils.utilalsa import make_zero_buffer
from utils.utilconfig import SD_MAX
from utils.utilnumpy import play_sound_buff


class AudioDrum(SimpleDrum):
    """Play drums generated from patterns, change patterns and intensity """

    def __init__(self):
        SimpleDrum.__init__(self)
        self._sounds: Dict[str, np.ndarray] = load_audio()
        self._load_all()
        self.__most_loud: np.ndarray = make_zero_buffer(0)

    def _prepare_one(self, pattern, length: int) -> Any:
        logging.debug(f"Preapring pattern: {pattern}")
        buff = drum_from_pattern(pattern, self._sounds, length, self._volume, self._swing)
        if buff.max(initial=0) > self.__most_loud.max(initial=0):
            self.__most_loud = buff
        return buff

    def _get_volume(self) -> float:
        return self.__most_loud.max(initial=0) / SD_MAX

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._intensity == ProtoDrum._MUTE:
            return

        if self._intensity == ProtoDrum._BREAK:
            play_sound_buff(self._bk, out_data, idx)
        elif self._intensity == ProtoDrum._LEVEL1:
            play_sound_buff(self._l1, out_data, idx)
        elif self._intensity == ProtoDrum._LEVEL2:
            play_sound_buff(self._l2, out_data, idx)


if __name__ == "__main__":
    pass
