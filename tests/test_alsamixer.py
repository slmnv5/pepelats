import unittest
from unittest import TestCase

from mixer import Mixer


class TestAlsaMixer(TestCase):
    """integration test, volume is saved in file"""

    def test_1(self):
        mixer1 = Mixer()
        out_v: int = mixer1.getvolume(out=True)
        in_v: int = mixer1.getvolume(out=False)

        mixer1.setvolume(33, out=True)
        mixer1.setvolume(23, out=False)

        self.assertEqual(mixer1.getvolume(out=True), 33)
        self.assertEqual(mixer1.getvolume(out=False), 23)

        mixer1.setvolume(out_v, out=True)
        mixer1.setvolume(in_v, out=False)

        mixer3 = Mixer()
        self.assertEqual(mixer3.getvolume(out=True), out_v)
        self.assertEqual(mixer3.getvolume(out=False), in_v)


if __name__ == "__main__":
    unittest.main()
