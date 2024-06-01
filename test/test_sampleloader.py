import sounddevice as sd

from audio.audioinfo import AINFO
# noinspection PyProtectedMember
from audio.sampleloader import SMPLLOAD


def test_1():
    print(SMPLLOAD.get_energy('bd', True))
    sound = SMPLLOAD.get_sound('bd', True)
    assert sound.shape[1] == AINFO.SD_CH
    assert sound.dtype == AINFO.SD_TYPE
    sd.play(sound, blocking=True)
