import os

from utils.utilconfig import ConfigName


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


def _load_html_file(fname: str) -> str:
    assert os.path.isfile(fname)
    with open(fname, 'r') as f:
        return f.read()


EDIT_PATH = "/edit?file="
SHOW_PATH = "/show?file="
RESET_PATH = "/reset"
EXIT_PATH = "/exit"
UPDATE_PATH = "/update"

_FORMAT_DICT: dict[str, str] = dict()
_FORMAT_DICT["l_exit"] = EXIT_PATH
_FORMAT_DICT["l_reset"] = RESET_PATH

_FORMAT_DICT["l_std_cfg"] = _one_link(ConfigName.main_ini, SHOW_PATH)
_FORMAT_DICT["l_custom_cfg"] = _one_link(ConfigName.local_ini, EDIT_PATH)

_FORMAT_DICT["l_curr_log"] = _one_link('log.txt', SHOW_PATH)
_FORMAT_DICT["l_old_log"] = _one_link('log.bak', SHOW_PATH)

_FORMAT_DICT["l_drum"] = _all_links(f"{ConfigName.drum_config_dir}", ".ini", EDIT_PATH)
_FORMAT_DICT["l_menu"] = _all_links(f"./{ConfigName.menu_config_dir}", ".ini", EDIT_PATH)

FILE_FORM_PAGE: str = _load_html_file("html/file_form.html")
CONFIG_PAGE: bytes = _load_html_file("html/config_page.html").format(**_FORMAT_DICT).encode()
MAIN_PAGE: bytes = _load_html_file("html/main_page.html").encode()
