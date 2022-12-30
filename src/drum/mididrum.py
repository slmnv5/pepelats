import logging
from typing import Dict, Any
from typing import List

import numpy as np

from drum._utildrum import load_midi
from drum._utildrum import position_with_swing
from drum.basedrum import ProtoDrum, SimpleDrum


class MidiDrum(SimpleDrum):
    """ MIDI Drum version sending configurable MIDI messages and sysex """

    def __init__(self, out_port):
        SimpleDrum.__init__(self)
        self._sounds: Dict[str, List[int]] = load_midi()
        self._load_all()
        self._out_port = out_port

    def _prepare_one(self, pattern, length: int) -> Any:
        # logging.debug(f"Preapring pattern: {pattern}")
        accents = pattern["accents"]
        result: Dict[int, List[List[int]]] = dict()
        for sound_name in [x for x in self._sounds if x in pattern]:
            notes = pattern[sound_name]
            steps = len(notes)
            if notes.count("!") + notes.count(".") != steps:
                logging.error(f"sound {sound_name} notes {notes} must contain only '.' and '!'")

            step_len = length // steps
            sound: List[int] = self._sounds[sound_name]
            assert type(sound) == list
            assert len(sound) == 3
            for step_number in range(steps):
                if notes[step_number] != '.':
                    step_accent = int(accents[step_number])
                    step_volume = int(step_accent / 9 * self._volume * 127)
                    assert step_volume <= 127
                    pos = position_with_swing(step_number, step_len, self._swing)
                    sound[2] = step_volume
                    lst = result.get(pos, list())
                    lst.append(sound)
                    result[pos] = lst
        logging.debug(f"Prepared pattern: {result}")
        return result

    def _play_midi_pattern(self, pattern: Dict[int, List[List[int]]], pos1: int, pos2: int) -> None:
        for msg_lst in [pattern[x] for x in pattern if pos1 <= x < pos2]:
            for msg in msg_lst:
                self._out_port.send_message(msg)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._intensity == ProtoDrum._MUTE:
            return

        pos1 = idx % self._length
        pos2 = pos1 + len(out_data)
        if self._intensity == ProtoDrum._LEVEL1:
            self._play_midi_pattern(self._l1, pos1, pos2)
        elif self._intensity == ProtoDrum._LEVEL2:
            self._play_midi_pattern(self._l2, pos1, pos2)
        elif self._intensity == ProtoDrum._BREAK:
            self._play_midi_pattern(self._bk, pos1, pos2)
        else:
            pass


class FakeMidiDrum(MidiDrum):
    def __init__(self, out_port):
        MidiDrum.__init__(self, out_port)
        self.__count: int = 0

    def _play_midi_pattern(self, pattern: Dict[int, List[List[int]]], pos1: int, pos2: int) -> None:
        self.__count += 1
        if self.__count % 100 > 0:
            return
        for msg_lst in [pattern[x] for x in pattern if pos1 <= x < pos2]:
            for msg in msg_lst:
                logging.debug(f"FakeMidiDrum send: {msg}")


if __name__ == "__main__":
    pass
