import logging
from typing import Dict, List, Tuple

import numpy as np

from drum._utildrum import load_audio, extend_list, drum_from_string
from drum.basedrum import SimpleDrum, ProtoDrum
from utils.utilnumpy import play_sound_buff


class AudioDrum(SimpleDrum):
    """Play drums generated from patterns, change patterns and intensity """

    def __init__(self):
        SimpleDrum.__init__(self)
        self._sounds = load_audio()
        self._load_all()

    def drum_from_pattern(self, pattern) -> Dict[int, List[Tuple[str, float]]]:
        logging.debug(f"Preapring pattern: {pattern}")
        steps = pattern["steps"]
        accents = pattern["accents"]
        result: Dict[int, List[Tuple[str, float]]] = dict()
        for sound_name in [x for x in self._sounds if x in pattern]:
            notes = pattern[sound_name]
            notes = extend_list(notes, steps) if steps else notes
            drum_from_string(result, sound_name, notes, accents, self._length, self._swing)

        return result

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._intensity == ProtoDrum._MUTE:
            return

        pos1 = idx % self._length
        pos2 = pos1 + len(out_data)
        snd_list: List[Tuple[str, float]] = self._get_sound(pos1, pos2)
        print(11111111, snd_list)
        for sound_name, volume in snd_list:
            sound = self._sounds[sound_name]
            play_sound_buff(sound, out_data, pos1)


if __name__ == "__main__":
    pass
