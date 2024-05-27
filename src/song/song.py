import os.path
import pickle

from buffer.loopctrl import LoopCtrl
from drum.drumfactory import create_drum
from drum.loopdrum import LoopDrum
# noinspection PyUnresolvedReferences
from song.songpart import SongPart
from utils.utilaudio import AUDIO
from utils.utilconfig import find_path
from utils.utillog import MyLog
from utils.utilname import generate_name
from utils.utilother import FileFinder, CollectionOwner

my_log = MyLog()


class Song(CollectionOwner[SongPart]):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self, ctrl: LoopCtrl, load_song: bool = False):
        CollectionOwner.__init__(self, SongPart())
        self._name: str = ""
        self._ctrl: LoopCtrl = ctrl
        self._ff = FileFinder(find_path(".save_song"), True, "")
        if not load_song or not self._ff.item_from_idx(-1):  # no saved song
            while self.item_count() < 4:
                self.idx_from_item(SongPart())
        else:
            self.load_song()  # there is latest song saved

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
        return f"{self.get_name()}.{cls}.{cfg}"

    def save_song(self) -> None:
        drum = self._ctrl.get_drum()
        self._ff.idx_from_item(self.get_complete_name())
        fname = self._ff.get_full_name()
        parts_lst = list()
        self.apply_to_each(lambda x: parts_lst.append(None if x.is_empty else x))
        drum_type = drum.get_class_name()
        drum_info = drum.get_pickle()
        audio_info = f"{AUDIO.SD_TYPE}{AUDIO.SD_CH}"
        with open(fname, 'wb') as f:
            pickle.dump((parts_lst, drum_type, drum_info, audio_info), f)

        my_log.info(f"Saved song file: {fname}")

    def load_song(self) -> None:
        self._name = self._ff.get_item().split(".")[0]
        fname = self._ff.get_full_name()
        if not os.path.isfile(fname):
            my_log.error(f"Song file not found: {fname}")
            return

        with open(fname, 'rb') as f:
            parts_lst, drum_type, drum_info, audio_info = pickle.load(f)

        # saved song may have different audio format and channels
        need_fix: bool = f"{AUDIO.SD_TYPE}{AUDIO.SD_CH}" != audio_info
        parts_lst: list[SongPart] = \
            [(x.correct_buffer(AUDIO.SD_CH, AUDIO.SD_TYPE) if need_fix else x)
             if x is not None else SongPart() for x in parts_lst[0:4]]
        assert parts_lst
        drum = create_drum(drum_type)
        self._ctrl.set_drum(drum)
        drum.set_pickle(drum_info)
        for part in parts_lst:
            self.idx_from_item(part)

        self.item_from_idx(0)
        while self.item_count() > len(parts_lst):
            self.delete_selected()

        if isinstance(drum, LoopDrum) and not drum.songpart:
            drum.songpart = self.item_from_idx(0)

        my_log.info(f"Loaded song file: {fname}")

    def save_new_song(self) -> None:
        self._name = ""
        self.save_song()

    def show_songs(self) -> str:
        return self._ff.get_str()

    def delete_song(self) -> None:
        self._ff.delete_selected()

    def iterate_song(self, steps: int) -> None:
        self._ff.iterate(steps=steps)
