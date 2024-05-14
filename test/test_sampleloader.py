import sounddevice as sd

# noinspection PyProtectedMember
from drum._sampleloader import SampleLoader


def test_1():
    sl = SampleLoader()
    sample_lst = sl.get_sound_names()
    assert sample_lst
    print("")
    for sample in sample_lst:
        sound = sl.get_sound(sample, True)
        sd.play(sound, blocking=True)
