from abc import ABC
from typing import Dict, Any

import numpy as np

from drum._utildrum import load_audio, max_volume_audio, position_with_swing
from drum.basedrum import RealDrum
from utils.log import LOGGER
from utils.utilalsa import make_zero_buffer, record_sound_buff, SD_TYPE


class AuLoader(RealDrum, ABC):
    """ class to load drum patterns, drum sounds, genrate audio bufferes with
    drum tracks using volume and swing parameters """

    def __init__(self):
        RealDrum.__init__(self)
        self._sounds: Dict[str, np.ndarray] = load_audio()
        self.max_volume: float = max_volume_audio(self._sounds)
        self._load_all()

    def _prepare_one(self, pattern, length: int) -> Any:
        LOGGER.debug(f"Preapring pattern: {pattern}")
        accents = pattern["acc"]
        result: np.ndarray = make_zero_buffer(length)
        for sound_name in [x for x in self._sounds if x in pattern]:
            notes = pattern[sound_name]
            steps = len(notes)
            if notes.count("!") + notes.count(".") != steps:
                LOGGER.error(f"sound {sound_name} notes {notes} must contain only '.' and '!'")

            step_len = length // steps
            sound: np.ndarray = self._sounds[sound_name]
            sound = sound[:length]
            assert sound.ndim == 2 and sound.shape[1] == 2
            assert 0 < sound.shape[0] <= length, f"Must be: 0 < {sound.shape[0]} <= {length}"

            for step_number in range(steps):
                if notes[step_number] != '.':
                    step_accent = int(accents[step_number])
                    step_volume = step_accent / 9 * self._volume
                    pos = position_with_swing(step_number, step_len, self._swing)
                    tmp = (sound * step_volume).astype(SD_TYPE)
                    record_sound_buff(result, tmp, pos)

        return result


if __name__ == "__main__":
    def test():
        import time
        LOGGER.setLevel("DEBUG")
        loader = AuLoader()
        loader.prepare_drum(100_000)
        while loader.get_length() == 0:
            time.sleep(0.1)

        print(f"loader: {loader}")


    test()
