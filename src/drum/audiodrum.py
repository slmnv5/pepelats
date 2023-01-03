import logging
from typing import Dict, Tuple, Any

import numpy as np

from drum._utildrum import load_audio, extend_list, position_with_swing
from drum.simpledrum import SimpleDrum
from utils.utilconfig import SD_TYPE, SD_MAX


class AudioDrum(SimpleDrum):
    """Play drums generated from patterns, change patterns and intensity """

    def __init__(self):
        SimpleDrum.__init__(self)
        self._sounds: Dict[str, np.ndarray] = load_audio()
        self._load_all()

    def drum_from_pattern(self, pattern) -> Dict[Tuple[int, int], Any]:
        logging.debug(f"Preapring pattern: {pattern}")
        steps = pattern["steps"]
        accents = pattern["accents"]
        result: Dict[Tuple[int, int], Any] = dict()
        for sound_name in [x for x in self._sounds if x in pattern]:
            notes = pattern[sound_name]
            notes = extend_list(notes, steps) if steps else notes
            self.__drum_from_string(result, sound_name, notes, accents)

        return result

    def __drum_from_string(self, result: Dict[Tuple[int, int], Any], sound_name: str, notes: str, accents: str) -> None:
        assert notes.count("!") + notes.count(".") == len(notes), f"Pattern symbol must be '.' or '!'"
        steps = len(notes)
        accents = extend_list(accents, steps)
        step_len = self._length // steps
        sound = self._sounds[sound_name]
        for step_number in range(steps):
            if notes[step_number] == '!':
                step_accent = int(accents[step_number])
                pos = position_with_swing(step_number, step_len, self._swing)
                sound2 = (sound * (step_accent / 9 * self._volume * SD_MAX)).astype(SD_TYPE)
                result[pos, pos + len(sound2)] = sound2

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        sound_dict = self.get_sound_dict()
        pos1 = idx % self._length
        pos2 = pos1 + len(out_data)
        for x, y in [(x, y) for (x, y) in sound_dict if pos1 < y and pos2 >= x]:
            sound = sound_dict[x, y]
            start = max(pos1, x)
            stop = min(pos2, y)
            out_data[0:stop - start] += sound[start - x:stop - x]


if __name__ == "__main__":
    pass
