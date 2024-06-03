import sounddevice as sd

from audio.audioinfo import AUDIO_INFO
from audio.sampleloader import SampleLoader


def test_1():
    sl = SampleLoader()
    print(sl.get_energy('bd', True))
    sound = sl.get_sound('bd', True)
    assert sound.shape[1] == AUDIO_INFO.SD_CH
    assert sound.dtype == AUDIO_INFO.SD_TYPE
    sd.play(sound, blocking=True)
