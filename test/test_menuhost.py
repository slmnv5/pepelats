# noinspection PyProtectedMember
from utils.util_config import convert_param


def test_1():
    assert convert_param('lkj') == 'lkj'
    assert convert_param(' +123  ') == 123
    assert convert_param(' -123.99  ') == -123.99
    assert convert_param(' -123.99. ') != -123.99
