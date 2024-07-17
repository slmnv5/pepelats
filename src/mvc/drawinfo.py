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
        self.len: int = HUGE_INT
        self.max_loop_len: int = HUGE_INT
        self.sleep: float = 1.0

    def to_json(self) -> str:
        tmp: dict[str, float | str] = self.get_dict()
        tmp["sleep_tm"] = self.get_sleep_tm()
        tmp["header"] = self.header
        tmp["description"] = self.description
        tmp["content"] = self.content

        return json.dumps(tmp)

    def get_sleep_tm(self) -> float:
        return self.len / self._RATE / self._UPDATES_PER_LOOP

    def get_dict(self) -> dict[str, float]:
        tmp: dict[str, float] = dict()
        self.idx += self.len / self._UPDATES_PER_LOOP
        tmp["pos"] = (self.idx % self.len) / self.len
        tmp["delta"] = 1 / self._UPDATES_PER_LOOP
        if self.max_loop_len > self.len:
            tmp["max_loop_pos"] = (self.idx % self.max_loop_len) / self.max_loop_len
            tmp["max_loop_delta"] = 1 / self._UPDATES_PER_LOOP / self.max_loop_len * self.len
        else:
            tmp["max_loop_pos"] = -1
            tmp["max_loop_delta"] = 0
        return tmp
