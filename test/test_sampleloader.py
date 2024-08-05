import sounddevice as sd

from utils.util_audio import AUDIO_INFO
# noinspection PyProtectedMember
from drum._sampleloader import SampleLoader


def test_1():
    sl = SampleLoader()
    assert sl.get_energy('bd', True) > 0
    sound = sl.get_sound('bd', True)
    assert sound.shape[1] == AUDIO_INFO.SD_CH
    assert sound.dtype == AUDIO_INFO.SD_TYPE
    sd.play(sound, blocking=True)
