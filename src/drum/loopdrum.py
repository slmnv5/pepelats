from random import random, choices
from threading import Timer

import numpy as np

from drum.basedrum import BaseDrum
from song.songpart import SongPart
from song.wrapbuffer import WrapBuffer
from utils.util_audio import AUDIO_INFO


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The song part will record real drum sounds and play along with other parts.
    The last loops is used only for drum fills.
    Other loops selected randomly.
    How often loops are randomized is proportional to self._param
    """

    def __init__(self, song_part: SongPart):
        BaseDrum.__init__(self)
        self._song_part: SongPart = song_part
        self._param = 0.2  # for this drum - probability to randomize at bar start

    def randomize(self) -> None:
        """ Randomly modify drum by excluding some sounds """
        loops = self._song_part.loops
        count: int = loops.item_count()
        exclude_lst = choices(range(count), k=(count // 3))
        loops.for_each(lambda x: x.set_silent(loops.add_item(x) in exclude_lst))
        loops.select_idx(-1).set_silent(True)
        self.start()

    def play_fill(self) -> None:
        if not self._bar_len:
            return
        loops = self._song_part.loops
        loops.select_idx(-1).set_silent(False)
        # return to normal drums
        Timer(self._bar_len / AUDIO_INFO.SD_RATE, self.randomize).start()

    def play(self, out_data: np.ndarray, idx: int) -> None:
        if self._is_stopped:
            return
        if idx % self._bar_len == 0 and random() < self._param:
            self.randomize()
        self._song_part.play(out_data, idx)

    def set_volume(self, volume: float) -> None:
        def chg_vol(x: WrapBuffer) -> None:
            np.multiply(x, volume / 0.5, out=x, casting="unsafe")

        super().set_volume(volume)
        loops = self._song_part.loops
        loops.for_each(lambda x: chg_vol(x))
