import sounddevice as sd

from audio.audioinfo import AINFO


def test_1():
    print(f"Default device type: {AINFO.SD_TYPE}, channels: {AINFO.SD_CH}")
    print(sd.query_devices(device=sd.default.device[0]))
    print(sd.query_devices(device=sd.default.device[1]))


if __name__ == "__main__":
    test_1()
