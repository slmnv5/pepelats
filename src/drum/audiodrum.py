from time import sleep

import numpy as np

from drum._auloader import AuLoader
from drum._utildrum import Intensity
from utils.utilalsa import play_sound_buff


class AudioDrum(AuLoader):
    """Play drums generated from patterns, change patterns and intencity """

    def __init__(self):
        AuLoader.__init__(self)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._intensity == Intensity.SILENT or not self._length:
            return

        if self._intensity & Intensity.BREAK:
            play_sound_buff(self._bk, out_data, idx)
            return
        if self._intensity & Intensity.LVL1:
            play_sound_buff(self._l1, out_data, idx)
        if self._intensity & Intensity.LVL2:
            play_sound_buff(self._l2, out_data, idx)

    def __str__(self):
        return f"{self._file_finder.get_fixed()} {self._bpm:.2F}"


if __name__ == "__main__":
    def test():
        from buffer import LoopSimple
        from loopctrl import OneLoopCtrl
        from threading import Timer
        from utils.utilalsa import make_sin_sound

        drum = AudioDrum()
        drum.load_drum_type()
        drum.prepare_drum(100_000)
        sound = make_sin_sound(440, 7.1)
        while not drum._length:
            sleep(0.1)

        print(f"==============>{drum}")
        ctrl = OneLoopCtrl(drum)
        loop = LoopSimple(ctrl)
        loop._record_samples(sound, 0)
        ctrl.idx = len(sound)
        print("======== start =============")
        loop.trim_buffer()
        Timer(5, ctrl.stop_at_bound, [0]).start()
        loop.play_buffer()
        drum.clear_drum()


    test()
