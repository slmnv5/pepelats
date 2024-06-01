from drum._bufferdrum import EuclidPtrnDrum, OldPtrnDrum
from drum._loopdrum import LoopDrum
from drum._mididrum import MidiDrum
from drum.basedrum import BaseDrum
from utils.utilconfig import ConfigName
from utils.utillog import MYLOG


class DrumFactory:
    @staticmethod
    def create_drum(bar_len: int, drum_type: str, **kwargs) -> BaseDrum:
        drum: BaseDrum
        if drum_type == ConfigName.EuclidPtrnDrum:
            drum = EuclidPtrnDrum()
        elif drum_type == ConfigName.OldPtrnDrum:
            drum = OldPtrnDrum()
        elif drum_type == ConfigName.MidiDrum:
            drum = MidiDrum()
        elif drum_type == ConfigName.LoopDrum:
            drum = LoopDrum(kwargs.get(ConfigName.drum_songpart))
        else:
            raise RuntimeError(f"Unknown drum type: {drum_type}")

        config: str = kwargs.get(ConfigName.drum_config)
        drum.set_config(config)
        drum.set_bar_len(bar_len)

        volume: float = kwargs.get(ConfigName.drum_volume)
        if volume:
            drum.set_volume(volume)
        par: float = kwargs.get(ConfigName.drum_par)
        if par:
            drum.set_par(par)
        MYLOG.info(f"Created drum: {drum}")
        return drum
