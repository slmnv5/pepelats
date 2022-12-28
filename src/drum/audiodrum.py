import logging
from abc import ABC
from typing import Dict, Any

import numpy as np

from drum._utildrum import load_audio, max_volume_audio, prepare_drum_pattern
from drum.basedrum import ProtoDrum, SimpleDrum
from utils.utilalsa import play_sound_buff


class LoadDrumWave(SimpleDrum, ABC):
    """ class to load drum patterns, drum sounds, generate audio bufferes with
    drum tracks using volume and swing parameters """

    def __init__(self):
        SimpleDrum.__init__(self)
        self._sounds: Dict[str, np.ndarray] = load_audio()
        self.max_volume: float = max_volume_audio(self._sounds)
        self._load_all()

    def _prepare_one(self, pattern, length: int) -> Any:
        logging.debug(f"Preapring pattern: {pattern}")
        return prepare_drum_pattern(pattern, self._sounds, length, self._volume, self._swing)


class AudioDrum(LoadDrumWave):
    """Play drums generated from patterns, change patterns and intencity """

    def __init__(self):
        LoadDrumWave.__init__(self)

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
