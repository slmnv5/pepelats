import logging
from abc import ABC
from typing import Dict, Any
from typing import List

import numpy as np
import rtmidi

from drum._utildrum import load_midi, max_volume_midi
from drum._utildrum import position_with_swing
from drum.basedrum import ProtoDrum, SimpleDrum


class LoadDrumMidi(SimpleDrum, ABC):
    """ Load JSON config for MIDI commands """

    def __init__(self, out_port: rtmidi.MidiOut):
        SimpleDrum.__init__(self)
        self._sounds: Dict[str, List[int]] = load_midi()
        self.max_volume = max_volume_midi(self._sounds)
        self._load_all()
        self._out_port: rtmidi.MidiOut = out_port

    def close_port(self):
        self._out_port.close_port()

    def _prepare_one(self, pattern, length: int) -> Any:
        # logging.debug(f"Preapring pattern: {pattern}")
        accents = pattern["acc"]
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


class MidiDrum(LoadDrumMidi):
    """ MIDI Drum version sending configurable MIDI messages and sysex """

    def __init__(self, out_port):
        LoadDrumMidi.__init__(self, out_port)

    def __play_midi_pattern(self, pattern: Dict[int, List[List[int]]], pos1: int, pos2: int) -> None:
        for msg_lst in [pattern[x] for x in pattern if pos1 <= x < pos2]:
            for msg in msg_lst:
                self._out_port.send_message(msg)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._intensity == ProtoDrum._MUTE or not self._length:
            return

        pos1 = idx % self._length
        pos2 = pos1 + len(out_data)
        if self._intensity == ProtoDrum._LEVEL1:
            self.__play_midi_pattern(self._l1, pos1, pos2)
        elif self._intensity == ProtoDrum._LEVEL2:
            self.__play_midi_pattern(self._l2, pos1, pos2)
        elif self._intensity == ProtoDrum._BREAK:
            self.__play_midi_pattern(self._bk, pos1, pos2)

    def __str__(self):
        return f"MIDI: {self._out_port.__class__.__name__} {self._name} {self._bpm:.2F}"


if __name__ == "__main__":
    def test():
        from utils.utilport import FakeOutPort

        from buffer import LoopSimple
        from buffer._oneloopctrl import OneLoopCtrl
        from threading import Timer
        from utils.utilalsa import make_sin_sound
        from time import sleep

        logging.basicConfig(level=logging.DEBUG)
        ctrl = OneLoopCtrl(MidiDrum(FakeOutPort()))
        drum = ctrl.get_drum()

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
