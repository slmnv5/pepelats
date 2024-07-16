from basic.audioinfo import AudioInfo
from utils.utilother import HUGE_INT


class DrawInfo:
    def __init__(self):
        self._UPDATES_PER_LOOP: int = 16
        self.update_method: str = ""
        self.header: str = ""
        self.description: str = ""
        self.content: str = ""
        self.part_len: int = HUGE_INT
        self.max_loop_len: int = HUGE_INT
        self.idx: int = 0
        self.is_rec: bool = False

        self.max_factor: float = 1.0
        self.part_delta: float = 0.0
        self.max_delta: float = 0.0
        self.sleep: float = 1.0
        self.pos: float = 0
        self.max_pos: float = 0

    def recalculate(self) -> None:
        self.pos = (self.idx % self.part_len) / self.part_len
        self.max_factor = self.max_loop_len / self.part_len
        self.max_pos = (self.idx % self.max_loop_len) / self.max_loop_len
        self.part_delta = self.part_len / self._UPDATES_PER_LOOP
        self.max_delta = self.part_delta / self.max_factor
        self.sleep = self.part_len / AudioInfo().SD_RATE / self._UPDATES_PER_LOOP
