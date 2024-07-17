import os
import time
from http.server import HTTPServer
from multiprocessing import Queue

from control._songctrl import SongCtrl
from drum.bufferdrum import EuclidDrum, StyleDrum
from drum.loopdrum import LoopDrum
from drum.mididrum import MidiDrum
from mvc.drawinfo import DrawInfo
from serv.confighandler import ConfigHandler
from utils.utilconfig import ConfigName, IP_ADDR
from utils.utilconfig import load_ini_section, update_ini_section
from utils.utillog import MyLog
from utils.utilother import FileFinder


class Looper(SongCtrl):
    """Adds screen connection, Mixer, looper commands"""

    def __init__(self, recv_q: Queue, send_q: Queue):
        SongCtrl.__init__(self, recv_q)
        self.__queue = send_q
        self._prev_di: DrawInfo = DrawInfo()
        self.drum_create(0)

    def _client_stop(self) -> None:
        super()._client_stop()
        self._song_stop()
        self.__queue.put([ConfigName.client_stop])

    def drum_create(self, bar_len: int, **kwargs) -> None:
        self.menu_client_queue(['_drum_create', bar_len, {**kwargs}])

    def _drum_create(self, bar_len: int, drum_info: dict[str: any]) -> None:
        drum_type: str = drum_info.get(ConfigName.drum_type, self._drum.get_class_name())

        if drum_type == ConfigName.EuclidDrum:
            self._drum = EuclidDrum()
        elif drum_type == ConfigName.StyleDrum:
            self._drum = StyleDrum()
        elif drum_type == ConfigName.MidiDrum:
            self._drum = MidiDrum()
        elif drum_type == ConfigName.LoopDrum:
            self._drum = LoopDrum(self._song.get_list()[0])
        else:
            self._drum = StyleDrum()

        config: str = drum_info.get(ConfigName.drum_config_file)
        self._drum.set_config(config)
        volume = drum_info.get(ConfigName.drum_volume)
        if volume:
            self._drum.set_volume(volume)
        par = drum_info.get(ConfigName.drum_par)
        if par:
            self._drum.set_par(par)
        if bar_len:
            self._drum.set_bar_len(bar_len)

    def _update_view(self) -> None:
        self.menu_client_queue([ConfigName.client_redraw, self._prev_di])

    def _client_redraw(self, di: DrawInfo) -> None:
        di.header = f"{self._drum}"
        if di.update_method:
            # noinspection PyBroadException
            try:
                method = getattr(self, di.update_method)
                di.content = method()
            except Exception as ex:
                MyLog().exception(ex)

        part = self._song.get_item()
        di.len = part.get_len()
        di.max_loop_len = part.get_max_len(di.len)
        di.idx = self.idx
        di.is_rec = self.get_is_rec()
        self._prev_di = di
        self.__queue.put([ConfigName.client_redraw, self._prev_di])

    # ===============+ other methods ===============================

    @staticmethod
    def _menu_config_show() -> str:
        dic = load_ini_section("MENU")
        return "Menu: " + dic.get(ConfigName.menu_choice, "")

    @staticmethod
    def _menu_config_iterate() -> None:
        tmp = load_ini_section("MENU")
        config = tmp.get(ConfigName.menu_choice, "")
        ff = FileFinder(ConfigName.menu_config_dir, False, "")
        ff.add_item(config)
        ff.iterate(1)  # next menu
        tmp[ConfigName.menu_choice] = ff.get_item()
        update_ini_section("MENU", tmp)

    @staticmethod
    def _looper_update() -> None:
        os.system("git reset --hard; clear; git pull")
        time.sleep(5)

    def _web_config(self) -> None:
        self._song_stop()
        print(f"HTTP server starting at: {IP_ADDR}:9000")
        # noinspection PyTypeChecker
        server = HTTPServer(('', 9000), ConfigHandler)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()
        print(f"HTTP server stopped at: {IP_ADDR}:9000")

    #  ============ all parts methods ===============

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

    # ================= one part methods ====================================

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
