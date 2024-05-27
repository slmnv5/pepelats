import numpy as np

from drum.basedrum import BaseDrum


class SilentDrum(BaseDrum):
    """ Drum that does nothing """

    def __init__(self):
        BaseDrum.__init__(self)

    def get_config(self) -> str:
        return ""

    def set_config(self, config: str = None) -> None:
        pass

    def play(self, out_data: np.ndarray, idx: int) -> None:
        pass

    def randomize(self) -> None:
        pass

    def play_fill(self, idx: int) -> None:
        pass

    def show_config(self) -> str:
        return ""

    def iterate_config(self, steps: int) -> None:
        pass

    def show_param(self) -> str:
        return ""
