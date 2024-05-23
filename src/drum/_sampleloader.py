import os
import sys
import wave

import numpy as np

from utils.utilconfig import SD_TYPE, find_path, MAX_SD_TYPE, SD_RATE, OUT_CH
from utils.utillog import get_my_log

my_log = get_my_log(__name__)

ACCENT_FACTOR = 1.2  # how much accent amplitude is bigger than non accent
_INIT_AMPLITUDE: float = 0.7


def _adjust_volume(vol: float, sounds: dict[str, np.ndarray]) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    v1 = vol * MAX_SD_TYPE
    v2 = v1 * ACCENT_FACTOR
    return {k: ((v * v1).astype(SD_TYPE), (v * v2).astype(SD_TYPE)) for k, v in sounds.items()}


def _read_wav_slow(fname):
    """ slow reading using wave module, avoids import of specialized modules """
    assert os.path.isfile(fname)
    with wave.open(fname, "rb") as f:
        nchannels, sampwidth, framerate, nframes, _, _ = f.getparams()
        buffer = f.readframes(-1)
    try:
        signed = sampwidth > 1  # 8 bit wavs are unsigned
        byteorder = sys.byteorder  # wave module uses sys.byteorder for bytes
        sz = sampwidth * nchannels
        frames = (buffer[i * sz: (i + 1) * sz] for i in range(nframes))
        values = []  # e.g. for stereo, values[i] = [left_val, right_val]
        for frame in frames:
            channel_vals = []  # mono has 1 channel, stereo 2, etc.
            for channel in range(nchannels):
                as_bytes = frame[channel * sampwidth: (channel + 1) * sampwidth]
                as_int = int.from_bytes(as_bytes, byteorder, signed=signed)
                channel_vals.append(as_int)
            values.append(channel_vals)

        nparray = np.array(values)
        factor: float = 1. / (2 ** (sampwidth * 8 - 1))
        nparray = (nparray * factor)
        if nparray.shape[1] < 2:
            nparray = np.column_stack((nparray, nparray))
        return nparray
    except Exception as ex:
        raise RuntimeError(f"Error: {ex} opening: {fname} params: {f.getparams()}")


def _load_audio_samples(dname: str) -> dict[str, np.ndarray]:
    """Loads WAV sounds, return dict of float samples from -1 to +1  """
    assert os.path.isdir(dname), dname
    result = dict()
    for fname in [x for x in os.listdir(dname) if x.endswith('.wav')]:
        full_fname = dname + os.sep + fname
        assert os.path.isfile(full_fname)
        sound = _read_wav_slow(full_fname)
        assert sound.dtype == np.float64 and np.max(sound) < 1 and sound.shape[1] == 2
        if OUT_CH == 1:
            # mono output is set for mono input
            sound = sound[:, 0]
        result[fname[:-4]] = sound
    my_log.info(f"Loaded samples from {len(result)} WAV files")
    return result


class SampleLoader:
    # sound name and loaded sound samples
    _sounds = _load_audio_samples(find_path("config/drum/wav"))
    _maxes: dict[str, float] = {k: round(v.max(initial=0.01), 2) for k, v in _sounds.items()}
    _ampl_factor: float = _INIT_AMPLITUDE / ACCENT_FACTOR / max(_maxes.values())
    # normalize amplitudes so that when volume == 1 there is no clipping
    for k, v in _sounds.items():
        _sounds[k] = v * _ampl_factor
    _variances: dict[str, float] = {k: round(1000 * v.var(), 2) for k, v in _sounds.items()}
    _durations: dict[str, float] = {k: round(len(v) / SD_RATE, 2) for k, v in _sounds.items()}

    # _adjusted are for changing volume up and down, _sounds do not change
    _adjusted = _adjust_volume(0.7, _sounds)
    my_log.debug(f"Loaded sounds:\nvariances:{_variances}")
    my_log.debug(f"Loaded sounds:\ndurations:{_durations}")
    my_log.debug(f"Loaded sounds:\nmaximums:{_maxes}")

    @classmethod
    def set_volume(cls, volume: float) -> None:
        cls._adjusted = _adjust_volume(volume, cls._sounds)

    @classmethod
    def get_sound(cls, sname: str, is_accent: bool) -> np.ndarray:
        if sname in cls._adjusted:
            if is_accent:
                return cls._adjusted[sname][1]
            else:
                return cls._adjusted[sname][0]

    @classmethod
    def get_power(cls, sname: str) -> float:
        return cls._variances.get(sname) * cls._durations.get(sname)

    @classmethod
    def get_sound_names(cls) -> list[str]:
        return list(cls._adjusted.keys())
