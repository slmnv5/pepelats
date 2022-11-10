import unittest
from unittest import TestCase

from drum import RDRUM

drum = RDRUM()


class TestRealDrum(TestCase):

    def test_1(self):
        """prepare and print"""
        drum.prepare_drum(150_000)
        drum.play_break_now()
        drum.play_break_later(1000, 100)
        print(drum)


if __name__ == "__main__":
    unittest.main()
