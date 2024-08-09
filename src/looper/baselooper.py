from abc import ABC

from drum.basedrum import BaseDrum
from utils.util_drum import drum_create


class BaseLooper(ABC):
    """class to control one loop playback, has drum"""

    def __init__(self):
        self._drum: BaseDrum = BaseDrum()

    # drum methods

    def _drum_create(self, bar_len: int, drum_info: dict) -> None:
        self._drum.stop()
        self._drum = drum_create(bar_len, drum_info)
        self._drum.start()

    def _drum_next_config(self) -> None:
        self._drum.get_next_config()

    def _drum_prev_config(self) -> None:
        self._drum.get_prev_config()

    def _drum_show_config(self) -> str:
        return self._drum.get_config(True)

    def _drum_change_param(self, chg: float) -> None:
        self._drum.set_param(self._drum.get_param() + chg)

    def _drum_change_volume(self, chg: float) -> None:
        self._drum.set_volume(self._drum.get_volume() * chg)

    def _drum_show_param(self) -> str:
        return self._drum.show_param()

    def _drum_randomize(self) -> None:
        self._drum.randomize()

    def _drum_play_fill(self) -> None:
        self._drum.play_fill()

    def _drum_stop(self) -> None:
        self._drum.stop()

    def _drum_set_config(self, config: str = None) -> None:
        self._drum.set_config(config)
