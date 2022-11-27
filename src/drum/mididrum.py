from time import sleep
from typing import List, Dict


import numpy as np

from drum._miloader import MiLoader
from drum._utildrum import Intensity


class MidiDrum(MiLoader):
    """ MIDI Drum version sending configurable MIDI messages and sysex """

    def __init__(self, ):
        super().__init__()

    def __play_midi_pattern(self, pattern: Dict[int, List[List[int]]], pos1: int, pos2: int) -> None:
        for msg_lst in [pattern[x] for x in pattern if pos1 <= x < pos2]:
            for msg in msg_lst:
                self._out_port.send_message(msg)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._intensity == Intensity.SILENT or not self._length:
            return

        pos1 = idx % self._length
        pos2 = pos1 + len(out_data)
        if self._intensity & Intensity.LVL1:
            self.__play_midi_pattern(self._l1, pos1, pos2)
        if self._intensity & Intensity.LVL2:
            self.__play_midi_pattern(self._l2, pos1, pos2)
        if self._intensity & Intensity.BREAK:
            self.__play_midi_pattern(self._bk, pos1, pos2)

    def __str__(self):
        return f"{self._file_finder.get_fixed()} {self._bpm:.2F}"


if __name__ == "__main__":
    def test():
        from buffer import LoopSimple
        from loopctrl import OneLoopCtrl
        from threading import Timer
        from utils.utilalsa import make_sin_sound

        drum = MidiDrum()
        drum.load_drum_type()
        drum.prepare_drum(100_000)
        print(f"==============>{drum}")
        sound = make_sin_sound(440, 7.1)
        while not drum.get_length():
            sleep(0.1)

        ctrl = OneLoopCtrl(drum)
        loop = LoopSimple(ctrl)
        loop._record_samples(sound, 0)
        ctrl.idx = len(sound)
        print("======== start =============")
        loop.trim_buffer()
        Timer(50, ctrl.stop_at_bound, [0]).start()
        loop.play_buffer()
        drum.clear_drum()


    test()
