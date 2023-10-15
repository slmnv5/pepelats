import numpy as np
import sounddevice

from utils.utilalsa import make_sin_sound, make_noise, correct_dtype, int_to_bytes, bytes_to_int
from utils.utilconfig import SD_RATE
from utils.utilnumpy import play_buffer


def test_1() -> None:
    duration_sec: float = 0.5
    result: np.ndarray = np.zeros(round(duration_sec * SD_RATE), dtype=float)

    freq_lst: list[int] = [60, 65, 70, 75, 80]
    for freq in freq_lst:
        sound = make_sin_sound(freq, 0.5)
        play_buffer(sound, result, 0)

    sound = make_noise(0.1)
    play_buffer(sound, result, 0)

    result = correct_dtype(result)
    sounddevice.play(result, blocking=True)


def test_2():
    n = 19915.112
    assert int_to_bytes(n, 5) == [1, 9, 9, 1, 5]
    assert int_to_bytes(n, 7) == [0, 0, 1, 9, 9, 1, 5]
    assert bytes_to_int([0, 0, 0, 0, 1, 9, 9, 1, 5]) == 19915

    n = 151.87
    assert int_to_bytes(n) == [1, 5, 2]
    assert bytes_to_int([1, 5, 2]) == 152
    assert int_to_bytes(1005) == [1, 0, 0, 5]
