import unittest
from unittest import TestCase

# noinspection PyProtectedMember
from loop._wrapbuffer import WrapBuffer
from utils import make_sin_sound, SD_RATE

sound_len = 500_000  # samples
sound = make_sin_sound(440, sound_len / SD_RATE)


class TestWrapBuffer(TestCase):

    def test_1(self):
        test_buff = WrapBuffer()
        test_buff.record_samples(sound[:100_000], 0)
        test_buff.finalize(121_000, -1)
        self.assertTrue(test_buff.length == 121_000)

        test_buff.sound_test(1, False)

    def test_trim2(self):
        test_buff = WrapBuffer()
        test_buff.record_samples(sound[:10], 0)
        test_buff.finalize(121_000, 100_000)
        self.assertTrue(test_buff.length == 100_000)

    def test_trim3(self):
        test_buff = WrapBuffer()
        test_buff.record_samples(sound[:10_000], 0)
        test_buff.finalize(10_000, 100_000)
        self.assertTrue(test_buff.length == 12_500, f"actual buff len: {test_buff.length}")

    def test_trim5(self):
        test_buff = WrapBuffer()
        had_error = False
        try:
            test_buff.finalize(151_000, 100_000)
        except AssertionError as err:
            self.assertTrue("start must be non negative" in str(err))
            had_error = True

        self.assertTrue(had_error)


if __name__ == "__main__":
    unittest.main()
