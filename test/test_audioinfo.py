from basic.audioinfo import AudioInfo


def test_1():
    assert 'float' in AudioInfo().SD_TYPE or 'int' in AudioInfo().SD_TYPE
    assert AudioInfo().SD_CH in [1, 2]
