import sounddevice as sd

# noinspection PyProtectedMember
from audio.sampleloader import SampleLoader


def test_1():
    sound = SampleLoader().get_sound('bd', True)
    sd.play(sound, blocking=True)
