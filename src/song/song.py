import os
import pickle

from control.loopctrl import LoopCtrl
# noinspection PyUnresolvedReferences
from song.songpart import SongPart
from utils.utilconfig import find_path, ConfigName
from utils.utillog import MYLOG
from utils.utilname import generate_name
from utils.utilother import FileFinder, CollectionOwner


class Song(CollectionOwner[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""
    SONG_PARTS: int = 4

    def __init__(self, ctrl: LoopCtrl, load_song: bool):
        tmp = [SongPart(1), SongPart(1), SongPart(1), SongPart(1)]
        CollectionOwner.__init__(self, tmp)
        self._name: str = ""
        self._ctrl: LoopCtrl = ctrl
        self._ff = FileFinder(find_path(".save_song"), True, ".sng")
        if load_song and self._ff.get_at_idx(-1):  # latest song
            self.select_idx(-1)
            self.load_song()
        else:
            self.clear()

    def clear(self) -> None:
        for k in range(self.item_count()):
            if not self.get_at_idx(k).is_empty:
                self.set_at_idx(k, SongPart())
        self.select_idx(0)
        self._name = generate_name()

    def get_complete_name(self) -> str:
        drum_type = self._ctrl.get_drum().get_class_name()[0]
        return f"{self._name}.{drum_type}.sng"

    def save_song(self) -> None:
        drum = self._ctrl.get_drum()
        self._ff.idx_from_item(self.get_complete_name())
        fname = self._ff.get_full_name()
        parts_lst = list()
        self.apply_to_each(lambda x: parts_lst.append(None if x.is_empty else x))
        drum_info: dict[str, any] = dict()
        drum_type = drum.get_class_name()
        bar_len = drum.get_bar_len()
        drum_info[ConfigName.drum_config] = drum.get_config()
        drum_info[ConfigName.drum_volume] = drum.get_volume()
        drum_info[ConfigName.drum_par] = drum.get_par()

        with open(fname, 'wb') as f:
            pickle.dump((parts_lst, bar_len, drum_type, drum_info), f)

        MYLOG.info(f"Saved song file: {fname}")

    def load_song(self) -> None:
        self._name = self._ff.get_item().split(".")[0]
        fname = self._ff.get_full_name()
        MYLOG.info(f"Loading song file: {fname}")
        part_lst: list[SongPart | None]
        with open(fname, 'rb') as f:
            parts_lst, bar_len, drum_type, drum_info = pickle.load(f)

        # saved song may have different basic format and channels
        for part in [x for x in parts_lst if x]:
            part.correct_buffer()

        parts_lst = [x if x else SongPart() for x in parts_lst]
        self._ctrl.menu_client_queue([ConfigName.drum_create, bar_len, drum_type, drum_info])

        for part in parts_lst:
            self.idx_from_item(part)

        self.select_idx(0)
        while self.item_count() > len(parts_lst):
            self.delete_selected()

    def show_songs(self) -> str:
        return self._ff.get_str()

    def delete_song(self) -> None:
        self._ff.delete_selected()

    def iterate_song(self, steps: int) -> None:
        self._ff.iterate(steps=steps)

    def _disable_failed_song(self) -> None:
        fname = self._ff.get_full_name()
        cmd = f"{'mv' if os.name == 'posix' else 'move'} {fname} {fname}.bad"
        os.system(f"{cmd}")
        if not os.path.isfile(fname):
            self._ff.delete_selected()
            MYLOG.error(f"Failed to load and disabled song: {fname}.bad")
