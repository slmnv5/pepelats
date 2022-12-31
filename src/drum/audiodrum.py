import logging
import os
from typing import Dict, Any

import numpy as np

from drum._utildrum import load_audio, audio_drum_from_pattern
from drum.basedrum import ProtoDrum, SimpleDrum
from utils.utilconfig import SD_MAX, ConfigName
from utils.utilnumpy import play_sound_buff


class AudioDrum(SimpleDrum):
    """Play drums generated from patterns, change patterns and intensity """

    def __init__(self):
        SimpleDrum.__init__(self)
        self._volume = float(os.getenv(ConfigName.audio_drum_volume, "0.75"))

        self._sounds: Dict[str, np.ndarray] = load_audio()
        self._load_all()

    def _prepare_one(self, pattern) -> Any:
        logging.debug(f"Preapring pattern: {pattern}")
        result = audio_drum_from_pattern(pattern, self._sounds, self._length, self._volume, self._swing)
        vol = result.max(initial=0)
        self._max_volume = max(vol, self._max_volume)
        return result

    def get_volume(self) -> float:
        return round(self._max_volume / SD_MAX, 2)

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
