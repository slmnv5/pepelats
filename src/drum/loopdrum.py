from random import randrange

import numpy as np

from drum.basedrum import BaseDrum
from song.songpart import SongPart


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The part will record real drum sounds and play along with parts 1, 2 based on drum level
    self._rand_shift = self._bar_len * randrange(4) is applied """

    def __init__(self, part: SongPart):
        BaseDrum.__init__(self)
        self._rand_shift: int = 0
        self._part: SongPart = part

    def get_config(self) -> str:
        return ""

    def get_id(self) -> int:
        return id(self._part)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        self._part.play_samples(out_data, idx + self._rand_shift)

    def random_drum(self) -> None:
        self._rand_shift = self._bar_len * randrange(4)
        loops = self._part.loops
        lst: list[int] = list(range(1, loops.item_count()))
        lp_count = self._drum_level  # play 0, 1 or 2 loops in addition to loop zero
        lp_count = min(lp_count, len(lst))
        lst = np.random.choice(lst, lp_count, replace=False).tolist()
        lst.append(0)
        for k in range(loops.item_count()):
            lp = loops.select_idx(k)
            lp.set_silent(k not in lst)

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
        self._part.loops.apply_to_each(lambda x: x.set_silent(True))

    def start_drum(self) -> None:
        self.random_drum()

    def get_drum_header(self) -> str:
        lp_lst: list[str] = list()
        loops = self._part.loops
        loops.apply_to_each(lambda x: lp_lst.append("S" if x.is_silent else "_"))
        return super().get_drum_header() + ":" + "".join(lp_lst)

    def show_drum_param(self) -> str:
        return ""
