import unittest
from unittest import TestCase

import numpy as np

from utils import record_sound_buff


class TestNumpy(TestCase):
    def test_simple(self):
        long_arr = np.arange(1, 13).reshape(12, 1)
        short_arr = np.arange(1, 6).reshape(5, 1)
        buff0 = np.array([100] * 12).reshape(12, 1)

        buff1 = buff0.copy()
        record_sound_buff(buff1, long_arr, 8)
        np.testing.assert_equal(buff1,
                                np.array([105, 106, 107, 108, 109, 110, 111, 112, 101, 102, 103, 104]).reshape(12, 1))

        buff1 = buff0.copy()
        record_sound_buff(buff1, short_arr, 8)
        np.testing.assert_equal(buff1,
                                np.array([105, 100, 100, 100, 100, 100, 100, 100, 101, 102, 103, 104]).reshape(12, 1))

        buff1 = buff0.copy()
        record_sound_buff(buff1, short_arr, 2)
        np.testing.assert_equal(buff1,
                                np.array([100, 100, 101, 102, 103, 104, 105, 100, 100, 100, 100, 100]).reshape(12, 1))


if __name__ == "__main__":
    unittest.main()
