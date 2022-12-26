import os
from math import ceil, log10
from typing import List, Dict, Union, Tuple

import numpy as np
import soundfile

from utils.utilconfig import SD_RATE, SD_TYPE, ROOT_DIR, ConfigName, SD_MAX, DRUM_CHANNEL
from utils.utilother import JsonDict


def is_midi_note(msg: List[int]) -> bool:
    return msg and len(msg) == 3 and 0x80 <= msg[0] <= 0x9F


def extend_list(some_list: Union[List, str], new_len: int) -> List:
    """replicate or shrink list or string to a new length
    ex: 'abc -> abcabc """
    k = -(-new_len // len(some_list))
    return (some_list * k)[:new_len]


def position_with_swing(step_number: int, step_len: int, swing: float) -> int:
    """ Shift every even 16th note to make it swing like."""
    if step_number % 2 == 0:
        return step_number * step_len
    else:
        swing_delta: int = int(step_len * (swing - 0.5))
        return step_number * step_len + swing_delta


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


def map_range_midi(target: float, initial: float, spread: float) -> Tuple[int, float]:
    """ Convert target in a range given as initial and spread into MIDI byte from 0 to 127
    As exact match not possible, returns MIDI byte and resulting target value.
    Ex. map_range_midi(55.22, 0, 127) -> (55, 55.22)"""
    if target < initial or target > initial + spread:
        raise RuntimeError(f"map_range_midi: worng values passed: {target}/{initial}/{spread}")
    val1 = round((target - initial) / spread * 127)
    tar1 = val1 * spread / 127 + initial
    return val1, tar1


def sysex_list(value: float, count: int = 0) -> List[int]:
    """ MIDI sysex contains data bytes, convert value to list: ex. 12531 -> 01, 25, 31"""
    value = -value if value < 0 else value
    value = round(value)
    if count <= 0:
        count = ceil(log10(value) / 2)
    assert value <= 100 ** count
    bytes_list = []
    for i in range(count):
        bytes_list.append(value % 100)
        value = value // 100
    return bytes_list[::-1]


def bpm_from_length(length: int) -> float:
    bar_seconds: float = length / SD_RATE
    return 60 / (bar_seconds / 4)


def max_volume_audio(sounds: Dict[str, np.ndarray]) -> float:
    max_found: float = 0
    for name, sound in sounds.items():
        assert isinstance(sound, np.ndarray), f"Incorrect audio type for sound: {name}"
        max_found = max(max_found, np.max(sound))
    return max_found / SD_MAX


def max_volume_midi(sounds: Dict[str, List[int]]) -> float:
    max_found: float = 0
    for sound in [x for x in sounds.values() if x[0] & 0xF0 == 0x90]:
        max_found = max(max_found, sound[2])
    return max_found / 127.0


def load_audio() -> Dict[str, np.ndarray]:
    """Loads WAV sounds, change volume to given value"""
    path = ROOT_DIR + "/config/sounds/drum_sounds.json"
    loader = JsonDict(path)
    result = dict()
    for name in loader.dic():
        drum_sound = loader.get(name, None)
        assert len(drum_sound) > 0
        assert type(drum_sound) == dict
        file_name: str = drum_sound.get("file_name")
        if not file_name:
            continue
        file_name: str = os.path.join(loader.get_dir(), file_name)
        sound_volume: float = drum_sound.get("volume", 1.0)
        (sound, _) = soundfile.read(file_name, dtype="int16", always_2d=True)
        assert sound.ndim == 2 and sound.shape[1] == 2
        sound = (sound * sound_volume).astype(SD_TYPE)
        result[name] = sound

    return result


def load_midi() -> Dict[str, List[int]]:
    """Loads WAV sounds, change volume to given value"""
    path = ROOT_DIR + "/config/sounds/drum_sounds.json"
    loader = JsonDict(path)
    result = dict()
    for name in loader.dic():
        drum_sound = loader.get(name, None)
        assert len(drum_sound) > 0
        assert type(drum_sound) == dict
        msg: List[int] = drum_sound.get("midi")
        if not msg:
            continue
        if is_midi_note(msg):
            msg[0] &= 0xF0
            msg[0] += DRUM_CHANNEL

        result[name] = msg

    return result


if __name__ == "__main__":
    def test1():
        import logging

        x = load_audio()
        y = max_volume_audio(x)
        logging.debug(y)

        x = load_midi()
        y = max_volume_midi(x)
        logging.debug(y)


    def test2():
        n = 15148263
        x = sysex_list(n)
        assert x == [15, 14, 82, 63]

        n = -151.87
        x = sysex_list(n)
        assert x == [1, 52]


    def test3():
        import logging

        a, b = map_range_midi(55.22, 0, 127)
        assert (a, b) == (55, 55.0)

        target = 120
        int_val1, try_bpm1 = map_range_midi(target, 20, 180)
        logging.debug(int_val1, try_bpm1)
        int_val2, try_bpm2 = map_range_midi(target - try_bpm1, -20, 40)
        logging.debug(int_val2, try_bpm2)


    test3()
