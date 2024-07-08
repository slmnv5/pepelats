import os

import numpy as np

from basic.audioinfo import correct_sound, AUDIO_INFO
from utils.utilalsa import read_wav_slow
from utils.utilconfig import find_path, SD_RATE
from utils.utillog import MYLOG


class SampleLoader:
    __instance = None
    _ACCENT_VOL = 1.2  # how much accent amplitude is bigger than non accent

    def __new__(cls):
        """ creates a singleton object, if it is not created, else returns existing """
        if not cls.__instance:
            cls.__instance = super(SampleLoader, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        # sound names and loaded sound samples
        self._sounds: dict[str, np.ndarray] = self._load_audio_samples(find_path("config/drum/wav"))
        maximum: dict[str, float] = {k: round(v.max() / AUDIO_INFO.MAX_SD_TYPE, 2) for k, v in self._sounds.items()}
        variance: dict[str, float] = {k: round(1000 * v.var() / (AUDIO_INFO.MAX_SD_TYPE ** 2), 2) for k, v in
                                      self._sounds.items()}
        duration: dict[str, float] = {k: round(len(v) / SD_RATE, 2) for k, v in self._sounds.items()}

        # _adjusted has normal and accented sound, used to change volume up/down, _sounds do not change
        self._adjusted: dict[str, tuple[np.ndarray, np.ndarray]] = dict()
        MYLOG.debug(f"Loaded sounds:\nvariance:{variance}")
        MYLOG.debug(f"Loaded sounds:\nduration:{duration}")
        MYLOG.debug(f"Loaded sounds:\nmaximum:{maximum}")
        # _energy has energy of each drum sound = variance * duration
        self._energy = {k: variance[k] * duration[k] for k in self._sounds}
        self.set_volume(1.0)

    @staticmethod
    def _load_audio_samples(dname: str) -> dict[str, np.ndarray]:
        """Loads WAV sounds, return dict of float samples from -1 to +1  """
        assert os.path.isdir(dname), dname
        result = dict()
        for fname in [x for x in os.listdir(dname) if x.endswith('.wav')]:
            full_fname = dname + os.sep + fname
            assert os.path.isfile(full_fname)
            sound = read_wav_slow(full_fname, AUDIO_INFO.SD_TYPE)
            sound = correct_sound(sound, AUDIO_INFO.SD_CH, AUDIO_INFO.SD_TYPE)
            assert sound.dtype == AUDIO_INFO.SD_TYPE and sound.ndim == 2 and sound.shape[1] == AUDIO_INFO.SD_CH
            result[fname[:-4]] = sound
        MYLOG.info(f"Loaded samples from {len(result)} WAV files")
        return result

    def set_volume(self, vol: float) -> None:
        """ Set SampleLoader._adjusted volumes - normal and accented. SampleLoader._sounds stay unchanged """
        vol1 = vol * AUDIO_INFO.DRUM_VOLUME
        vol2 = vol1 * self._ACCENT_VOL
        self._adjusted = {k: ((v * vol1).astype(AUDIO_INFO.SD_TYPE), (v * vol2).astype(AUDIO_INFO.SD_TYPE))
                          for k, v in self._sounds.items()}

    def get_sound(self, sname: str, is_accent: bool) -> np.ndarray:
        if sname in self._adjusted:
            if is_accent:
                return self._adjusted[sname][1]
            else:
                return self._adjusted[sname][0]

    def get_energy(self, sname: str, is_accent: bool) -> float:
        factor = self._ACCENT_VOL ** 2 if is_accent else 1
        return self._energy[sname] * factor

    def get_sound_names(self) -> list[str]:
        return list(self._sounds.keys())
