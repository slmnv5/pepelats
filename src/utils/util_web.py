import os
from http.server import BaseHTTPRequestHandler

from utils.util_name import AppName

EDIT_PATH: str = "/edit?file="
SHOW_PATH: str = "/show?file="
RESET_PATH: str = "/reset"
EXIT_PATH: str = "/exit"


def send_redirect(handler: BaseHTTPRequestHandler) -> None:
    handler.send_response(303)
    handler.send_header('Content-type', 'text/html')
    handler.send_header('Location', '/')  # This will navigate to the original page
    handler.end_headers()


def load_file(fname: str, is_binary: bool = False) -> str | bytes:
    assert os.path.isfile(fname)
    mode = "rb" if is_binary else "r"
    with open(fname, mode) as f:
        return f.read()


def send_headers(handler: BaseHTTPRequestHandler, content_type: str = 'text/html') -> None:
    handler.send_response(200)
    handler.send_header('Content-type', content_type)
    handler.end_headers()


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
_FORMAT_DICT["l_exit"] = EXIT_PATH
_FORMAT_DICT["l_reset"] = RESET_PATH

_FORMAT_DICT["l_std_cfg"] = _one_link(AppName.main_ini, SHOW_PATH)
_FORMAT_DICT["l_custom_cfg"] = _one_link(AppName.local_ini, EDIT_PATH)

_FORMAT_DICT["l_curr_log"] = _one_link('log.txt', SHOW_PATH)
_FORMAT_DICT["l_old_log"] = _one_link('log.bak', SHOW_PATH)

_FORMAT_DICT["l_drum"] = _all_links(f"{AppName.drum_config_dir}", ".ini", EDIT_PATH)
_FORMAT_DICT["l_menu"] = _all_links(f"./{AppName.menu_config_dir}", ".ini", EDIT_PATH)

CONFIG_PAGE: bytes = load_file("html/config_page.html").format(**_FORMAT_DICT).encode()
