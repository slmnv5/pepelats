from configparser import ConfigParser

from utils.util_config import load_ini_section
from utils.util_log import ConfigError
from utils.util_name import AppName


class MenuLoader:
    """ class loading menu mapping from INI files """

    def __init__(self):
        dname: str = load_ini_section("MENU").get(AppName.menu_choice, "")
        dname = f"{AppName.menu_config_dir}/{dname}"

        self.__section: str = AppName.play_section
        self.__idx: int = 0  # section id
        self.__dic = dict()  # single dict for all files

        lst = ["play.ini", "song.ini", "drum.ini", "serv.ini"]
        f_navigate = f"{dname}/navigate.ini"
        for f_menu in [f"{dname}/{x}" for x in lst]:
            cfg = ConfigParser()
            read_lst = cfg.read([f_navigate, f_menu])
            if len(read_lst) != 2:
                raise ConfigError(f"INI menu files not loaded: {f_navigate}/{f_menu}")
            self.__dic |= {s: dict(cfg.items(s)) for s in cfg.sections()}

    def get_command(self, key: str) -> str:
        key1 = f"{self.__section}.{self.__idx}"
        if key1 not in self.__dic:
            return ""
        section_dic = self.__dic[key1]
        if key not in section_dic:
            return ""
        return section_dic[key]

    def _menu_update(self, section: str) -> None:
        assert f"{section}.0" in self.__dic
        self.__section = section
        self.__idx = 0

    def _section_update(self, k: int) -> None:
        lst = [x for x in self.__dic.keys() if self.__section in x]
        self.__idx = (self.__idx + k) % len(lst)

    def __str__(self):
        return f"{self.__section}.{self.__idx}"
