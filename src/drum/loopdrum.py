import numpy as np

from drum.basedrum import BaseDrum
from song.songpart import SongPart


class LoopDrum(BaseDrum):
    """ Drum using song part as it's base.
    The part will record real drum sounds and play along with all other parts """

    def __init__(self, part: SongPart):
        BaseDrum.__init__(self)
        self._part: SongPart = part

    def get_config(self) -> str:
        return ""

    def get_id(self) -> int:
        return id(self._part)

    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        self._part.play_samples(out_data, idx)

    def random_drum(self) -> None:
        loops = self._part.loops
        lst = list(range(self._part.loops.item_count()))
        lp_count = min(len(lst), 1 + self._drum_level)  # play 1, 2, 3 loops for drum_level 0, 1, 2
        lst = np.random.choice(lst, lp_count, replace=False)
        lst = [loops.select_idx(k) for k in lst]
        self._part.loops.apply_to_each(lambda x: x.set_silent(x not in lst))

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
