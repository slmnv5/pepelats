import logging
import os
from math import ceil, log10
from typing import List, Dict, Union, Any

import numpy as np
import soundfile

from utils.utilalsa import make_zero_buffer
from utils.utilconfig import ENV_SD_RATE, SD_TYPE, ENV_ROOT_DIR, ConfigName, ENV_DRUM_CHANNEL
from utils.utilnumpy import record_sound_buff
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
    bar_seconds: float = length / ENV_SD_RATE
    return 60 / (bar_seconds / 4)


def load_audio() -> Dict[str, np.ndarray]:
    """Loads WAV sounds, change volume to given value"""
    path = ENV_ROOT_DIR + "/config/sounds/drum_sounds.json"
    loader = JsonDict(path)
    result = dict()
    for name in loader.dict():
        drum_sound = loader.get(name, None)
        assert len(drum_sound) > 0
        assert type(drum_sound) == dict
        file_name: str = drum_sound.get("file_name")
        if not file_name:
            continue
        file_name: str = os.path.join(loader.get_dir(), file_name)
        sound_volume: float = drum_sound.get("volume", 1.0)
        (sound, _) = soundfile.read(file_name, dtype=SD_TYPE, always_2d=True)
        assert sound.ndim == 2 and sound.shape[1] == 2
        sound = (sound * sound_volume).astype(SD_TYPE)
        result[name] = sound

    return result


def load_midi() -> Dict[str, List[int]]:
    """Loads WAV sounds, change volume to given value"""
    path = ENV_ROOT_DIR + "/config/sounds/drum_sounds.json"
    loader = JsonDict(path)
    result = dict()
    for name in loader.dict():
        drum_sound = loader.get(name, None)
        assert len(drum_sound) > 0
        assert type(drum_sound) == dict
        msg: List[int] = drum_sound.get("midi")
        if not msg:
            continue
        if is_midi_note(msg):
            msg[0] &= 0xF0
            msg[0] += ENV_DRUM_CHANNEL

        result[name] = msg

    return result


def load_all_patterns(directory: str, file_name: str, storage: List[Dict], sounds: Dict[str, np.ndarray]) -> None:
    storage.clear()
    loader = JsonDict(os.path.join(directory, file_name + ".json"))
    dic: Dict = loader.dict()
    default: Dict = dic.get(ConfigName.default_config, dict())
    for key in [x for x in dic if x not in [ConfigName.default_config, ConfigName.comment]]:
        pattern = loader.get(key, None)
        assert type(pattern) == dict, f"Must be dictionary {key}"
        assert len(pattern) > 0, f"Dictionary must be non empty {key}"
        pattern = dict(default, **pattern)
        steps = pattern.get("steps", 0)
        assert isinstance(steps, int) and steps >= 0
        accents = pattern.get("accents", "5")
        assert isinstance(accents, str) and len(accents) > 0
        for sound_name in [x for x in pattern if x not in sounds]:
            pattern.pop(sound_name)

        pattern["accents"] = accents
        pattern["name"] = key
        pattern["steps"] = steps
        storage.append(pattern)


def audio_drum_from_pattern(pattern: Dict[str, Any], sounds: Dict[str, np.ndarray],
                            length: int, volume: float, swing: float) -> np.ndarray:
    steps = pattern["steps"]
    accents = pattern["accents"]
    result: np.ndarray = make_zero_buffer(length)
    for sound_name in [x for x in sounds if x in pattern]:
        notes = pattern[sound_name]
        sound = sounds[sound_name][0:length]
        if isinstance(notes, str):
            notes = extend_list(notes, steps) if steps else notes
            audio_drum_from_string(result, sound, notes, accents, length, volume, swing)
        else:
            logging.error(f"Drum pattern must be a string: {sound_name}")

    return result


def audio_drum_from_string(result: np.ndarray, sound: np.ndarray, notes: str, accents: str,
                           length: int, volume: float, swing: float) -> None:
    assert notes.count("!") + notes.count(".") == len(notes), f"Pattern symbol must be '.' or '!'"
    steps = len(notes)
    accents = extend_list(accents, steps)
    step_len = length // steps
    assert sound.ndim == 2 and sound.shape[1] == 2

    for step_number in range(steps):
        if notes[step_number] == '!':
            step_accent = int(accents[step_number])
            step_volume = step_accent / 9 * volume
            pos = position_with_swing(step_number, step_len, swing)
            tmp = (sound * step_volume).astype(SD_TYPE)
            record_sound_buff(result, tmp, pos)


def midi_drum_from_pattern(pattern: Dict[str, Any], sounds: Dict[str, List[int]],
                           length: int, volume: float, swing: float) -> Dict[int, List[List[int]]]:
    steps = pattern["steps"]
    accents = pattern["accents"]
    result: Dict[int, List[List[int]]] = dict()
    for sound_name in [x for x in sounds if x in pattern]:
        notes = pattern[sound_name]
        sound = sounds[sound_name]
        if isinstance(notes, str):
            notes = extend_list(notes, steps) if steps else notes
            midi_drum_from_string(result, sound, notes, accents, length, volume, swing)
        else:
            raise RuntimeError(f"Drum pattern must be a string: {sound_name}")

    return result


def midi_drum_from_string(result: Dict, sound: List[int], notes: str, accents: str,
                          length, volume: float, swing: float) -> None:
    assert notes.count("!") + notes.count(".") == len(notes), f"Pattern symbol must be '.' or '!'"
    steps = len(notes)
    accents = extend_list(accents, steps)
    step_len = length // steps
    for step_number in range(steps):
        if notes[step_number] == '!':
            step_accent = int(accents[step_number])
            step_volume = int(step_accent / 9 * volume * 127)
            assert step_volume <= 127
            pos = position_with_swing(step_number, step_len, swing)
            sound[2] = step_volume
            lst = result.get(pos, list())
            lst.append(sound)
            result[pos] = lst


if __name__ == "__main__":
    pass
