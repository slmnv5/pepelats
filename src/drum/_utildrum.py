import os
import traceback
from enum import IntEnum
from typing import List, Dict, Union

import numpy as np
import soundfile

from utils import JsonDict
from utils.config import SD_RATE, SD_TYPE, ROOT_DIR, ConfigName, SD_MAX
from utils.log import LOGGER


class Intensity(IntEnum):
    SILENT = 0
    LVL1 = 1
    LVL2 = 2
    BREAK = 4


def extend_list(some_list: Union[List, str], new_len: int) -> List:
    """replicate or shrink list or string to a new length
    ex: 'abc -> abcabc """
    k = -(-new_len // len(some_list))
    return (some_list * k)[:new_len]


def position_with_swing(length: int, step_number: int, step_len: int, swing: float, early_shift: int) -> int:
    """ Shift every even 16th note to make it swing like.
    Apply early shift and return non negative postion"""
    assert early_shift >= 0
    if step_number % 2 == 0:
        return (step_number * step_len - early_shift) % length
    else:
        swing_delta: int = int(step_len * (swing - 0.5))
        return (step_number * step_len + swing_delta - early_shift) % length


def load_all_patterns(directory: str, file_name: str, storage: List[Dict], sound_names: List[str]) -> None:
    storage.clear()
    loader = JsonDict(os.path.join(directory, file_name + ".json"))
    default: Dict = loader.get(ConfigName.default_config, None)
    if default:
        loader.dic().pop(ConfigName.default_config)
    for key in loader.dic():
        value = loader.get(key, None)
        if not value:
            continue
        assert type(value) == dict, f"Must be dictionary {key}"
        assert len(value) > 0, f"Dictionary must be non empty {key}"
        if default:
            value = dict(default, **value)
        for sound_name in [x for x in sound_names if x in value]:
            value[sound_name] = extend_list(value[sound_name], value["steps"])

        value["name"] = key
        value["acc"] = extend_list(value["acc"], value["steps"])
        storage.append(value)


def int_to_7bit_list(int_value: int) -> List[int]:
    """ MIDI sysex message contains data as 7bit list (high bit must be zero)
     Here an integer is stored in 7bit valuse MSB goes first] """
    bit_str: str = f'{int_value:b}'
    _7bit_list: List[int] = [int(bit_str[i:i + 7], 2) for i in range(0, len(bit_str), 7)]
    return _7bit_list


def convert_list(lst: List, **kwargs) -> List[int]:
    """  convert list where numbers are integer or hex strings
    or passed as kwargs: ["0xAF", 112, "0XFF", "volume"] """
    # noinspection PyBroadException
    try:
        lst = [kwargs[x] if x in kwargs else x for x in lst]
        return [int(x, 0) if isinstance(x, str) else x for x in lst]
    except Exception:
        LOGGER.error(f"convert_list: list: {lst} args: {kwargs}, error: {traceback.format_exc()}")
        return []


def bpm_from_length(length: int) -> float:
    bar_seconds: float = length / SD_RATE
    return 60 / (bar_seconds / 4)


def max_volume_audio(sounds: Dict[str, np.ndarray]) -> float:
    max_found: float = 0
    for sound in sounds.values():
        max_found = max(max_found, np.max(sound))
    return max_found / SD_MAX


def max_volume_midi(sounds: Dict[str, List[int]]) -> float:
    max_found: float = 0
    for sound in sounds.values():
        max_found = max(max_found, sound[2])
    return max_found / 127


def load_sounds(load_midi: bool) -> Dict[str, Union[np.ndarray, List[int]]]:
    """Loads WAV sounds, change volume to given value"""
    path = os.path.join(ROOT_DIR, "config/sounds/drum_sounds.json")
    loader = JsonDict(path)
    for name in loader.dic():
        drum_sound = loader.get(name, None)
        assert len(drum_sound) > 0
        assert type(drum_sound) == dict
        if load_midi:
            midi_bytes: List[int] = drum_sound["midi"]
            loader.dic()[name] = midi_bytes
        else:
            file_name: str = os.path.join(loader.get_dir(), drum_sound["file_name"])
            sound_volume: float = drum_sound.get("volume", 1.0)

            (sound, _) = soundfile.read(file_name, dtype="int16", always_2d=True)
            assert sound.ndim == 2
            assert sound.shape[1] == 2

            sound = (sound * sound_volume).astype(SD_TYPE)
            loader.dic()[name] = sound
    return loader.dic()
