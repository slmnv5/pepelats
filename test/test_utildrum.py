import logging

# noinspection PyProtectedMember
from drum._utildrum import load_audio, max_volume_audio, load_midi, max_volume_midi, sysex_list


def test_1():
    x = load_audio()
    y = max_volume_audio(x)
    logging.debug(y)

    x = load_midi()
    y = max_volume_midi(x)
    logging.debug(y)


def test_2():
    n = 15148263
    x = sysex_list(n)
    assert x == [15, 14, 82, 63]

    n = -151.87
    x = sysex_list(n)
    assert x == [1, 52]
