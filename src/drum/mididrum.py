import logging
from typing import Dict, Tuple
from typing import List

import numpy as np

from drum._utildrum import load_midi, drum_from_pattern
from drum.basedrum import SimpleDrum


class MidiDrum(SimpleDrum):
    """ MIDI Drum version sending configurable MIDI messages and sysex """

    def __init__(self, out_port):
        SimpleDrum.__init__(self)
        self._sounds: Dict[str, List[int]] = load_midi()
        self._load_all()
        self._out_port = out_port

    def get_max_volume(self) -> float:
        return round(self._max_volume / 127, 2)

    def _prepare_one(self, pattern) -> Dict[int, List[Tuple[str, float]]]:
        logging.debug(f"Preapring pattern: {pattern}")
        result = drum_from_pattern(pattern, self._sounds, self._length, self._swing)
        for lst in result.values():
            for note in lst:
                self._max_volume = max(note[2], self._max_volume)

        return result

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        pos1 = idx % self._length
        pos2 = pos1 + len(out_data)
        snd_list = self._get_sound(pos1, pos2)
        for sound_name, volume in snd_list:
            sound = self._sounds[sound_name]
            sound[2] = int(127 * volume * self._volume)
            self._out_port.send_message(sound)


class FakeMidiDrum(MidiDrum):
    def __init__(self, out_port):
        MidiDrum.__init__(self, out_port)
        self.__count: int = 0

    def _play_pattern(self, pos1: int, pos2: int) -> None:
        pass


if __name__ == "__main__":
    pass
