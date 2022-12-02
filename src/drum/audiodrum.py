from time import sleep

import numpy as np

from drum.basedrum import ProtoDrum, LoadDrum
from utils.utilalsa import play_sound_buff


class AudioDrum(LoadDrum):
    """Play drums generated from patterns, change patterns and intencity """

    def __init__(self):
        LoadDrum.__init__(self)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if self._intensity == ProtoDrum._MUTE or not self._length:
            return

        if self._intensity == ProtoDrum._BREAK:
            play_sound_buff(self._bk, out_data, idx)
        elif self._intensity == ProtoDrum._LEVEL1:
            play_sound_buff(self._l1, out_data, idx)
        elif self._intensity == ProtoDrum._LEVEL2:
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
