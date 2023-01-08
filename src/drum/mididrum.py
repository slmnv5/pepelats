import logging
from typing import Any, List, Tuple

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

    def __drum_from_string(self, result: List[Tuple[int, float, Any]],
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

    def _play_sample(self, sound: Any, position: int, out_data: np.ndarray) -> None:
        self._out_port.send(sound)

    def _finalize_play(self, out_data: np.ndarray, position: int) -> None:
        pass


class FakeMidiDrum(MidiDrum):
    def __init__(self, out_port):
        MidiDrum.__init__(self, out_port)
        self.__count: int = 0

    def _play_sample(self, sound: Any, position: int, out_data: np.ndarray) -> None:
        self.__count += 1
        if self.__count % 10 == 0:
            logging.info(f"FakeOutPort MIDI: {sound}")


if __name__ == "__main__":
    pass
