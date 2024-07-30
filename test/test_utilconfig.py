from utils.util_config import load_ini_section, get_params
from utils.util_name import AppName


def test_1():
    dic = load_ini_section("AUDIO")
    assert dic[AppName.max_len_seconds] == "60"
    dic = load_ini_section("AUDIO", True)
    assert dic[AppName.max_len_seconds] == 60


def test_2():
    dic = get_params("update?id=12345&user=pepe&addr=localhost")
    assert "user" in dic
    assert dic["id"] == 12345
    assert len(dic) == 3
