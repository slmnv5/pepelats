import logging
from abc import ABC
from typing import Dict, Any

import numpy as np

from drum._utildrum import load_audio, max_volume_audio, position_with_swing
from drum.basedrum import ProtoDrum, SimpleDrum
from utils.utilalsa import make_zero_buffer, record_sound_buff, SD_TYPE
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
        accents = pattern["acc"]
        result: np.ndarray = make_zero_buffer(length)
        for sound_name in [x for x in self._sounds if x in pattern]:
            notes = pattern[sound_name]
            steps = len(notes)
            if notes.count("!") + notes.count(".") != steps:
                logging.error(f"sound {sound_name} notes {notes} must contain only '.' and '!'")

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


class AudioDrum(LoadDrumWave):
    """Play drums generated from patterns, change patterns and intencity """

    def __init__(self):
        LoadDrumWave.__init__(self)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._intensity == ProtoDrum._MUTE or not self._length:
            return

        if self._intensity == ProtoDrum._BREAK:
            play_sound_buff(self._bk, out_data, idx)
        elif self._intensity == ProtoDrum._LEVEL1:
            play_sound_buff(self._l1, out_data, idx)
        elif self._intensity == ProtoDrum._LEVEL2:
            play_sound_buff(self._l2, out_data, idx)

    def __str__(self):
        return f"AUDIO:{self._name} {self._bpm:.2F}"


if __name__ == "__main__":
    def test():
        from buffer import LoopSimple
        from buffer._oneloopctrl import OneLoopCtrl
        from threading import Timer
        from utils.utilalsa import make_sin_sound
        from time import sleep
        logging.basicConfig(level=logging.DEBUG)
        ctrl = OneLoopCtrl()
        drum = ctrl.get_drum()
        drum.load_drum_name()
        drum.prepare_drum(100_000)
        sound = make_sin_sound(440, 7.1)
        while not drum._length:
            sleep(0.1)

        print(f"==============>{drum}")

        loop = LoopSimple(ctrl)
        loop._record_samples(sound, 0)
        ctrl.idx = len(sound)
        print("======== start =============")
        loop.trim_buffer()
        Timer(5, ctrl.stop_at_bound, [0]).start()
        loop.play_buffer()
        drum.clear_drum()


    test()
