import unittest
from unittest import TestCase

from utils import CONFLDR, ConfigName


class TestMainLoader(TestCase):

    def test_1(self):
        val = CONFLDR.get(ConfigName.drum_volume, -1)
        self.assertTrue(val > 0)


if __name__ == "__main__":
    unittest.main()
