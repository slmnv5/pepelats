import os
import sys
import wave
from math import ceil, log10
from typing import Any

import numpy as np
from numpy import dtype, floating

from basic.audioinfo import get_dtype_max, AudioInfo


def make_sin_sound(sound_freq: int, duration_sec: float, amplitude: float = 0.25) -> np.ndarray:
    assert 0 <= amplitude < 1 and sound_freq > 0 and duration_sec > 0
    points_in_array: int = int(AudioInfo().SD_RATE * duration_sec)
    t = np.linspace(0, duration_sec, points_in_array)
    x = amplitude * np.sin(2 * np.pi * sound_freq * t)
    return x


def make_noise(duration_sec: float, amplitude: float = 0.25):
    points_in_array: int = int(AudioInfo().SD_RATE * duration_sec)
    x = np.random.standard_normal(points_in_array)
    max_value = np.max(x)
    x = x * (amplitude / max_value)
    return x


def int_to_bytes(value: float, byte_count: int = 0) -> list[int]:
    """ MIDI sys-ex data bytes, convert value to list: ex. 12531 -> 01, 02, 05, 03, 01 """
    assert value >= 0
    value = round(value)
    if byte_count <= 0:
        byte_count = ceil(log10(value))
    assert value <= 10 ** byte_count, f"value: {value}, byte_count: {byte_count}"
    bytes_list = []
    for i in range(byte_count):
        bytes_list.append(value % 10)
        value //= 10
    return bytes_list[::-1]


def bytes_to_int(byte_list: list[int]) -> int:
    """ MIDI sys-ex data bytes, convert it to int: ex. 00, 01, 02, 05, 03, 09 -> 12539"""
    value: int = 0
    byte_list = byte_list[::-1]
    for i in range(len(byte_list)):
        value += byte_list[i] * (10 ** i)
    return value


def read_wav_slow(fname: str, data_type: str) -> np.ndarray[Any, dtype[floating[Any]]]:
    """ slow reading using wave module, avoids import of specialized modules """
    assert os.path.isfile(fname)
    with wave.open(fname, "rb") as f:
        n_channels, sample_width, frame_rate, n_frames, _, _ = f.getparams()
        buffer = f.readframes(-1)

    signed = sample_width > 1  # 8 bit WAVs are unsigned
    byteorder = sys.byteorder  # wave module uses sys.byteorder for bytes
    sz = sample_width * n_channels
    frames = (buffer[i * sz: (i + 1) * sz] for i in range(n_frames))
    values = []  # e.g. for stereo, values[i] = [left_val, right_val]
    for frame in frames:
        channel_vals = []  # mono has 1 channel, stereo 2, etc.
        for channel in range(n_channels):
            as_bytes = frame[channel * sample_width: (channel + 1) * sample_width]
            as_int = int.from_bytes(as_bytes, byteorder, signed=signed)
            channel_vals.append(as_int)
        values.append(channel_vals)

    nparray = np.array(values)
    factor1: float = 1. / (2 ** (sample_width * 8 - 1))
    factor2: float = get_dtype_max(data_type)
    return (nparray * (factor1 * factor2)).astype(data_type)


def write_wav(fname: str, sound: np.ndarray) -> None:
    assert sound.ndim == 2 and sound.shape[1] in [1, 2]
    with wave.open(fname, "w") as f:
        f.setnchannels(sound.shape[1])
        f.setsampwidth(sound.itemsize)
        f.setframerate(AudioInfo().SD_RATE)
        f.writeframes(sound.tobytes())
