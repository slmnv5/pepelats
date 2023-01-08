import logging
from random import random
from typing import Dict, Any, Tuple, List

import numpy as np

from drum._utildrum import load_audio, extend_list, position_with_swing
from drum.simpledrum import SimpleDrum
from utils.utilalsa import make_zero_buffer
from utils.utilconfig import SD_TYPE, SD_MAX
from utils.utilnumpy import play_sound_buff, record_sound_buff, zero_sound_buff


class AudioDrum(SimpleDrum):
    """Play drums generated from patterns, change patterns and intensity """

    def __init__(self):
        SimpleDrum.__init__(self)
        self.__buff = None
        self._sounds: Dict[str, np.ndarray] = load_audio()
        self._load_all()

    def prepare_drum(self, length: int) -> None:
        if not length:
            return
        self.__buff = make_zero_buffer(length)
        super().prepare_drum(length)

    def drum_from_pattern(self, pattern) -> List[Tuple[int, float, Any]]:
        logging.debug(f"Preapring pattern: {pattern}")
        steps = pattern["steps"]
        accents = pattern["accents"]
        result: List[Tuple[int, float, Any]] = list()
        for sound_name in [x for x in self._sounds if x in pattern]:
            notes = pattern[sound_name]
            notes = extend_list(notes, steps) if steps else notes
            self.__drum_from_string(result, sound_name, notes, accents)

        return result

    def __drum_from_string(self, result: List[Tuple[int, float, Any]], sound_name: str, notes: str,
                           accents: str) -> None:
        steps = len(notes)
        accents = extend_list(accents, steps)
        step_len = self._length // steps
        sound = self._sounds[sound_name]
        for step_number in range(steps):
            if notes[step_number] != '.':
                step_prob = self._char2float(notes[step_number])
                step_accent = self._char2float(accents[step_number])
                pos = position_with_swing(step_number, step_len, self._swing)
                sound2 = (sound * (step_accent * self._volume * SD_MAX)).astype(SD_TYPE)[:self._length]
                if step_prob:
                    result.append((pos, step_prob, sound2))

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        sound_dict = self.get_sound_dict()
        if not sound_dict:
            return

        position = idx % self._length
        data_len = len(out_data)
        for x, prob, sound in [tuple3 for tuple3 in sound_dict if position <= tuple3[0] < position + data_len]:
            if random() < prob:
                record_sound_buff(self.__buff, sound, position)

        play_sound_buff(self.__buff, out_data, position)
        zero_sound_buff(self.__buff, data_len, position)


if __name__ == "__main__":
    pass
