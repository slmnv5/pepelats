import os.path
import pickle

from buffer.loopctrl import LoopCtrl
# noinspection PyUnresolvedReferences
from song.songpart import SongPart

from utils.utilconfig import find_path
from utils.utilfactory import create_drum
from utils.utillog import get_my_log
from utils.utilname import generate_name
from utils.utilother import FileFinder, CollectionOwner

my_log = get_my_log(__name__)


class Song:
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self, ctrl: LoopCtrl):
        self._name: str = ""
        self.parts = CollectionOwner[SongPart](SongPart())
        self._ff = FileFinder(find_path(".save_song"), True, "")
        if not self._ff.set_item(0):
            self.save_song(ctrl)

    def load_latest(self, ctrl: LoopCtrl):
        self._ff.set_item(-1)
        try:
            self.load_song(ctrl)  # load latest saved song
        except Exception as ex:
            my_log.error(f"Error: {ex} loading saved song: {self._name}")

    def get_name(self) -> str:
        if not self._name:
            self._name = generate_name()
        assert self._name.count(".") == 0
        assert self._name.count("_") == 1
        return self._name

    def get_complete_name(self, ctrl: LoopCtrl) -> str:
        dr = ctrl.get_drum()
        cls = dr.get_class_name()[0]
        cfg = dr.get_config()[:-4]
        return f"{self.get_name()}.{cls}.{cfg}"

    def save_song(self, ctrl: LoopCtrl) -> None:
        dr = ctrl.get_drum()
        self._ff.add_item(self.get_complete_name(ctrl))
        fname = self._ff.get_full_name()
        save_list = list()
        self.parts.apply_to_each(lambda x: save_list.append(None if x.is_empty else x))
        assert save_list
        tpl = dr.get_class_name(), dr.get_config(), dr.get_bar_len(), dr.get_volume(), dr.get_par()

        with open(fname, 'wb') as f:
            pickle.dump((save_list, *tpl), f)

        my_log.info(f"Saved song file: {fname}")

    def load_song(self, ctrl: LoopCtrl) -> None:
        self._name = self._ff.get_item().split(".")[0]
        fname = self._ff.get_full_name()
        if not os.path.isfile(fname):
            my_log.error(f"File not found: {fname}")
            return

        with open(fname, 'rb') as f:
            load_list, drum_type, config, bar_len, volume, par = pickle.load(f)

        load_list = [x if x is not None else SongPart() for x in load_list]
        while len(load_list) < 4:
            load_list.append(SongPart())
        assert len(load_list) >= 4
        assert all(type(p) == SongPart for p in load_list)
        assert type(bar_len) == int, f"{bar_len}"
        assert type(volume) == float and 0 <= volume <= 1, f"{volume}"
        assert type(par) == float and 0 <= par <= 1, f"{par}"

        kwargs = {"SongPart": load_list[0]}
        dr = create_drum(drum_type, **kwargs)
        dr.load_drum_config(config, bar_len)
        dr.set_volume(volume)
        dr.set_par(par)
        ctrl.set_drum(dr)
        for part in load_list:
            part.init_str()
        self.parts = CollectionOwner(load_list)
        my_log.info(f"Loaded song file: {fname}")

    def save_new_song(self, ctrl) -> None:
        self._name = ""
        self.save_song(ctrl)

    def show_songs(self) -> str:
        return self._ff.get_str()

    def delete_song(self) -> None:
        self._ff.delete_selected()

    def iterate_song(self, steps: int) -> None:
        self._ff.iterate(steps=steps)
