from abc import abstractmethod

import numpy as np


# noinspection PyMethodMayBeStatic
class FakeDrum:

    def get_item(self) -> str:
        return ""

    @abstractmethod
    def get_fixed(self) -> str:
        return ""

    def set_fixed(self, fixed: str) -> None:
        pass

    def get_str(self) -> str:
        return ""

    def iterate(self, go_fwd: bool) -> None:
        pass

    def clear_drum(self) -> None:
        pass

    @abstractmethod
    def get_length(self) -> int:
        return 0

    def random_samples(self) -> None:
        pass

    def load_drum_type(self) -> None:
        pass

    @abstractmethod
    def prepare_drum(self, length: int) -> None:
        pass

    # ================

    def change_volume(self, change_factor: float) -> None:
        pass

    def change_swing(self, change_steps: int) -> None:
        pass

    def get_volume(self) -> float:
        return 0

    def get_swing(self) -> float:
        return 0

    @abstractmethod
    def play_samples(self, out_data: np.ndarray, idx: int) -> None:
        pass

    def play_break_later(self, part_len: int, idx: int) -> None:
        pass

    def play_break_now(self, bars: float = 0) -> None:
        pass

    def change_intensity(self, change_by: int) -> None:
        pass
