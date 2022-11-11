import unittest
from unittest import TestCase

from utils import ConfLoader, ConfigName


class TestMainLoader(TestCase):

    def test_1(self):
        val = ConfLoader.get(ConfigName.drum_volume, -1)
        self.assertTrue(val > 0)


if __name__ == "__main__":
    unittest.main()
