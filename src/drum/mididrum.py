import logging
from typing import Dict, Tuple

import numpy as np

from drum._utildrum import load_midi
from drum.basedrum import SimpleDrum, ProtoDrum


class MidiDrum(SimpleDrum):
    """ MIDI Drum version sending configurable MIDI messages and sysex """

    def __init__(self, out_port):
        SimpleDrum.__init__(self)
        self._sounds = load_midi()
        self._load_all()
        self._out_port = out_port

    def drum_from_pattern(self, pattern) -> Dict[int, Tuple[str, float]]:
        logging.debug(f"Preapring pattern: {pattern}")
        return dict()

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._intensity == ProtoDrum._MUTE:
            return

        pos1 = idx % self._length
        pos2 = pos1 + len(out_data)
        snd_list: Tuple[str, float] = self._get_sound(pos1, pos2)
        for sound_name, volume in snd_list:
            sound, max_volume, length = self._sounds[sound_name]
            sound[2] = int(max_volume * volume * self._volume)
            self._out_port.send_message(sound)


class FakeMidiDrum(MidiDrum):
    def __init__(self, out_port):
        MidiDrum.__init__(self, out_port)
        self.__count: int = 0

    def _play_pattern(self, pos1: int, pos2: int) -> None:
        pass


if __name__ == "__main__":
    pass
