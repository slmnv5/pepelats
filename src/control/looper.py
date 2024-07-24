import os
from multiprocessing import Queue
from time import sleep

from control._songctrl import SongCtrl
from drum.bufferdrum import EuclidDrum, StyleDrum
from drum.loopdrum import LoopDrum
from drum.mididrum import MidiDrum
from serv.confighandler import web_config
from utils.util_config import IP_ADDR, BRANCH
from utils.util_config import load_ini_section, update_ini_section
from utils.util_log import MY_LOG
from utils.util_name import AppName
from utils.util_screen import get_default_dict


class Looper(SongCtrl):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_q: Queue, send_q: Queue):
        SongCtrl.__init__(self, recv_q)
        self.__queue = send_q
        self.__dic: dict = get_default_dict()
        self._drum_create(0, dict())

    def _client_stop(self) -> None:
        self._client_enqueue([AppName.client_stop])
        super()._client_stop()
        self._song_stop()

    def drum_create_async(self, bar_len: int, drum_info: dict) -> None:
        self._client_enqueue(['_drum_create', bar_len, drum_info])

    def _drum_create(self, bar_len: int, drum_info: dict) -> None:
        drum_type: str = drum_info.get(AppName.drum_type, self._drum.get_class_name())

        if drum_type == AppName.EuclidDrum:
            self._drum = EuclidDrum()
        elif drum_type == AppName.StyleDrum:
            self._drum = StyleDrum()
        elif drum_type == AppName.MidiDrum:
            self._drum = MidiDrum()
        elif drum_type == AppName.LoopDrum:
            self._drum = LoopDrum(self._song.get_list()[0])
        else:
            self._drum = StyleDrum()

        config: str = drum_info.get(AppName.drum_config_file)
        self._drum.set_config(config)
        volume = drum_info.get(AppName.drum_volume)
        if volume:
            self._drum.set_volume(volume)
        par = drum_info.get(AppName.drum_par)
        if par:
            self._drum.set_par(par)
        if bar_len:
            self._drum.set_bar_len(bar_len)

    def _update_view(self) -> None:
        self._client_enqueue([AppName.client_redraw, self.__dic])

    def _client_redraw(self, dic: dict) -> None:
        dic["header"] = f"{self._drum}"
        if "update_method" in dic:
            # noinspection PyBroadException
            try:
                method = getattr(self, dic["update_method"])
                dic["content"] = method()
            except Exception as ex:
                MY_LOG.exception(ex)

        part = self._song.get_item()
        dic["len"] = part.get_len()
        dic["max_loop_len"] = part.get_max_len(True)
        dic["idx"] = self.idx
        dic["is_rec"] = self.get_is_rec()
        self.__dic.update(dic)
        self.__queue.put([AppName.client_redraw, self.__dic])

    # other methods

    @staticmethod
    def _info_show() -> str:
        scr_type: int = load_ini_section("SCREEN", True).get(AppName.screen_type, 0)
        return f"IP addr: {IP_ADDR}\nscreen type: {scr_type} (0-lcd, 1-web)\nversion: {BRANCH}"

    @staticmethod
    def _screen_type_change() -> None:
        dic = load_ini_section("SCREEN", True)
        scr_type: int = dic.get(AppName.screen_type, 0)
        dic[AppName.screen_type] = str((scr_type + 1) % 2)
        update_ini_section("SCREEN", dic)

    @staticmethod
    def _looper_update() -> None:
        os.system("git reset --hard; clear; git pull")
        sleep(5)

    def _web_config(self) -> None:
        self._song_stop()
        MY_LOG.warning(f"HTTP server starting at: {IP_ADDR}:9000")
        web_config()
        self._client_clear_queue()

    #  parts methods

    def _part_undo(self) -> None:
        part = self._song.get_item()
        if part.item_count() <= 1:
            return

        is_rec = self.get_is_rec()
        self._set_is_rec(False)

        if not is_rec:
            part.undo()
        else:
            part.delete_selected()

    def _part_redo(self) -> None:
        self._set_is_rec(False)
        part = self._song.get_item()
        part.redo()

    # one part methods

    def _loop_iterate(self, steps: int) -> None:
        self._song.get_item().iterate(steps)

    def _loop_edit(self, action: str) -> None:
        part = self._song.get_item()
        loop = part.get_item()
        if action == "silent":
            loop.set_silent(not loop.is_silent())
        elif action == "reverse":
            loop.flip_reverse()
        elif action == "move" and part != loop:
            deleted = part.delete_selected()
            if deleted:
                part.add_item(deleted)
        elif action == "delete" and part != loop:
            part.delete_selected()
