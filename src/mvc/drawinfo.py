import json

from basic.audioinfo import AudioInfo
from utils.utilother import HUGE_INT


class DrawInfo:
    def __init__(self):
        self._UPDATES_PER_LOOP: int = 16
        self._RATE = AudioInfo().SD_RATE
        self.update_method: str = ""
        self.header: str = ""
        self.description: str = ""
        self.content: str = ""

        self.idx: int = 0
        self.is_rec: bool = False
        self.part_len: int = HUGE_INT
        self.max_loop_len: int = HUGE_INT
        self.sleep: float = 1.0

    def to_json(self) -> str:
        return json.dumps(self, default=vars)

    def get_sleep_tm(self) -> float:
        return self.part_len / self._RATE / self._UPDATES_PER_LOOP

    def get_dict(self) -> dict[str, float]:
        dic = dict()
        self.idx += self.part_len / self._UPDATES_PER_LOOP
        dic["pos"] = (self.idx % self.part_len) / self.part_len
        if self.max_loop_len > self.part_len:
            dic["max_loop_pos"] = (self.idx % self.max_loop_len) / self.max_loop_len
        else:
            dic["max_loop_pos"] = -1
        return dic
