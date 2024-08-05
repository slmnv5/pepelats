from abc import ABC, abstractmethod

from drum.basedrum import BaseDrum


class LoopCtrl(ABC):
    """class to control one loop playback, has drum"""

    def __init__(self):
        self._drum: BaseDrum = BaseDrum()

    # noinspection PyMethodMayBeStatic

    @abstractmethod
    def _update_view(self) -> None:
        pass

    @abstractmethod
    def drum_create_async(self, bar_len: int, drum_info: dict) -> None:
        pass

    # drum methods

    def _drum_iterate_config(self, steps: int) -> None:
        self._drum.iterate_config(steps)

    def _drum_show_config(self) -> str:
        return self._drum.get_config(True)

    def _drum_set_param(self, chg: float) -> None:
        chg = 0.2 if chg > 0 else -0.2
        self._drum.set_param(self._drum.get_param() + chg)

    def _drum_set_volume(self, chg: float) -> None:
        volume = self._drum.get_volume()
        volume *= (1.2 if chg > 0 else 0.83)
        self._drum.set_volume(volume)

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
