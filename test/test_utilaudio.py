import sounddevice as sd

from utils.utilaudio import SD_TYPE, SD_CH


def test_1():
    print(f"Default device type: {SD_TYPE}, chanels: {SD_CH}")
    print(sd.query_devices(device=sd.default.device[0]))
    print(sd.query_devices(device=sd.default.device[1]))


if __name__ == "__main__":
    test_1()
