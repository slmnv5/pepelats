import os
from abc import ABC
from typing import Dict, Any, List

from rtmidi.midiutil import open_midioutput

from drum._utildrum import load_sounds, position_with_swing, bpm_from_length, max_volume_midi
from drum.basedrum import RealDrum
from utils.log import LOGGER
from utils.utilalsa import MockMidiPort


class MiLoader(RealDrum, ABC):
    """ Load JSON config for MIDI commands, implements simple methods """

    def __init__(self):
        super().__init__()
        self._sounds: Dict[str, List[int]] = load_sounds(load_midi=True)
        self.max_volume = max_volume_midi(self._sounds)
        self._load_all()
        if os.name != "posix":
            self._out_port = MockMidiPort()
        else:
            port_name = os.getenv('CLOCK_PORT_NAME', "DrumClock_in")
            self._out_port, _ = open_midioutput(port_name, interactive=False)

    def prepare_drum(self, length: int) -> None:
        if not length:
            return
        self._length = length
        self._bpm = bpm_from_length(length)
        self._prepare_all(length)

    def _prepare_one(self, pattern, length: int) -> Any:
        accents = pattern["acc"]
        result: Dict[int, List[List[int]]] = dict()
        for sound_name in [x for x in self._sounds if x in pattern]:
            notes = pattern[sound_name]
            steps = len(notes)
            if notes.count("!") + notes.count(".") != steps:
                LOGGER.error(f"sound {sound_name} notes {notes} must contain only '.' and '!'")

            step_len = length // steps
            sound: List[int] = self._sounds[sound_name]
            assert type(sound) == list
            assert len(sound) == 3
            for step_number in range(steps):
                if notes[step_number] != '.':
                    step_accent = int(accents[step_number])
                    step_volume = int(step_accent / 9 * self._volume * 127)
                    assert step_volume <= 127
                    pos = position_with_swing(length, step_number, step_len, self._swing, self._shift)
                    sound[2] = step_volume
                    lst = result.get(pos, list())
                    lst.append(sound)
                    result[pos] = lst
        return result


if __name__ == "__main__":
    def test():
        import time
        loader = MiLoader()
        loader.prepare_drum(100_000)
        while loader.get_length() == 0:
            time.sleep(0.1)

        print(f"loader: {loader}")
        print(f"pattern: {loader._snd_l1}")


    test()
