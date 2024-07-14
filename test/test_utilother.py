import random

from utils.utilother import FileFinder, CollectionOwner, EuclidSlicer, split_key_value


def test_1():
    lst = [chr(k) for k in range(65, 80)]
    co = CollectionOwner(lst)
    co.select_idx(8)
    list_str = co.get_str(9)
    print(list_str)
    assert "-07 H" in list_str
    assert "*08 I" in list_str
    assert "~09 J" in list_str


def test_2():
    ff = FileFinder(".", True, "")
    for x in ff.get_list():
        print(x)
    print(f"count: {ff.item_count()}")


def test_3():
    ff = FileFinder(".", True, ".apple_orange")
    assert "" == ff.get_item()
    assert 1 == ff.item_count()


def test_4():
    assert EuclidSlicer(13, 5, 0, 0).beat_steps() == [0, 3, 5, 8, 10]
    assert EuclidSlicer(13, 5, 5, 0).beat_steps() == [8, 11, 0, 3, 5]

    assert EuclidSlicer(4, 5, 0, 0).beat_steps() == [0, 1, 2, 3]
    assert EuclidSlicer(2, 8, 0, 0).beat_steps() == [0, 1]


def test_6():
    assert EuclidSlicer(10, 3, 0, 0).sub_list_by_idx(0) == [0, 1, 2]
    assert EuclidSlicer(10, 3, 0, 0).sub_list_by_idx(1) == [3, 4, 5, 6]
    assert EuclidSlicer(10, 3, 0, 0).sub_list_by_idx(2) == [7, 8, 9]

    assert EuclidSlicer(3, 3, 0, 0).sub_list_by_idx(0) == [0]
    assert EuclidSlicer(3, 3, 0, 0).sub_list_by_idx(1) == [1]
    assert EuclidSlicer(3, 3, 0, 0).sub_list_by_idx(2) == [2]

    assert EuclidSlicer(2, 3, 0, 0).sub_list_by_idx(0) == [0]
    assert EuclidSlicer(2, 2, 0, 0).sub_list_by_idx(1) == [1]
    assert EuclidSlicer(2, 3, 0, 0).sub_list_by_idx(1) == [1]

    assert EuclidSlicer(5, 30, 0, 0).sub_list_by_idx(0) == [0]
    assert EuclidSlicer(5, 30, 0, 0).sub_list_by_idx(6) == [1]
    assert EuclidSlicer(5, 30, 0, 0).sub_list_by_idx(7) == [2]

    assert EuclidSlicer(5, 3, 0, 0).sub_list_by_idx(1) == [2]

    assert EuclidSlicer(30, 5, 0, 0).sub_list_by_idx(0) == [0, 1, 2, 3, 4, 5]
    assert EuclidSlicer(30, 5, 0, 0).sub_list_by_idx(3) == [18, 19, 20, 21, 22, 23]


def test_7():
    lst = [1, 2]
    es = EuclidSlicer(len(lst), 12, 0, 0)
    sl: slice = es.slice_by_idx(0)
    lst = lst[sl]
    idx = sl.start + random.randrange(len(lst))
    assert idx == 0
    assert lst == [1]


def test_8():
    big_str = "cc12345ab\n\n\n12345dd"
    assert ("12345", "12345") == split_key_value(big_str, "cc", "\n", "ab", strip2="\nd")
    assert ("12345", "12345") == split_key_value(big_str, "cc", "ab", "", strip2="\nd")
    assert ("12345", "12345dd") == split_key_value(big_str, "cc", "a", "", strip2="b\n")
    assert ("", "") == split_key_value(big_str, "CC", "a", "", strip2="")
    assert ("", "") == split_key_value(big_str, "cc", "A", "", strip2="")
    assert ("5", "\n12345dd") == split_key_value(big_str, "34", "\n\n", "ab", strip2="")
