import logging

# noinspection PyProtectedMember
from drum._utildrum import load_audio, load_midi, sysex_list


def test_1():
    x = load_audio()
    logging.debug(x)

    x = load_midi()
    logging.debug(x)


def test_2():
    n = 15148263
    x = sysex_list(n)
    assert x == [15, 14, 82, 63]

    n = -151.87
    x = sysex_list(n)
    assert x == [1, 52]
