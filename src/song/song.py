import os
import pickle

from control.loopctrl import LoopCtrl
from drum.drumfactory import create_drum
from drum.loopdrum import LoopDrum
# noinspection PyUnresolvedReferences
from song.songpart import SongPart
from utils.utilconfig import find_path
from utils.utillog import MYLOG
from utils.utilname import generate_name
from utils.utilother import FileFinder, CollectionOwner


class Song(CollectionOwner[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self, ctrl: LoopCtrl, load_song: bool):
        CollectionOwner.__init__(self, SongPart())
        self._name: str = ""
        self._ctrl: LoopCtrl = ctrl
        self._ff = FileFinder(find_path(".save_song"), True, ".sng")
        if load_song and self._ff.item_from_idx(-1):  # there is saved song
            try:
                self.load_song()
                return  # loaded latest saved song
            except Exception as ex:
                MYLOG.exception(ex)
                song_dir = find_path(".save_song")
                fname = self._ff.get_item()
                os.system(f"mkdir {song_dir}/bad")
                os.system(f"mv -v {song_dir}/{fname} {song_dir}/bad/")
                MYLOG.error(f"Moved song to 'bad' sub directory: {fname}")

        while self.item_count() < 4:
            self.idx_from_item(SongPart())

    def get_name(self) -> str:
        if not self._name:
            self._name = generate_name()
        assert self._name.count(".") == 0
        assert self._name.count("_") == 1
        return self._name

    def get_complete_name(self) -> str:
        drum = self._ctrl.get_drum()
        cls = drum.get_class_name()[0]
        cfg = drum.get_config()[:-4]
        cfg = '-' if not cfg else cfg
        return f"{self.get_name()}.{cls}.{cfg}.sng"

    def save_song(self) -> None:
        drum = self._ctrl.get_drum()
        self._ff.idx_from_item(self.get_complete_name())
        fname = self._ff.get_full_name()
        parts_lst = list()
        self.apply_to_each(lambda x: parts_lst.append(None if x.is_empty else x))
        drum_type = drum.get_class_name()
        drum_info = drum.get_pickle_info()
        with open(fname, 'wb') as f:
            pickle.dump((parts_lst, drum_type, drum_info), f)

        MYLOG.info(f"Saved song file: {fname}")

    def load_song(self) -> None:
        self._name = self._ff.get_item().split(".")[0]
        fname = self._ff.get_full_name()
        MYLOG.info(f"Loading song file: {fname}")
        part_lst: list[SongPart | None]
        with open(fname, 'rb') as f:
            parts_lst, drum_type, drum_info = pickle.load(f)

        # saved song may have different audio format and channels
        for part in [x for x in parts_lst if x]:
            part.correct_buffer()

        parts_lst = [x if x else SongPart() for x in parts_lst]
        drum = create_drum(drum_type)
        drum.set_pickle_info(drum_info)
        self._ctrl.set_drum(drum)

        for part in parts_lst:
            self.idx_from_item(part)

        self.item_from_idx(0)
        while self.item_count() > len(parts_lst):
            self.delete_selected()

        if isinstance(drum, LoopDrum) and not drum.songpart:
            drum.songpart = self.item_from_idx(0)

    def save_new_song(self) -> None:
        self._name = ""
        self.save_song()

    def show_songs(self) -> str:
        return self._ff.get_str()

    def delete_song(self) -> None:
        self._ff.delete_selected()

    def iterate_song(self, steps: int) -> None:
        self._ff.iterate(steps=steps)
