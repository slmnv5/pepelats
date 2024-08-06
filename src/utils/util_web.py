import os

from utils.util_name import AppName

EDIT_PATH: str = "/edit?file="
CONFIG_PATH: str = "/config"
UPDATE_PATH: str = "/update?update_id="


def load_file(fname: str) -> str:
    assert os.path.isfile(fname)
    with open(fname, 'r') as f:
        return f.read()


def load_bin_file(fname: str) -> bytes:
    assert os.path.isfile(fname)
    with open(fname, 'rb') as f:
        return f.read()


def _one_link(fname: str, prefix: str) -> str:
    return f"<a href = {prefix}{fname}>{fname}</a>"


def _all_links(dname: str, end_with: str, prefix: str) -> str:
    file_lst = list()

    for root, _, files in os.walk(dname):
        for fname in [os.path.join(root, x) for x in files if x.endswith(end_with)]:
            file_lst.append(fname)
    link_lst = list()
    for fname in file_lst:
        link_lst.append("\n" + _one_link(fname, prefix) + "<br/>")
    return "".join(link_lst)


_FORMAT_DICT: dict[str, str] = dict()

_FORMAT_DICT["l_main_config"] = _one_link(AppName.main_ini, EDIT_PATH)
_FORMAT_DICT["l_local_config"] = _one_link(AppName.local_ini, EDIT_PATH)

_FORMAT_DICT["l_drum"] = _all_links(f"{AppName.drum_config_dir}", ".ini", EDIT_PATH)
_FORMAT_DICT["l_menu"] = _all_links(f"./{AppName.menu_config_dir}", ".ini", EDIT_PATH)

CONFIG_PAGE_B: bytes = load_file("html/config_page.html").format(**_FORMAT_DICT).encode()
