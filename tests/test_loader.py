import unittest
from unittest import TestCase


class AA:
    def __init__(self):
        pass

    @staticmethod
    def st1():
        return "st1"


class BB(AA):
    def __init__(self):
        AA.__init__(self)

    @staticmethod
    def st1():
        return "st2"


class TestLoader(TestCase):
    bb = BB()
    print(BB.st1(), bb.st1())


if __name__ == "__main__":
    unittest.main()
