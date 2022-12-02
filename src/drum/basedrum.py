import random
from abc import ABC
from abc import abstractmethod
from threading import Timer
from typing import Dict, Any
from typing import List

import numpy as np

from drum._utildrum import load_all_patterns, bpm_from_length
from drum._utildrum import load_audio, max_volume_audio, position_with_swing
from utils.config import SD_RATE
from utils.log import LOGGER
from utils.utilalsa import make_zero_buffer, record_sound_buff, SD_TYPE
from utils.utilother import FileFinder


# noinspection PyMethodMayBeStatic
class ProtoDrum:
    """ Prototype or interface, default implemFentation of somes methods """

    _MUTE = 0
    _LEVEL1 = 1
    _LEVEL2 = 2
    _BREAK = 3

    def __init__(self):
        self._file_finder = FileFinder("config/drum", False, "")
        self._length: int = 0
        self._bpm: float = 0
        self._sounds: Dict = dict()
        self._ptn_l1: List[Dict[str, Any]] = []
        self._ptn_l2: List[Dict[str, Any]] = []
        self._ptn_bk: List[Dict[str, Any]] = []
        self._intensity: int = ProtoDrum._LEVEL1
        self._is_break_pending: bool = False

    def clear_drum(self) -> None:
        self._length = 0
        self._bpm = 0

    def get_item(self) -> str:
        return self._file_finder.get_item()

    def set_fixed(self, fixed: str) -> None:
        return self._file_finder.set_fixed(fixed)

    def get_str(self) -> str:
        return self._file_finder.get_str()

    def iterate(self, go_fwd: bool) -> None:
        return self._file_finder.iterate(go_fwd)

    def get_length(self) -> int:
        return self._length

    @abstractmethod
    def play_drums(self, out_data: np.ndarray, idx: int) -> None:
        pass

    @abstractmethod
    def prepare_drum(self, length: int) -> None:
        pass

    def _randomize(self):
        pass

    def _load_all(self) -> None:
        directory: str = self._file_finder.get_full_name()
        lst1 = ["drum_level1", "drum_level2", "drum_break"]
        lst2 = [self._ptn_l1, self._ptn_l2, self._ptn_bk]
        for k in range(3):
            LOGGER.info(f"Loaded patterns from directory: {directory}, file: {lst1[k]}")
            load_all_patterns(directory, lst1[k], lst2[k], [*self._sounds])

    def load_drum_type(self) -> None:
        self._file_finder.set_fixed(self._file_finder.get_item())
        self._load_all()
        if self._length:
            self.prepare_drum(self._length)

    def change_intensity(self, change_by: int) -> None:
        i = self._intensity + change_by
        i = 0 if i > 3 else i
        i = 3 if i < 0 else i
        self._intensity = i

    def play_break_now(self) -> None:
        if self._intensity == ProtoDrum._MUTE:
            self._intensity = ProtoDrum._LEVEL1

        def revert():
            self._intensity = ProtoDrum._LEVEL1
            self._is_break_pending = False

        self._randomize()
        self._intensity = ProtoDrum._BREAK
        Timer((self._length // 2) / SD_RATE, revert).start()

    def play_break_later(self, part_len: int, idx: int) -> None:
        if self._is_break_pending:
            return
        samples = self._length // 2
        idx %= part_len
        start_at = (part_len - idx) - samples
        if start_at > 0:
            self._is_break_pending = True
            Timer(start_at / SD_RATE, self.play_break_now).start()


class SimpleDrum(ProtoDrum, ABC):
    """ load drum patterns, drum sounds, genrate audio bufferes with
    drum tracks using volume and swing parameters """

    def __init__(self):
        ProtoDrum.__init__(self)
        self._volume: float = 1.0  # from 0 to 1
        self._max_volume: float = 1.0  # from 0 to 1
        self._swing: float = 0.75

        self._l1 = self._l2 = self._bk = []
        self._snd_l1 = []
        self._snd_l2 = []
        self._snd_bk = []

    def prepare_drum(self, length: int) -> None:
        if not length:
            return
        self._length = 0  # keep it zero until sound load is done
        self._bpm = bpm_from_length(length)
        self._snd_l1 = [self._prepare_one(p, length) for p in self._ptn_l1]
        self._snd_l2 = [self._prepare_one(p, length) for p in self._ptn_l2]
        self._snd_bk = [self._prepare_one(p, length) for p in self._ptn_bk]
        self._l1 = self._l2 = self._bk = self._snd_l1[0]
        self._length = length

    def _prepare_one(self, pattern, length: int) -> Any:
        pass

    def change_volume(self, change_factor: float) -> None:
        self._volume = round(self._volume * change_factor, 2)
        self._volume = min(1.0, self._volume)
        self._volume = max(0.03, self._volume)
        self.prepare_drum(self._length)

    def change_swing(self, change_by: float) -> None:
        self._swing += change_by
        if self._swing > 0.75:
            self._swing = 0.5
        elif self._swing < 0.5:
            self._swing = 0.75
        self.prepare_drum(self._length)

    def show_drum_param(self) -> str:
        return f"Drum parameters:\nvolume(0.0-1.0):{self._volume:.2F}\n" \
               f"swing(0.5-0.75):{self._swing:.2F}"

    def _randomize(self):
        self._l2 = random.choice(self._snd_l2)
        self._l1 = random.choice(self._snd_l1)
        self._bk = random.choice(self._snd_bk)

    def __str__(self):
        return f"{self.__class__.__name__} " \
               f"patterns: {len(self._ptn_l1)}/{len(self._ptn_l2)}/{len(self._ptn_bk)}" \
               f", sounds: {len(self._snd_l1)}/{len(self._snd_l2)}/{len(self._snd_bk)}"


class LoadDrum(SimpleDrum, ABC):
    """ class to load drum patterns, drum sounds, generate audio bufferes with
    drum tracks using volume and swing parameters """

    def __init__(self):
        SimpleDrum.__init__(self)
        self._sounds: Dict[str, np.ndarray] = load_audio()
        self.max_volume: float = max_volume_audio(self._sounds)
        self._load_all()

    def _prepare_one(self, pattern, length: int) -> Any:
        LOGGER.debug(f"Preapring pattern: {pattern}")
        accents = pattern["acc"]
        result: np.ndarray = make_zero_buffer(length)
        for sound_name in [x for x in self._sounds if x in pattern]:
            notes = pattern[sound_name]
            steps = len(notes)
            if notes.count("!") + notes.count(".") != steps:
                LOGGER.error(f"sound {sound_name} notes {notes} must contain only '.' and '!'")

            step_len = length // steps
            sound: np.ndarray = self._sounds[sound_name]
            sound = sound[:length]
            assert sound.ndim == 2 and sound.shape[1] == 2
            assert 0 < sound.shape[0] <= length, f"Must be: 0 < {sound.shape[0]} <= {length}"

            for step_number in range(steps):
                if notes[step_number] != '.':
                    step_accent = int(accents[step_number])
                    step_volume = step_accent / 9 * self._volume
                    pos = position_with_swing(step_number, step_len, self._swing)
                    tmp = (sound * step_volume).astype(SD_TYPE)
                    record_sound_buff(result, tmp, pos)

        return result


if __name__ == "__main__":
    def test():
        import time
        LOGGER.setLevel("DEBUG")
        loader = LoadDrum()
        loader.prepare_drum(100_000)
        while loader.get_length() == 0:
            time.sleep(0.1)

        print(f"loader: {loader}")


    test()
