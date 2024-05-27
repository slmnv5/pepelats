import sounddevice as sd

from utils.utilaudio import AUDIO


def test_1():
    print(f"Default device type: {AUDIO.SD_TYPE}, chanels: {AUDIO.SD_CH}")
    print(sd.query_devices(device=sd.default.device[0]))
    print(sd.query_devices(device=sd.default.device[1]))


if __name__ == "__main__":
    test_1()
