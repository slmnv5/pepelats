import os
import sys
import wave
from math import ceil, log10
from typing import List, Dict, Union, Tuple

import numpy as np

from utils.utilconfig import ENV_SD_RATE, ENV_ROOT_DIR, ConfigName, ENV_DRUM_CHANNEL
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
    """Loads WAV sounds, return float samples from -1 to 1"""
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
        (sound, _) = read_wav(file_name)
        assert sound.ndim == 2 and sound.shape[1] == 2
        sound = sound * sound_volume
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


def load_all_patterns(directory: str, file_name: str, storage: List[Dict]) -> None:
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
        pattern["accents"] = accents
        pattern["name"] = key
        pattern["steps"] = steps
        storage.append(pattern)


def read_wav(file_name) -> Tuple[np.ndarray, int]:
    with wave.open(file_name, "rb") as f:
        nchannels, sampwidth, framerate, nframes, _, _ = f.getparams()
        signed = sampwidth > 1  # 8 bit wavs are unsigned
        byteorder = sys.byteorder  # wave module uses sys.byteorder for bytes

        values = []  # e.g. for stereo, values[i] = [left_val, right_val]
        for _ in range(nframes):
            frame = f.readframes(1)  # read next frame
            channel_vals = []  # mono has 1 channel, stereo 2, etc.
            for channel in range(nchannels):
                as_bytes = frame[channel * sampwidth: (channel + 1) * sampwidth]
                as_int = int.from_bytes(as_bytes, byteorder, signed=signed)
                channel_vals.append(as_int)
            values.append(channel_vals)
    nparray = np.array(values)
    factor: float = 1 / (2 ** (sampwidth * 8 - 1))
    return nparray * factor, framerate


if __name__ == "__main__":
    pass
