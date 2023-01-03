import logging
from typing import Dict, List, Tuple

import numpy as np

from drum._utildrum import load_audio, drum_from_pattern
from drum.basedrum import SimpleDrum
from utils.utilconfig import SD_MAX
from utils.utilnumpy import play_sound_buff


class AudioDrum(SimpleDrum):
    """Play drums generated from patterns, change patterns and intensity """

    def __init__(self):
        SimpleDrum.__init__(self)
        self._sounds: Dict[str, np.ndarray] = load_audio()
        self._load_all()

    def _prepare_one(self, pattern) -> Dict[int, List[Tuple[str, float]]]:
        logging.debug(f"Preapring pattern: {pattern}")
        result = drum_from_pattern(pattern, self._sounds, self._length, self._swing)
        self._max_volume = 0.1111111
        return result

    def get_max_volume(self) -> float:
        return round(self._max_volume / SD_MAX, 2)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        pos1 = idx % self._length
        pos2 = pos1 + len(out_data)
        snd_list = self._get_sound(pos1, pos2)
        for sound_name, volume in snd_list:
            sound = self._sounds[sound_name]
            play_sound_buff(sound, out_data, pos1)


if __name__ == "__main__":
    pass
