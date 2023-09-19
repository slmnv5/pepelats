from utils.utilconfig import load_ini_section, find_path


def test_1():
    dic = load_ini_section(find_path("main.ini"), "AUDIO")
    assert dic["max_len_seconds"] == "60"
