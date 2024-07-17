import json

from basic.audioinfo import AudioInfo


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
        self.len: int = 100_000
        self.max_loop_len: int = 100_000
        self.sleep: float = 1.0

    def to_json(self) -> str:
        tmp: dict[str, any] = self.get_dict()
        return json.dumps(tmp)

    def get_dict(self) -> dict[str, any]:
        tmp: dict[str, any] = dict()
        tmp["sleep_tm"] = self.len / self._RATE / self._UPDATES_PER_LOOP
        tmp["header"] = self.header
        tmp["description"] = self.description
        tmp["content"] = self.content
        tmp["is_rec"] = self.is_rec
        tmp["pos"] = (self.idx % self.len) / self.len
        tmp["delta"] = 1 / self._UPDATES_PER_LOOP
        if self.max_loop_len > self.len:
            tmp["max_loop_pos"] = (self.idx % self.max_loop_len) / self.max_loop_len
            tmp["max_loop_delta"] = 1 / self._UPDATES_PER_LOOP / self.max_loop_len * self.len
        else:
            tmp["max_loop_pos"] = 0
            tmp["max_loop_delta"] = 0
        return tmp
