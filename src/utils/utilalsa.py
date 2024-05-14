from math import ceil, log10

import numpy as np
import sounddevice as sd

from utils.utilconfig import SD_TYPE, MAX_LEN, OUT_CH, MAX_SD_TYPE


def make_zero_buffer(buff_len: int) -> np.ndarray:
    if buff_len < 0 or buff_len > MAX_LEN:
        raise RuntimeError(f"make_zero_buffer: incorrect buffer size: {buff_len}")
    return np.zeros((buff_len, OUT_CH), SD_TYPE)


def line_ndarray(slope: float, offset: float, duration_sec: float) -> np.ndarray:
    """ Makes numpy array with linear function: y = slope * t + offset """
    points_in_array: int = int(sd.default.samplerate * duration_sec)
    t = np.linspace(0, duration_sec, points_in_array)
    return slope * t + offset


def correct_dtype(x: np.ndarray) -> np.ndarray:
    assert x.ndim == 1 or x.shape[1] == 1
    assert x.dtype in [np.float64, np.float32]
    x = (x * MAX_SD_TYPE).astype(SD_TYPE)
    return np.column_stack((x, x))


def make_sin_sound(sound_freq: int, duration_sec: float, amplitude: float = 0.25) -> np.ndarray:
    assert 0 <= amplitude < 1 and sound_freq > 0 and duration_sec > 0
    points_in_array: int = int(sd.default.samplerate * duration_sec)
    t = np.linspace(0, duration_sec, points_in_array)
    x = amplitude * np.sin(2 * np.pi * sound_freq * t)
    return x


def make_noise(duration_sec: float, amplitude: float = 0.25):
    points_in_array: int = int(sd.default.samplerate * duration_sec)
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
