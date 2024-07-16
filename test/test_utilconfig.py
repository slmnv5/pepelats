from utils.utilconfig import load_ini_section, ConfigName


def test_1():
    dic = load_ini_section("AUDIO")
    assert dic[ConfigName.max_len_seconds] == "60"
