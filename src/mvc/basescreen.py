from multiprocessing import Queue

from basic.audioinfo import AudioInfo
from mvc.menuclient import MenuClient
from utils.utilother import DrawInfo


class BaseScreen(MenuClient):
    def __init__(self, q: Queue):
        MenuClient.__init__(self, q)
        self.updates_per_loop: float = 16.0
        self.di: DrawInfo = DrawInfo()
        self._pos: float = 0
        self._max_pos: float = 0
        self._max_factor: float = 1.0
        self._delta: float = 1.0 / self.updates_per_loop
        self._delta_max: float = self._delta
        self._sleep: float = 10.0

    def _client_redraw(self, di: DrawInfo) -> None:
        self.di = di
        self._pos = (di.idx % di.part_len) / di.part_len
        self._max_factor = di.max_loop_len / di.part_len
        self._max_pos = (di.idx % di.max_loop_len) / di.max_loop_len
        self._delta_max = self._delta / self._max_factor
        self._sleep = di.part_len / AudioInfo().SD_RATE / self.updates_per_loop
