import os
import pickle

import numpy as np

from basic.audioinfo import correct_sound, AudioInfo
from utils.utilalsa import read_wav_slow
from utils.utilconfig import find_path, ConfigName
from utils.utillog import MyLog


class SampleLoader:
    __instance = None
    _ACCENT_VOL = 1.2  # how much accent amplitude is bigger than non accent

    def __new__(cls):
        """ creates a singleton object """
        if not cls.__instance:
            cls.__instance = super(SampleLoader, cls).__new__(cls)
            cls.__instance.__initialized = False
        return cls.__instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True
        # sound names and loaded sound samples
        self._sounds: dict[str, np.ndarray] = dict()
        fname = find_path(ConfigName.pickled_drum_samples)
        if os.path.isfile(fname):
            with open(fname, 'rb') as f:
                try:
                    self._sounds = pickle.load(f)
                    sound = self._sounds['bd']
                    if sound.dtype != AudioInfo().SD_TYPE:
                        raise RuntimeError(f"Pickled sounds have wrong dtype: {sound.dtype}")
                    if sound.shape[1] != AudioInfo().SD_CH:
                        raise RuntimeError(f"Pickled sounds have wrong channels: {sound.shape[1]}")
                except Exception as ex:
                    self._sounds = dict()
                    MyLog().error(ex)

        if not self._sounds:
            self._sounds = self._load_audio_samples(find_path('config/drum/wav'))
            try:
                with open(fname, 'wb') as f:
                    pickle.dump(self._sounds, f)
            except pickle.PicklingError as ex:
                MyLog().error(ex)
            MyLog().warning("Loaded drum sounds from WAV file")
        else:
            MyLog().warning("Loaded drum sounds from pickle file")

        m_amp = AudioInfo().MAX_SD_TYPE
        m_amp2 = m_amp * m_amp / 1000
        maximum: dict[str, float] = {k: round(v.max() / m_amp, 2) for k, v in self._sounds.items()}
        variance: dict[str, float] = {k: round(v.var() / m_amp2, 2) for k, v in self._sounds.items()}
        duration: dict[str, float] = {k: round(len(v) / AudioInfo().SD_RATE, 2) for k, v in self._sounds.items()}

        # _adjusted has normal and accented sound, used to change volume up/down, _sounds do not change
        self._adjusted: dict[str, tuple[np.ndarray, np.ndarray]] = dict()
        MyLog().debug(f"Loaded sounds:\nvariance:{variance}")
        MyLog().debug(f"Loaded sounds:\nduration:{duration}")
        MyLog().debug(f"Loaded sounds:\nmaximum:{maximum}")
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
            sound = read_wav_slow(full_fname, AudioInfo().SD_TYPE)
            sound = correct_sound(sound, AudioInfo().SD_CH, AudioInfo().SD_TYPE)
            assert sound.dtype == AudioInfo().SD_TYPE and sound.ndim == 2 and sound.shape[1] == AudioInfo().SD_CH
            result[fname[:-4]] = sound
        MyLog().info(f"Loaded samples from {len(result)} WAV files")
        return result

    def set_volume(self, vol: float) -> None:
        """ Set SampleLoader._adjusted volumes - normal and accented. SampleLoader._sounds stay unchanged """
        vol1 = vol * AudioInfo().DRUM_VOLUME
        vol2 = vol1 * self._ACCENT_VOL
        self._adjusted = {k: ((v * vol1).astype(AudioInfo().SD_TYPE), (v * vol2).astype(AudioInfo().SD_TYPE))
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
