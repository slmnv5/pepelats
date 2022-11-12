# noinspection PyUnusedLocal


class MockedMixer:
    """Used to run on windows, there is no ALSA sound on windows"""

    def __init__(self):
        self.__vol_in: int = 100
        self.__vol_out: int = 100

    def fade(self, seconds: int) -> None:
        pass

    def setvolume(self, vol: int, out: bool):
        if vol > 100 or vol < 0:
            return
        if out:
            self.__vol_out = vol
        else:
            self.__vol_in = vol

    def getvolume(self, out: bool):
        if out:
            return self.__vol_out
        else:
            return self.__vol_in

    def change_volume(self, change_by: int, out: bool):
        self.setvolume(self.getvolume(out) + change_by, out)

    def __str__(self):
        return f"{self.__class__.__name__} out {self.getvolume(True)} in {self.getvolume(False)}"


if __name__ == "__main__":
    def test():
        mmix = MockedMixer()
        print(mmix.getvolume(True), mmix.getvolume(False))


    test()
