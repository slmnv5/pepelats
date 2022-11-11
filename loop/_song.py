import os
import pickle
from abc import abstractmethod
from typing import Dict

from drum import RDRUM
from utils import LOGR
from loop._oneloopctrl import OneLoopCtrl
from loop._songpart import SongPart
from utils import FileFinder, CONFLDR, CollectionOwner, ConfigName
from utils import generate_name


class SongPartOwner(CollectionOwner[SongPart]):
    """Class for list of items and two indexes.
    It is parent for Song as it has 'now' and 'nxt' - two  parts """

    default_config: Dict = {
        "DRUM_SWING": 0.625,
        "DRUM_VOLUME": 0.5,
        "DRUM_TYPE": "pop",
        "MIXER_IN": 30,
        "MIXER_OUT": 99,
        "SONG_NAME": "first.s"
    }

    def __init__(self, first: SongPart):
        CollectionOwner.__init__(self, first)
        self.__id2: int = 0

    @property
    def id2(self) -> int:
        return self.__id2

    def get_item2(self) -> SongPart:
        return self._get_id(self.__id2)

    def align_ids(self) -> None:
        self.__id2 = self.id

    def find_empty_part_id(self) -> int:
        for k in range(self.item_count):
            if self._get_id(k).is_empty:
                return k
        return -1


class Song(SongPartOwner):
    """Song keeps SongParts as CollectionOwner, can save and load from file"""

    def __init__(self, first: SongPart):
        SongPartOwner.__init__(self, first)
        self._file_finder: FileFinder = FileFinder("save_song", True, ".s")

    @abstractmethod
    def _stop_song(self, wait: int = 0) -> None:
        pass

    @abstractmethod
    def _get_control(self) -> OneLoopCtrl:
        pass

    def _load_song(self) -> None:
        self._stop_song()
        full_name = self._file_finder.get_path()
        dic: Dict
        with open(full_name, 'rb') as f:
            length, dic, load_list = pickle.load(f)

        if len(load_list) != 4:
            raise RuntimeError(f"Song must have 4 parts: {self.get_item()}")

        CONFLDR.dic = dic
        CONFLDR.set(ConfigName.song_name, self._file_finder.get_item())
        CONFLDR.set_defaults(Song.default_config)
        RDRUM.prepare_drum(length)
        ctrl = self._get_control()
        load_list = [x if x is not None else SongPart(ctrl) for x in load_list]

        for part in load_list:
            assert type(part) == SongPart
            part.set_ctrl(ctrl)
            self.append(part)

        CONFLDR.save()
        while self.item_count > 4:
            self.delete(0, save_backup=False)

        self.go_first()
        self.align_ids()
        LOGR.info(f"Loaded song file: {full_name}")

    def _save_song(self) -> None:
        length: int = RDRUM.get_length()
        save_list = []
        for k in range(self.item_count):
            x = self._get_id(k)
            save_list.append(x if not x.is_empty else None)

        if len(save_list) != 4:
            raise RuntimeError(f"Song must have 4 parts: {self.get_item()}")

        full_name = self._file_finder.get_path()
        with open(full_name, 'wb') as f:
            pickle.dump((length, CONFLDR.dic, save_list), f)

        LOGR.info(f"Saved song file {full_name}")

    def _save_new_song(self):
        tmp = self.__new_song_name()
        self._file_finder.append(tmp)
        self._file_finder.go_last()
        self._save_song()

    def _delete_song(self) -> None:
        self._stop_song()
        path = self._file_finder.get_path()
        if os.path.isfile(path):
            os.remove(path)
        self._file_finder.delete(self._file_finder.id, save_backup=False)
        self._file_finder.iterate(True)
        self._stop_song()

    def __new_song_name(self) -> str:
        return generate_name() + self._file_finder.get_end_with()
