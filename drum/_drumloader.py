import os
import random
from pathlib import Path
from typing import List, Any, Dict, Union, Tuple

import numpy as np
import soundfile as sf

import logging
from utils import JsonDict, make_zero_buffer, record_sound_buff, SD_TYPE, ConfigName, FileFinder
from utils import SD_MAX


def extend_list(some_list: Union[List, str], new_len: int) -> List:
    """replicate or shrink list or string to a new length"""
    k = -(-new_len // len(some_list))
    return (some_list * k)[:new_len]


def position_with_swing(step_number: int, step_len: int, swing: float) -> int:
    """shift every even 16th note to make it swing like"""
    if step_number % 2 == 0:
        return round(step_number * step_len)
    else:
        swing_delta: float = step_len * (swing - 0.5)
        return round(step_number * step_len + swing_delta)


class DrumLoader:
    """ class to load drum patterns """

    def __init__(self):
        self._file_finder = FileFinder("config/drums", False, "")
        self.volume: int = 70
        self.swing: float = 0.75
        self.max_volume: float = 0
        self.__length: int = 0
        self.__sounds: Dict[str, Tuple[np.ndarray, float]] = dict()
        self.l1: np.ndarray = np.empty(shape=[0, 2])
        self.l2: np.ndarray = np.empty(shape=[0, 2])
        self.bk: np.ndarray = np.empty(shape=[0, 2])
        self.__ptn_l1: List[Dict[str, Any]] = []
        self.__ptn_l2: List[Dict[str, Any]] = []
        self.__ptn_bk: List[Dict[str, Any]] = []
        self.__snd_l1: List[np.ndarray] = []
        self.__snd_l2: List[np.ndarray] = []
        self.__snd_bk: List[np.ndarray] = []
        self.__load()

    def get_item(self) -> str:
        return self._file_finder.get_item()

    def get_fixed(self) -> str:
        return self._file_finder.get_fixed()

    def set_fixed(self, fixed: str) -> None:
        return self._file_finder.set_fixed(fixed)

    def get_str(self) -> str:
        return self._file_finder.get_str()

    def iterate(self, go_fwd: bool) -> None:
        return self._file_finder.iterate(go_fwd)

    def clear_drum(self) -> None:
        self.__length = 0

    def get_length(self) -> int:
        return self.__length

    def random_samples(self):
        self.l2 = random.choice(self.__snd_l2)
        self.l1 = random.choice(self.__snd_l1)
        self.bk = random.choice(self.__snd_bk)

    def load_drum_type(self) -> None:
        self._file_finder.set_fixed(self._file_finder.get_item())
        self.__load()
        if self.get_length():
            self.prepare_drum(self.get_length())

    def __load(self) -> None:
        directory: str = self._file_finder.get_full_name()
        logging.info(f"Loading drum {directory}")
        if len(self.__sounds) == 0:
            self.__load_sounds(directory)
            logging.info(f"Loaded drum sounds {len(self.__sounds)}")
        self.__load_all_patterns(directory, "drum_level1", self.__ptn_l1)
        self.__load_all_patterns(directory, "drum_level2", self.__ptn_l2)
        self.__load_all_patterns(directory, "drum_break", self.__ptn_bk)
        logging.info(f"Loaded drum patterns {len(self.__ptn_l1)}")

    def __load_sounds(self, directory: str) -> None:
        """Loads WAV sounds"""
        path = os.path.join(Path(directory).parent, "drum_sounds.json")
        loader = JsonDict(path)
        for name in loader.dic():
            drum_sound = loader.get(name, dict())
            assert len(drum_sound) > 0
            assert type(drum_sound) == dict
            file_name = Path(loader.get_dir(), drum_sound["file_name"])
            sound_volume: float = drum_sound.get("volume", 1.0)

            (sound, _) = sf.read(str(file_name), dtype="int16", always_2d=True)
            assert sound.ndim == 2
            assert sound.shape[1] == 2
            array_max: float = np.max(sound)
            self.max_volume = max(self.max_volume, sound_volume * array_max)
            assert self.max_volume < SD_MAX
            #  logging.info(f"Loaded sound {file_name}")
            self.__sounds[name] = (sound, sound_volume)

    def __load_all_patterns(self, directory: str, file_name: str, storage: List[Dict]) -> None:
        storage.clear()
        path = os.path.join(directory, file_name + ".json")
        loader = JsonDict(path)
        default = loader.get(ConfigName.default_pattern, dict())
        for key in [x for x in loader.dic() if x not in [ConfigName.comment, ConfigName.default_pattern]]:
            value = loader.get(key, None)
            assert type(value) == dict, f"Must be dictionary {key}"
            assert len(value) > 0, f"Dictionary must be non empty {key}"
            value = dict(default, **value)
            value["name"] = key
            value["acc"] = extend_list(value["acc"], value["steps"])
            for sound_name in [x for x in self.__sounds if x in value]:
                value[sound_name] = extend_list(value[sound_name], value["steps"])
            storage.append(value)

    def prepare_drum(self, length: int) -> None:
        self.__length = 0  # keep it zero until sound load is done

        for i in [self.__snd_l1, self.__snd_l2, self.__snd_bk]:
            i.clear()

        for i in self.__ptn_l1:
            self.__snd_l1.append(self.__prepare_one(i, length))

        for i in self.__ptn_l2:
            self.__snd_l2.append(self.__prepare_one(i, length))

        for i in self.__ptn_bk:
            self.__snd_bk.append(self.__prepare_one(i, length))

        logging.info(f"Generated drum patterns {len(self.__snd_l1)}")

        self.random_samples()
        self.__length = length

    def __prepare_one(self, pattern, length: int) -> np.ndarray:
        accents = pattern["acc"]
        ndarr = make_zero_buffer(length)
        for sound_name in [x for x in self.__sounds if x in pattern]:
            notes = pattern[sound_name]
            steps = len(notes)
            if notes.count("!") + notes.count(".") != steps:
                logging.error(f"sound {sound_name} notes {notes} must contain only '.' and '!'")

            step_len = length // steps
            sound, sound_volume = self.__sounds[sound_name]
            sound = sound[:length]
            assert sound.ndim == 2 and sound.shape[1] == 2
            assert 0 < sound.shape[0] <= length, f"Must be: 0 < {sound.shape[0]} <= {length}"

            for step_number in range(steps):
                if notes[step_number] != '.':
                    step_accent = int(accents[step_number])
                    step_volume = sound_volume * step_accent / 9 * self.volume / 100
                    pos = position_with_swing(step_number, step_len, self.swing)
                    tmp = (sound * step_volume).astype(SD_TYPE)
                    record_sound_buff(ndarr, tmp, pos)

        return ndarr


if __name__ == "__main__":
    pass
