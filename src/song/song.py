import os.path
import pickle
from collections.abc import Iterable

from buffer.loopctrl import LoopCtrl
# noinspection PyUnresolvedReferences
from song.songpart import SongPart

from utils.utilconfig import find_path
from utils.utilfactory import create_drum
from utils.utillog import get_my_log
from utils.utilname import generate_name
from utils.utilother import FileFinder, CollectionOwner

my_log = get_my_log(__name__)


class Song(CollectionOwner[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self, first: SongPart | Iterable[SongPart]):
        CollectionOwner.__init__(self, first)
        self._name: str = ""
        self._ff = FileFinder(find_path(".save_song"), True, "")

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
        self._ff.idx_from_item(self.get_complete_name(ctrl))
        fname = self._ff.get_full_name()
        parts_lst = list()
        self.apply_to_each(lambda x: parts_lst.append(None if x.is_empty else x))
        assert parts_lst
        with open(fname, 'wb') as f:
            pickle.dump((parts_lst, dr.get_class_name(), dr.get_config(),
                         dr.get_bar_len(), dr.get_volume(), dr.get_par()), f)

        my_log.info(f"Saved song file: {fname}")

    def load_song(self, ctrl: LoopCtrl) -> None:
        self._name = self._ff.get_item().split(".")[0]
        fname = self._ff.get_full_name()
        if not os.path.isfile(fname):
            my_log.error(f"Song file not found: {fname}")
            return

        with open(fname, 'rb') as f:
            parts_lst, drum_type, config, bar_len, volume, par = pickle.load(f)

        parts_lst = [x if x is not None else SongPart() for x in parts_lst[0:4]]
        assert parts_lst
        assert isinstance(bar_len, int), f"{bar_len}"
        assert isinstance(volume, float) and 0 <= volume <= 1, f"{volume}"
        assert isinstance(par, float) and 0 <= par <= 1, f"{par}"

        kwargs = {"SongPart": parts_lst[0]}
        dr = create_drum(drum_type, **kwargs)
        dr.set_config(config)
        dr.load_config(bar_len)
        dr.set_volume(volume)
        dr.set_par(par)
        ctrl.set_drum(dr)
        for part in parts_lst:
            self.idx_from_item(part)
        self.item_from_idx(0)
        while self.item_count() > len(parts_lst):
            self.delete_selected()

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
