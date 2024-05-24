import numpy as np
import sounddevice as sd

from utils.utilalsa import make_noise, correct_dtype, int_to_bytes, bytes_to_int
from utils.utilconfig import SD_RATE
from utils.utilnumpy import play_buffer


def test_1() -> None:
    duration_sec: float = 0.5
    result: np.ndarray = np.zeros(round(duration_sec * SD_RATE), dtype=float)
    result = correct_dtype(result)

    sound = make_noise(0.5)
    sound = correct_dtype(sound)
    play_buffer(sound, result, 0)

    sd.play(result, blocking=True)


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
    duration_sec: float = 1.0
    result: np.ndarray = sd.rec(round(duration_sec * SD_RATE), dtype='int16', blocking=True)
    print(111111111111, result.shape)

    for _ in range(3):
        sd.play(result, blocking=True)


if __name__ == "__main__":
    test_1()
    test_3()
