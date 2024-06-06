import sounddevice as sd

from basic.audioinfo import AUDIO_INFO


def test_1():
    print(f"Default device type: {AUDIO_INFO.SD_TYPE}, channels: {AUDIO_INFO.SD_CH}")
    print(sd.query_devices(device=sd.default.device[0]))
    print(sd.query_devices(device=sd.default.device[1]))


if __name__ == "__main__":
    test_1()
