from utils.util_config import load_ini_section
from utils.util_name import AppName


def test_1():
    dic = load_ini_section("AUDIO")
    assert dic[AppName.max_len_seconds] == "60"
