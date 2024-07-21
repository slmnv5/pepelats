import pickle

from control.loopctrl import LoopCtrl
# noinspection PyUnresolvedReferences
# noinspection PyUnresolvedReferences
from song.songpart import SongPart
from utils.util_log import MY_LOG
from utils.util_name import AppName
from utils.util_other import FileFinder, CollectionOwner, song_name_generate


class Song(CollectionOwner[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""
    SONG_PARTS: int = 4

    def __init__(self, ctrl: LoopCtrl):
        tmp = [SongPart(), SongPart(), SongPart(), SongPart()]
        CollectionOwner.__init__(self, tmp)
        self._name: str = song_name_generate()
        self._ctrl: LoopCtrl = ctrl
        self._ff = FileFinder(AppName.save_song, True, ".sng")

    def clear(self) -> None:
        for k, x in enumerate(self.get_list()):
            if not x.is_empty:
                self.set_at_idx(k, SongPart())
        self.select_idx(0)
        self._name = song_name_generate()

    def get_complete_name(self) -> str:
        drum_type = self._ctrl.get_drum().get_class_name()[0]
        return f"{self._name}.{drum_type}.sng"

    def save_song(self) -> None:
        drum = self._ctrl.get_drum()
        self._ff.add_item(self.get_complete_name())
        fname = self._ff.get_full_name()
        parts_lst = list()
        for x in self.get_list():
            parts_lst.append(None if x.is_empty else x)
        bar_len = drum.get_bar_len()
        drum_info = drum.get_drum_info()

        with open(fname, 'wb') as f:
            pickle.dump((parts_lst, bar_len, drum_info), f)

        MY_LOG.info(f"Saved song file: {fname}")

    def load_song(self) -> None:
        self._name = self._ff.get_item().split(".")[0]
        fname = self._ff.get_full_name()
        MY_LOG.info(f"Loading song file: {fname}")
        part_lst: list[SongPart | None]
        with open(fname, 'rb') as f:
            parts_lst, bar_len, drum_info = pickle.load(f)

        # saved song may have different basic format and channels
        for part in [x for x in parts_lst if x]:
            part.correct_buffer()

        parts_lst = [x if x else SongPart() for x in parts_lst]
        for part in parts_lst:
            self.add_item(part)

        self.select_idx(0)
        while self.item_count() > len(parts_lst):
            self.delete_selected()

        self._ctrl.drum_create(bar_len, **drum_info)

    def show_list(self) -> str:
        return self._ff.get_str()

    def delete_song(self) -> None:
        self._ff.delete_selected()

    def iterate_song(self, steps: int) -> None:
        self._ff.iterate(steps=steps)
