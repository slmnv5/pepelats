from random import random
from typing import Any, Tuple
from typing import List

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
        self._sounds = load_audio()
        self._load_all()

    def prepare_drum(self, length: int) -> None:
        if not length:
            return
        self.__buff = make_zero_buffer(length)
        super().prepare_drum(length)

    def _drum_from_string(self, result: List[Tuple[int, float, Any]], sound_name: str, notes: str,
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
        sound_list = self._get_sound_list()
        if not sound_list:
            return

        position = idx % self._length
        position2 = position + len(out_data)
        for _, step_prob, sound in [tpl for tpl in sound_list if position <= tpl[0] < position2]:
            if random() < step_prob:
                record_sound_buff(self.__buff, sound, position)

        play_sound_buff(self.__buff, out_data, position)
        zero_sound_buff(self.__buff, len(out_data), position)


if __name__ == "__main__":
    pass
