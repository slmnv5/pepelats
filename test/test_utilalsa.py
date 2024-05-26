import os

import numpy as np
import sounddevice as sd

from utils.utilalsa import make_noise, correct_sound, int_to_bytes, bytes_to_int, make_sin_sound, write_wav, \
    read_wav_slow, get_conversion_factor
from utils.utilaudio import SD_RATE
from utils.utilconfig import find_path


def test_1() -> None:
    sound = make_noise(0.5)
    sound = correct_sound(sound, 2, 'int16')
    sd.play(sound, blocking=True)


def test_2():
    n = 19915.112
    assert int_to_bytes(n, 5) == [1, 9, 9, 1, 5]
    assert int_to_bytes(n, 7) == [0, 0, 1, 9, 9, 1, 5]
    assert bytes_to_int([0, 0, 0, 0, 1, 9, 9, 1, 5]) == 19915

    n = 151.87
    assert int_to_bytes(n) == [1, 5, 2]
    assert bytes_to_int([1, 5, 2]) == 152
    assert int_to_bytes(1005) == [1, 0, 0, 5]


def test_3() -> None:
    sound: np.ndarray = sd.rec(SD_RATE, dtype='int16', blocking=True)

    for _ in range(3):
        sd.play(sound, blocking=True)


def test_4() -> None:
    sound: np.ndarray = sd.rec(SD_RATE, dtype='float32', blocking=True)

    for _ in range(3):
        sd.play(sound, blocking=True)


def test_5() -> None:
    fname = find_path('.save_song') + os.sep + "test.wav"
    sound1: np.ndarray = make_sin_sound(330, 1)

    sound1 = correct_sound(sound1, 1, 'int16')
    write_wav(fname, sound1)
    sound2: np.ndarray = read_wav_slow(fname)
    assert sound2.shape == (SD_RATE, 1)

    sound1 = correct_sound(sound1, 2, 'float32')
    write_wav(fname, sound1)
    sound2: np.ndarray = read_wav_slow(fname)
    assert sound2.shape == (SD_RATE, 2)
    # noinspection PyBroadException
    try:
        os.remove(fname)
    except Exception:
        pass


def test_6() -> None:
    assert get_conversion_factor('int16', 'int16') == 1
    assert get_conversion_factor('float32', 'int16') == 32767
    assert round(get_conversion_factor('int16', 'float32'), 6) == round(1 / 32768, 6)
    assert get_conversion_factor('float64', 'float32') == 1
    assert get_conversion_factor('float32', 'float64') == 1
    assert get_conversion_factor('float64', 'int16') == 32767


if __name__ == "__main__":
    test_3()
    test_4()
    test_5()
