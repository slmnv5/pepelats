import pickle

from drum.basedrum import BaseDrum
# noinspection PyUnresolvedReferences
from song.songpart import SongPart
from utils.util_drum import drum_create
from utils.util_log import MY_LOG
from utils.util_menu import PARTS
from utils.util_name import AppName, song_name_generate
from utils.util_other import FileFinder, CollectionOwner
from utils.util_screen import SCR_ROWS


class Song:
    """Song keeps SongParts as CollectionOwner, can save and load from file"""
    ff = FileFinder(AppName.save_song, True, ".sng")

    def __init__(self):
        self.parts: CollectionOwner[SongPart] = CollectionOwner[SongPart](SongPart())
        while self.parts.item_count() < PARTS:
            self.parts.add_item(SongPart())
        self._name: str = song_name_generate()

    def clear(self) -> None:
        self.parts.for_each(lambda x: x.clear() if not x.is_empty() else None)
        self.parts.select_idx(0)
        self._name = song_name_generate()

    def get_complete_name(self, drum: BaseDrum) -> str:
        drum_type = drum.get_class_name()[0]
        return f"{self._name}.{drum_type}.sng"

    @staticmethod
    def show_list() -> str:
        return Song.ff.get_str(SCR_ROWS - 5)

    @staticmethod
    def delete_song() -> None:
        Song.ff.delete_item()

    @staticmethod
    def iterate_song(steps: int) -> None:
        Song.ff.iterate(steps=steps)


def load_song_drum() -> tuple[Song, BaseDrum]:
    song = Song()
    song._name = Song.ff.get_item().split(".")[0]
    fname = Song.ff.get_full_name()
    MY_LOG.info(f"Loading song file: {fname}")
    part_lst: list[SongPart | None]
    with open(fname, 'rb') as f:
        parts_lst, bar_len, drum_info = pickle.load(f)

    # saved song may have different basic format and channels
    for part in [x for x in parts_lst if x]:
        part.correct_buffer()

    parts_lst = [x if x else SongPart() for x in parts_lst[:PARTS]]
    for part in parts_lst:
        song.parts.add_item(part)

    song.parts.select_idx(0)
    while song.parts.item_count() > len(parts_lst):
        song.parts.delete_item()

    drum_info[AppName.song_part] = song.parts.get_first()
    drum = drum_create(bar_len, drum_info)
    return song, drum


def save_song_drum(song: Song, drum: BaseDrum) -> None:
    Song.ff.add_item(song.get_complete_name(drum))
    fname = Song.ff.get_full_name()
    parts_lst = list()
    song.parts.for_each(lambda x: parts_lst.append(None if x.is_empty() else x))
    bar_len = drum.get_bar_len()
    drum_info = drum.get_drum_info()

    with open(fname, 'wb') as f:
        pickle.dump((parts_lst, bar_len, drum_info), f)

    MY_LOG.info(f"Saved song file: {fname}")
