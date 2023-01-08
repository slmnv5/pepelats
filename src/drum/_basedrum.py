import logging
from threading import Timer
from typing import Dict, Any
from typing import List

from drum._utildrum import load_all_patterns
from utils.utilconfig import ENV_SD_RATE
from utils.utilother import FileFinder


# noinspection PyMethodMayBeStatic
class BaseDrum(FileFinder):
    """ Prototype or interface, default implemFentation of somes methods """

    _MUTE = 0
    _LEVEL1 = 1
    _LEVEL2 = 2
    _BREAK = 3

    def __init__(self):
        FileFinder.__init__(self, "config/drum", False, "")
        self._length: int = 0
        self._bpm: float = 0
        self._ptn_l1: List[Dict[str, Any]] = []
        self._ptn_l2: List[Dict[str, Any]] = []
        self._ptn_bk: List[Dict[str, Any]] = []
        self._intensity: int = BaseDrum._MUTE
        self._is_break_pending: bool = False
        self._name: str = self.get_item()

    def clear_drum(self) -> None:
        self._length = 0
        self._bpm = 0
        self._intensity = BaseDrum._MUTE

    def get_length(self) -> int:
        return self._length

    def randomize(self):
        pass

    def _char2float(self, char: str) -> float:
        try:
            ch = "9" if char[0] == "!" else char[0]
            return int(ch) / 9.0
        except (ValueError, IndexError):
            return 0.0

    def _load_all(self) -> None:
        directory: str = self.get_full_name()
        lst1 = ["drum_level1", "drum_level2", "drum_break"]
        lst2 = [self._ptn_l1, self._ptn_l2, self._ptn_bk]
        for k in range(3):
            logging.info(f"Loaded patterns from directory: {directory}/{lst1[k]}")
            load_all_patterns(directory, lst1[k], lst2[k])

    def load_drum_name(self, drum_name: str) -> None:
        if self._name == drum_name:
            return
        self.set_id(self.find_item(drum_name))
        self._name = self.get_item()
        self._load_all()

    def change_intensity(self, change_by: int) -> None:
        if not self._length:
            return
        change_by = (1 if change_by > 0 else -1)
        self._intensity += change_by
        self._intensity %= (BaseDrum._BREAK + 1)

    def play_break_now(self) -> None:
        if not self._length:
            return

        if self._intensity == BaseDrum._MUTE:
            self._intensity = BaseDrum._LEVEL1

        save_int = self._intensity

        def revert():
            self._intensity = save_int
            self._is_break_pending = False

        self.randomize()
        self._intensity = BaseDrum._BREAK
        Timer((self._length // 2) / ENV_SD_RATE, revert).start()

    def play_break_later(self, part_len: int, idx: int) -> None:
        if self._is_break_pending:
            return
        samples = self._length // 2
        idx %= part_len
        start_at = (part_len - idx) - samples
        if start_at > 0:
            self._is_break_pending = True
            Timer(start_at / ENV_SD_RATE, self.play_break_now).start()


if __name__ == "__main__":
    pass
