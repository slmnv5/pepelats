from random import randrange, random, sample

import numpy as np

from buffer.wrapbuffer import WrapBuffer
from drum.basedrum import BaseDrum
from song.songpart import SongPart


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The song part will record real drum sounds and play along with other parts.
    Loop #0 always plays, other loops may be added randomly if drum level > 0
    Random shift is applied to drum loops """

    def __init__(self, part: SongPart):
        BaseDrum.__init__(self)
        self._rand_shift: int = 0  # shift by 1/4 of bar
        self._shift_idx: int = 0
        self._play_lst: list[WrapBuffer] = list()  # list of loops in song part to play
        self._stopped: bool = True
        self._part: SongPart = part

    def play_samples(self, buff: WrapBuffer) -> bool:
        return id(self._part) != id(buff)

    def get_config(self) -> str:
        return ""

    def get_id(self) -> int:
        return id(self._part)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        if not self._bar_len or self._stopped:
            return
        if idx % self._bar_len == 0:
            if random() < self._par:
                self.random_drum()
        for lp in self._play_lst:
            WrapBuffer.play_samples(lp, out_data, idx + self._shift_idx)

    def random_drum(self) -> None:
        self._rand_shift = randrange(4)
        self._shift_idx = round(self._rand_shift * self.get_bar_len() / 4)
        self._stopped = False
        loops = self._part.loops
        save_idx: int = loops.idx()
        lp_count: int = loops.item_count()
        # play 1 or 2 random loops in addition to loop #0
        lp_add = min(lp_count - 1, self._drum_level)
        lst = sample(list(range(lp_count))[1:], lp_add)
        lst.append(0)
        self._play_lst.clear()
        for k in lst:
            self._play_lst.append(loops.set_idx(k))
        loops.set_idx(save_idx)

    def load_drum_config(self, config: str = None, bar_len: int = None) -> None:
        self.stop_drum()
        bar_len = self._bar_len if bar_len is None else bar_len
        self._set_bar_len(bar_len)
        self.start_drum()

    def iterate_drum_config(self, steps: int) -> None:
        pass

    def show_drum_config(self) -> str:
        return ""

    def stop_drum(self) -> None:
        self._stopped = True

    def start_drum(self) -> None:
        self.random_drum()

    def get_drum_header(self) -> str:
        return super().get_drum_header() + f":shft{self._rand_shift}"

    def show_drum_param(self) -> str:
        return super().show_drum_param()
