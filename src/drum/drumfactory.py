from drum._bufferdrum import EuclidDrum, StyleDrum
from drum._loopdrum import LoopDrum
from drum._mididrum import MidiDrum
from drum.basedrum import BaseDrum
from utils.utilconfig import ConfigName
from utils.utillog import MYLOG


def create_drum(bar_len: int, **kwargs) -> BaseDrum:
    drum: BaseDrum
    drum_type: str = kwargs.get(ConfigName.drum_type, ConfigName.StyleDrum)
    if drum_type == ConfigName.EuclidDrum:
        drum = EuclidDrum()
    elif drum_type == ConfigName.StyleDrum:
        drum = StyleDrum()
    elif drum_type == ConfigName.MidiDrum:
        drum = MidiDrum()
    elif drum_type == ConfigName.LoopDrum:
        drum = LoopDrum(kwargs.get(ConfigName.drum_song_part))
    else:
        raise RuntimeError(f"Unknown drum type: {drum_type}")

    config: str = kwargs.get(ConfigName.drum_config)
    drum.set_config(config)

    volume: float = kwargs.get(ConfigName.drum_volume)
    if volume:
        drum.set_volume(volume)
    par: float = kwargs.get(ConfigName.drum_par)
    if par:
        drum.set_par(par)

    drum.set_bar_len(bar_len)
    drum.randomize()

    MYLOG.info(f"Created drum: {drum}")
    return drum
