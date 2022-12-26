import os
from math import ceil, log10
from typing import List, Dict, Union, Tuple

import numpy as np
import soundfile

from utils.utilconfig import SD_RATE, SD_TYPE, ROOT_DIR, ConfigName, SD_MAX, DRUM_CHANNEL
from utils.utilother import JsonDict


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
