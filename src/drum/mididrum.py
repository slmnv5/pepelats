import logging
from random import random
from typing import Any, Tuple
from typing import List

import numpy as np

from drum._utildrum import load_midi, extend_list, position_with_swing, is_midi_note
from drum.simpledrum import SimpleDrum


class MidiDrum(SimpleDrum):
    """ MIDI Drum version sending configurable MIDI messages and sysex """

    def __init__(self, out_port):
        SimpleDrum.__init__(self)
        self._sounds = load_midi()
        self._load_all()
        self._out_port = out_port

    def _drum_from_string(self, result: List[Tuple[int, float, Any]],
                          sound_name: str, notes: str, accents: str) -> None:
        steps = len(notes)
        accents = extend_list(accents, steps)
        step_len = self._length // steps
        sound = self._sounds[sound_name]
        for step_number in range(steps):
            if notes[step_number] != '.':
                step_prob = self._char2float(notes[step_number])
                step_accent = self._char2float(accents[step_number])
                pos = position_with_swing(step_number, step_len, self._swing)
                if is_midi_note(sound):
                    sound[2] = int(step_accent * self._volume * 127)
                if step_prob:
                    result.append((pos, step_prob, sound))

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        sound_list = self._get_sound_list()
        if not sound_list:
            return

        position = idx % self._length
        position2 = position + len(out_data)
        for _, step_prob, sound in [tpl for tpl in sound_list if position <= tpl[0] < position2]:
            if random() < step_prob:
                self._play_sound(sound)

    def _play_sound(self, sound) -> None:
        self._out_port.send(sound)


class FakeMidiDrum(MidiDrum):
    def __init__(self, out_port):
        MidiDrum.__init__(self, out_port)
        self.__count: int = 0

    def _play_sound(self, sound) -> None:
        self.__count += 1
        if self.__count % 10 == 0:
            logging.info(f"FakeMidiDrum send: {sound}")


if __name__ == "__main__":
    pass
