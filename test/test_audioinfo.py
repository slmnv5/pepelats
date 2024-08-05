from utils.util_audio import AUDIO_INFO


def test_1():
    assert 'float' in AUDIO_INFO.SD_TYPE or 'int' in AUDIO_INFO.SD_TYPE
    assert AUDIO_INFO.SD_CH in [1, 2]
