import random

import numpy as np

from utils.util_audio import AUDIO_INFO
from utils.util_numpy import from_buff_to_data, from_data_to_buff, trim_buffer


def _record(buff_len, data_len, idx):
    buff = np.zeros((buff_len, AUDIO_INFO.SD_CH), AUDIO_INFO.SD_TYPE)
    data = np.zeros((data_len, AUDIO_INFO.SD_CH), AUDIO_INFO.SD_TYPE)
    buff[:] = 1
    data[:] = 2
    original = data.copy()

    from_data_to_buff(buff, data, idx)
    assert np.array_equal(original, data)
    if data_len == 0 or buff_len == 0:
        is_good = np.all(np.unique(buff) == [1])
    elif data_len >= buff_len > 0:
        is_good = np.all(np.unique(buff) == [3])
    else:
        is_good = np.all(np.unique(buff) == [1, 3])

    assert is_good, f"==={buff_len}=={data_len}=={idx}==RECORD"


def _play(buff_len, data_len, idx):
    buff = np.zeros((buff_len, AUDIO_INFO.SD_CH), AUDIO_INFO.SD_TYPE)
    data = np.zeros((data_len, AUDIO_INFO.SD_CH), AUDIO_INFO.SD_TYPE)
    buff[:] = 1
    data[:] = 2
    original = buff.copy()

    from_buff_to_data(buff, data, idx)
    assert np.array_equal(original, buff)

    if data_len == 0 or buff_len == 0:
        is_good = np.all(np.unique(data) == [2])
    elif 0 < data_len <= buff_len:
        is_good = np.all(np.unique(data) == [3])
    else:
        is_good = np.all(np.unique(data) == [2, 3])

    assert is_good, f"==={buff_len}=={data_len}=={idx}==PLAY"


def _trim(buff_len, data_len, idx):
    x = np.linspace(1, buff_len, buff_len)
    y = np.column_stack((x, x))
    z = trim_buffer(y, data_len, idx)

    min_len = min(buff_len, data_len)

    if data_len == 0 or buff_len == 0:
        pass
    else:
        check1 = len(z) == min_len
        check2 = np.all(z[0] == y[idx % len(y)])
        assert check1 and check2


def test_all():
    for _ in range(100):
        buff_len: int = random.randrange(0, 50)
        data_len: int = random.randrange(0, 50)
        idx: int = random.randint(0, 200)
        _record(buff_len, data_len, idx)
        _play(buff_len, data_len, idx)
        _trim(buff_len, data_len, idx)


def test_1():
    x = np.array([0, 1, 2, 3, 4, 5])
    z = trim_buffer(x, 4, 3)
    assert z.tolist() == [3, 4, 5, 0]
