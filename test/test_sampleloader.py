import sounddevice

# noinspection PyProtectedMember
from drum._sampleloader import SampleLoader
from utils.utilconfig import SD_RATE


def test_1():
    sl = SampleLoader()
    sample_lst = sl.get_sound_names()
    assert sample_lst
    print("")
    for sample in sample_lst:
        sound = sl.get_sound(sample, True)
        print(f"sound: {sample}, volume: {sl.volumes[sample]}, "
              f"max: {sl.maxes[sample]}, duration: {round(len(sound) / SD_RATE, 2)} sec.")
        sound = sl.get_sound(sample, True)
        sounddevice.play(sound, blocking=True)
