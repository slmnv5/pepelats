import os
import random
from pathlib import Path
from typing import List, Any, Dict, Union, Tuple

import numpy as np
import soundfile as sf

from utils import LOGR
from utils import JsonDict, make_zero_buffer, record_sound_buff, SD_TYPE, ConfigName, FileFinder, CONFLDR
from utils import SD_MAX


def extend_list(some_list: Union[List, str], new_len: int) -> List:
    """replicate or shrink list or string to a new length"""
    k = -(-new_len // len(some_list))
    return (some_list * k)[:new_len]


class DrumLoader:
    """ class will only static methods to load drum patterns """

    max_volume: float = 0
    __length: int = 0
    __sounds: Dict[str, Tuple[np.ndarray, float]] = dict()
    l1: np.ndarray = []
    l2: np.ndarray = []
    bk: np.ndarray = []
    __ptn_l1: List[Dict[str, Any]] = []
    __ptn_l2: List[Dict[str, Any]] = []
    __ptn_bk: List[Dict[str, Any]] = []
    __snd_l1: List[np.ndarray] = []
    __snd_l2: List[np.ndarray] = []
    __snd_bk: List[np.ndarray] = []

    @staticmethod
    def clear_drum() -> None:
        DrumLoader.__length = 0

    @staticmethod
    def get_length() -> int:
        return DrumLoader.__length

    @staticmethod
    def random_samples():
        DrumLoader.l2 = random.choice(DrumLoader.__snd_l2)
        DrumLoader.l1 = random.choice(DrumLoader.__snd_l1)
        DrumLoader.bk = random.choice(DrumLoader.__snd_bk)

    @staticmethod
    def load(dir_name: Path) -> None:
        LOGR.info(f"Loading drum {dir_name}")
        if len(DrumLoader.__sounds) == 0:
            DrumLoader.__load_sounds(dir_name)
            LOGR.info(f"Loaded drum sounds {len(DrumLoader.__sounds)}")
        DrumLoader.__load_all_patterns(dir_name, "drum_level1", DrumLoader.__ptn_l1)
        DrumLoader.__load_all_patterns(dir_name, "drum_level2", DrumLoader.__ptn_l2)
        DrumLoader.__load_all_patterns(dir_name, "drum_break", DrumLoader.__ptn_bk)
        LOGR.info(f"Loaded drum patterns {len(DrumLoader.__ptn_l1)}")

    @staticmethod
    def __load_sounds(dir_name: Path) -> None:
        """Loads WAV sounds"""
        path = os.path.join(dir_name.parent, "drum_sounds.json")
        loader = JsonDict(path)
        for name in loader.dic:
            drum_sound = loader.get(name, dict())
            assert len(drum_sound) > 0
            assert type(drum_sound) == dict
            file_name = drum_sound["file_name"]
            file_name = Path(loader.get_filename().parent, file_name)
            v1: float = drum_sound.get("volume", 1.0)

            (sound, _) = sf.read(str(file_name), dtype="int16", always_2d=True)
            assert sound.ndim == 2
            assert sound.shape[1] == 2
            v2: float = np.max(sound)
            DrumLoader.max_volume = max(DrumLoader.max_volume, v1 * v2)
            assert DrumLoader.max_volume < SD_MAX
            #  LOGR.info(f"Loaded sound {file_name}")
            DrumLoader.__sounds[name] = (sound, v1)

    @staticmethod
    def __load_all_patterns(dir_name: Path, file_name: str, storage: List[Dict]) -> None:
        storage.clear()
        path = os.path.join(dir_name, file_name + ".json")
        loader = JsonDict(path)
        default = loader.get(ConfigName.default_pattern, dict())
        for key in [x for x in loader.dic if x not in [ConfigName.comment, ConfigName.default_pattern]]:
            value = loader.get(key, None)
            assert type(value) == dict, f"Must be dictionary {key}"
            assert len(value) > 0, f"Dictionary must be non empty {key}"
            value = dict(default, **value)
            value["name"] = key
            value["acc"] = extend_list(value["acc"], value["steps"])
            for sound_name in [x for x in DrumLoader.__sounds if x in value]:
                value[sound_name] = extend_list(value[sound_name], value["steps"])
            storage.append(value)

    @staticmethod
    def prepare_all(length: int) -> None:
        DrumLoader.__length = 0
        if length == 0:
            return

        for i in [DrumLoader.__snd_l1, DrumLoader.__snd_l2, DrumLoader.__snd_bk]:
            i.clear()

        for i in DrumLoader.__ptn_l1:
            DrumLoader.__snd_l1.append(DrumLoader.__prepare_one(i, length))

        for i in DrumLoader.__ptn_l2:
            DrumLoader.__snd_l2.append(DrumLoader.__prepare_one(i, length))

        for i in DrumLoader.__ptn_bk:
            DrumLoader.__snd_bk.append(DrumLoader.__prepare_one(i, length))

        LOGR.info(f"Generated drum patterns {len(DrumLoader.__snd_l1)}")

        DrumLoader.random_samples()
        DrumLoader.__length = length

    @staticmethod
    def __prepare_one(pattern, length: int) -> np.ndarray:
        accents = pattern["acc"]
        swing: float = pattern["swing"]
        ndarr = make_zero_buffer(length)
        drum_volume = CONFLDR.get(ConfigName.drum_volume, 1)
        for sound_name in [x for x in DrumLoader.__sounds if x in pattern]:
            notes = pattern[sound_name]
            steps = len(notes)
            if notes.count("!") + notes.count(".") != steps:
                LOGR.error(f"sound {sound_name} notes {notes} must contain only '.' and '!'")

            step_len = length // steps
            sound, sound_volume = DrumLoader.__sounds[sound_name]
            sound = sound[:length]
            assert sound.ndim == 2 and sound.shape[1] == 2
            assert 0 < sound.shape[0] <= length, f"Must be: 0 < {sound.shape[0]} <= {length}"

            for step_number in range(steps):
                if notes[step_number] != '.':
                    step_accent = int(accents[step_number])
                    step_volume = sound_volume * step_accent * drum_volume / 9.0
                    pos = DrumLoader.__pos_with_swing(step_number, step_len, swing)
                    tmp = (sound * step_volume).astype(SD_TYPE)
                    record_sound_buff(ndarr, tmp, pos)

        return ndarr

    @staticmethod
    def __pos_with_swing(step_number: int, step_len: int, swing: float) -> int:
        """shift every even 16th note to make it swing like"""
        if step_number % 2 == 0:
            return round(step_number * step_len)
        else:
            swing_delta: float = step_len * (swing - 0.5)
            return round(step_number * step_len + swing_delta)


if __name__ == "__main__":
    def test():
        file_finder = FileFinder("config/drums", False, "")
        tmp = file_finder.get_path()
        DrumLoader.load(tmp)


    test()
