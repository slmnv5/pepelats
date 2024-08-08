import os
import pickle

import numpy as np

from utils.util_alsa import read_wav_slow
from utils.util_audio import correct_sound, AUDIO_INFO
from utils.util_log import MY_LOG
from utils.util_name import AppName


class SampleLoader:
    __instance = None
    _ACCENT = 1.2  # how much accent amplitude is bigger than non accent

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
        try:
            with open(AppName.pickled_drum_samples, 'rb') as f:
                self._sounds = pickle.load(f)
                sound = list(self._sounds.values())[0]
                if sound.dtype != AUDIO_INFO.SD_TYPE:
                    raise RuntimeError(f"Pickled drum samples have wrong dtype: {sound.dtype}")
                if sound.shape[1] != AUDIO_INFO.SD_CH:
                    raise RuntimeError(f"Pickled drum samples have wrong channels: {sound.shape[1]}")

            MY_LOG.info("Loaded drum samples from pickle file")
        except Exception as ex:
            MY_LOG.error(ex)
            self._sounds = self._load_audio_samples(AppName.drum_samples_dir)
            pickle.dump(self._sounds, f)
            MY_LOG.info("Loaded drum samples from WAV files")

        m_amp = AUDIO_INFO.MAX_SD_TYPE
        m_amp2, mln = m_amp * m_amp, 1_000_000
        max_lst = {v.max() * self._ACCENT / m_amp for v in self._sounds.values()}
        self._inner_vol = max(max_lst)  # (1 / self._inner_vol) max. increase without clipping
        variance = {k: round(v.var() / m_amp2 / mln, 2) for k, v in self._sounds.items()}
        duration = {k: round(len(v) / AUDIO_INFO.SD_RATE, 2) for k, v in self._sounds.items()}

        # _adjusted stores sounds (normal, accent) after volume change, original _sounds do not change
        self._adjusted: dict[str, tuple[np.ndarray, np.ndarray]] = dict()
        # _energy has energy of each drum sound
        self._energy = {k: variance[k] * duration[k] for k in self._sounds}

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
        MY_LOG.info(f"Loaded samples from {len(result)} WAV files")
        return result

    def set_volume(self, vol: float) -> None:
        """ Change _adjusted. _sounds stay unchanged """
        vol = 1 / self._inner_vol * vol  # vol = 1 on the verge of clipping
        self._adjusted = {k: ((v * vol).astype(AUDIO_INFO.SD_TYPE),
                              (v * vol * self._ACCENT).astype(AUDIO_INFO.SD_TYPE))
                          for k, v in self._sounds.items()}

    def get_sound(self, sname: str, is_accent: bool) -> np.ndarray:
        if sname in self._adjusted:
            if is_accent:
                return self._adjusted[sname][1]
            else:
                return self._adjusted[sname][0]

    def get_energy(self, sname: str, is_accent: bool) -> float:
        factor = self._ACCENT ** 2 if is_accent else 1
        return self._energy[sname] * factor

    def get_sound_names(self) -> list[str]:
        return list(self._sounds.keys())
