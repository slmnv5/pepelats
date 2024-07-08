import sounddevice as sd

from basic.audioinfo import AudioInfo
# noinspection PyProtectedMember
from drum._sampleloader import SampleLoader


def test_1():
    sl = SampleLoader()
    print(sl.get_energy('bd', True))
    sound = sl.get_sound('bd', True)
    assert sound.shape[1] == AudioInfo().SD_CH
    assert sound.dtype == AudioInfo().SD_TYPE
    sd.play(sound, blocking=True)
