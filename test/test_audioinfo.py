import sounddevice as sd

from basic.audioinfo import AudioInfo


def test_1():
    print(f"Default device type: {AudioInfo().SD_TYPE}, channels: {AudioInfo().SD_CH}")
    print(sd.query_devices(device=sd.default.device[0]))
    print(sd.query_devices(device=sd.default.device[1]))
