import logging
from random import random
from typing import Dict, Any

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

    def drum_from_pattern(self, pattern) -> Dict[int, Any]:
        logging.debug(f"Preapring pattern: {pattern}")
        steps = pattern["steps"]
        accents = pattern["accents"]
        result: Dict[int, Any] = dict()
        for sound_name in [x for x in self._sounds if x in pattern]:
            notes = pattern[sound_name]
            notes = extend_list(notes, steps) if steps else notes
            self.__drum_from_string(result, sound_name, notes, accents)

        return result

    def __drum_from_string(self, result: Dict[int, Any],
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
                    result[pos] = sound, step_prob

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        sound_dict = self.get_sound_dict()
        if not sound_dict:
            return

        position = idx % self._length
        data_len = len(out_data)
        for x in [x for x in sound_dict if position <= x < position + data_len]:
            sound, prob = sound_dict[x]
            if random() < prob:
                self._out_port.send(sound)


class FakeMidiDrum(MidiDrum):
    def __init__(self, out_port):
        MidiDrum.__init__(self, out_port)
        self.__count: int = 0

    def _play_pattern(self, pos1: int, pos2: int) -> None:
        pass


if __name__ == "__main__":
    pass
