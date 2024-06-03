import sounddevice as sd

from audio.audioinfo import AINFO
# noinspection PyProtectedMember
from audio.sampleloader import SAMPLE_LOAD


def test_1():
    print(SAMPLE_LOAD.get_energy('bd', True))
    sound = SAMPLE_LOAD.get_sound('bd', True)
    assert sound.shape[1] == AINFO.SD_CH
    assert sound.dtype == AINFO.SD_TYPE
    sd.play(sound, blocking=True)
