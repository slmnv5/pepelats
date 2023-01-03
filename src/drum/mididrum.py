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


class FakeMidiDrum(MidiDrum):
    def __init__(self, out_port):
        MidiDrum.__init__(self, out_port)
        self.__count: int = 0

    def _play_pattern(self, pos1: int, pos2: int) -> None:
        pass


if __name__ == "__main__":
    pass
