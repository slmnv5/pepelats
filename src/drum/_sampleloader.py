import os
import sys
import wave

import numpy as np

from utils.utilconfig import SD_TYPE, find_path, MAX_SD_TYPE
from utils.utillog import get_my_log

my_log = get_my_log(__name__)

# how much accent amplitude is bigger
_ACCENT_FACTOR = 1.2


def _adjust_volume(vol: float, sounds: dict[str, np.ndarray]) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    v1 = vol * MAX_SD_TYPE
    v2 = v1 * _ACCENT_FACTOR
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
        result[fname[:-4]] = sound
    return result


class SampleLoader:
    _MAX_AMPLITUDE = 0.5
    # sound name and sound samples, never change
    _sounds = _load_audio_samples(find_path("config/drum/wav"))
    maxes: dict[str, float] = {k: round(v.max(initial=0.01), 2) for k, v in _sounds.items()}
    for k, v in _sounds.items():
        _sounds[k] = v * (_MAX_AMPLITUDE / maxes[k])  # make max amplitude equal for all sounds

    volumes: dict[str, float] = {k: round(1000 * v.var(), 2) for k, v in _sounds.items()}
    maxes: dict[str, float] = {k: round(v.max(initial=0.01), 2) for k, v in _sounds.items()}

    # _adjusted is for changing volume up and down, _sounds does not change
    _adjusted = _adjust_volume(0.7, _sounds)
    my_log.debug(f"Loaded sounds:\nvolumes:{volumes}\nmaxes:{maxes}")

    @classmethod
    def set_volume(cls, volume: float) -> None:
        cls._adjusted = _adjust_volume(volume, cls._sounds)

    @classmethod
    def get_sound(cls, snd: str, accent: bool) -> np.ndarray:
        if snd in cls._adjusted:
            if accent:
                return cls._adjusted[snd][1]
            else:
                return cls._adjusted[snd][0]

    @classmethod
    def get_sound_names(cls) -> list[str]:
        return list(cls._adjusted.keys())
