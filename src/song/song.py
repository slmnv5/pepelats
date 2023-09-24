import os.path
import pickle

from buffer.loopctrl import LoopCtrl
from song.songpart import SongPart
from utils.utilconfig import find_path
from utils.utilfactory import get_drum
from utils.utillog import get_my_log
from utils.utilname import generate_name
from utils.utilother import FileFinder, CollectionOwner

my_log = get_my_log(__name__)


class Song:
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self, ctrl: LoopCtrl):
        self._name: str = ""
        self.parts = CollectionOwner[SongPart](SongPart())
        self._ff = FileFinder(find_path("save_song"), True, "")
        if not self._ff.select_idx(0):
            self.save_song(ctrl)

    def load_latest(self, ctrl: LoopCtrl):
        self._ff.select_idx(-1)
        try:
            self.load_song(ctrl)  # load latest saved song
        except Exception as ex:
            my_log.error(f"Error: {ex} loading saved song: {self._name}")

    def get_name(self) -> str:
        return self._name

    def clear_name(self) -> None:
        self._name = ""

    def save_song(self, ctrl: LoopCtrl) -> None:
        dr = ctrl.get_drum()
        if not self._name:
            self._name = generate_name()
            cls = dr.get_class_name()[0]
            cfg = dr.get_config()[:-4]
            self._name += f".{cls}.{cfg}"
        self._ff.add_item(self._name)
        fname = self._ff.get_full_name()
        save_list = list()
        self.parts.apply_to_each(lambda x: save_list.append(None if x.is_empty else x))
        assert save_list
        tpl = dr.get_class_name(), dr.get_config(), dr.get_bar_len(), dr.get_volume(), dr.get_par()

        with open(fname, 'wb') as f:
            pickle.dump((save_list, *tpl), f)

        my_log.info(f"Saved song file: {fname}")

    def load_song(self, ctrl: LoopCtrl) -> None:
        self._name = self._ff.selected_item()
        fname = self._ff.get_full_name()
        if not os.path.isfile(fname):
            my_log.error(f"File not found: {fname}")
            return

        with open(fname, 'rb') as f:
            load_list, drum_type, config, bar_len, volume, par = pickle.load(f)

        load_list = [x if x is not None else SongPart() for x in load_list]
        assert load_list
        assert type(load_list[0]) == SongPart
        assert drum_type in ["LoopDrum", "AudioDrum", "MidiDrum", "EuclidDrum"]
        assert type(bar_len) == int, f"{bar_len}"
        assert type(volume) == float, f"{volume}"
        assert type(par) == float, f"{par}"

        kwargs = {"SongPart": load_list[0]}
        dr = get_drum(drum_type, **kwargs)
        dr.load_drum_config(config, bar_len)
        dr.set_volume(volume)
        dr.set_par(par)
        ctrl.set_drum(dr)
        self.parts = CollectionOwner(load_list)
        my_log.info(f"Loaded song file: {fname}")

    def save_new_song(self, ctrl) -> None:
        self._name = ""
        self.save_song(ctrl)

    def show_songs(self) -> str:
        idx = self._ff.find_item_idx(self._name)
        return self._ff.get_str(idx)

    def delete_song(self) -> None:
        self._ff.delete_selected()

    def iterate_song(self, steps: int) -> None:
        self._ff.iterate(steps=steps)
