import time
from typing import List

# noinspection PyUnresolvedReferences
import alsaaudio

from utils import LOGR
from mixer._mockedmixer import MockedMixer
from utils import ConfLoader, ConfigName


# noinspection PyBroadException
def info(mixer: alsaaudio.Mixer) -> str:
    lst: List[str] = []
    func_dic = {"name": alsaaudio.Mixer.cls_mixer, "id": alsaaudio.Mixer.mixerid,
                "switching": alsaaudio.Mixer.switchcap, "volume": alsaaudio.Mixer.volumecap,
                "mute": alsaaudio.Mixer.getmute, "record": alsaaudio.Mixer.getrec}
    for key, func in func_dic.items():
        try:
            lst.append(key + "=" + str(func(mixer)) + "\t")
        except Exception:
            pass
    return str(lst)


def find_mixer(names_list: List[str], all_mixers_list: List[str]) -> alsaaudio.Mixer:
    mixer = FakeMixer()
    for mixer_name in names_list:
        if mixer_name in all_mixers_list:
            mixer = alsaaudio.Mixer(mixer_name)
            break

    return mixer


# noinspection PyUnusedLocal
class FakeMixer:
    """Used if sound card does not have specific mixer"""

    def __init__(self):
        self.__vol: int = 80

    def setvolume(self, vol: int, *args):
        vol = min(100, vol)
        vol = max(0, vol)
        self.__vol = vol

    def getvolume(self, *args) -> int:
        return self.__vol


# noinspection PyBroadException,PyArgumentList
class AlsaMixer(MockedMixer):
    def __init__(self):
        super().__init__()

        all_mixers_list = alsaaudio.mixers()
        self.__out = find_mixer(["Master", "PCM", "Speaker"], all_mixers_list)
        self.__out.setvolume(ConfLoader.get(ConfigName.mixer_out, 100))

        self.__in = find_mixer(["Mic"], all_mixers_list)
        self.__in.setvolume(ConfLoader.get(ConfigName.mixer_in, 50))

        LOGR.info(f"Found mixers: {alsaaudio.mixers()}, info: {str(self)}")

    def fade(self, seconds: int) -> None:
        new_volume = save_volume = self.getvolume(out=True)
        for _ in range(seconds):
            time.sleep(1)
            new_volume -= save_volume // seconds
            self.__out.setvolume(new_volume)
        self.__out.setvolume(save_volume)

    def setvolume(self, vol: int, out: bool):
        if vol > 100 or vol < 0:
            return
        if out:
            self.__out.setvolume(vol)
            ConfLoader.set(ConfigName.mixer_out, vol)
        else:
            self.__in.setvolume(vol, alsaaudio.MIXER_CHANNEL_ALL, alsaaudio.PCM_CAPTURE)
            ConfLoader.set(ConfigName.mixer_in, vol)

    def getvolume(self, out: bool):
        if out:
            vol = self.__out.getvolume()
        else:
            vol = self.__in.getvolume(alsaaudio.PCM_CAPTURE)
        try:
            # noinspection PyUnresolvedReferences
            return vol[0]
        except TypeError:
            return vol

    def change_volume(self, change_by: int, out: bool):
        new_vol = self.getvolume(out) + change_by
        self.setvolume(new_vol, out)

    def __str__(self):
        return f"{self.__class__.__name__} out {self.getvolume(True)} in {self.getvolume(False)}"


if __name__ == "__main__":
    pass
