from drum.basedrum import BaseDrum
from drum.bufferdrum import EuclidDrum, StyleDrum
from drum.loopdrum import LoopDrum
from drum.mididrum import MidiDrum
from utils.util_name import AppName


def drum_create(bar_len: int, drum_info: dict) -> BaseDrum:
    drum_type: str = drum_info.get(AppName.drum_type, AppName.StyleDrum)

    if drum_type == AppName.EuclidDrum:
        drum = EuclidDrum()
    elif drum_type == AppName.StyleDrum:
        drum = StyleDrum()
    elif drum_type == AppName.MidiDrum:
        drum = MidiDrum()
    elif drum_type == AppName.LoopDrum:
        drum = LoopDrum(drum_info[AppName.song_part])
    else:
        raise RuntimeError(f"Drum type is incorrect: {drum_type}")

    config: str = drum_info.get(AppName.drum_config_file)
    if config:
        drum.set_config(config)
    volume = drum_info.get(AppName.drum_volume)
    if volume:
        drum.set_volume(volume)
    par = drum_info.get(AppName.drum_param)
    if par:
        drum.set_param(par)
    if bar_len:
        drum.set_bar_len(bar_len)

    return drum
