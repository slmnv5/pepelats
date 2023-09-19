from utils.utilother import FileFinder, CollectionOwner, euclid_spacing, euclid_pattern_str, lst_for_slice, \
    slice_for_elm


def test_1():
    lst = [chr(k) for k in range(65, 80)]
    co = CollectionOwner(lst[0])
    for k in lst[1:]:
        co.add_item(k)
    found_list = list()
    co.apply_to_each(lambda x: found_list.append(x if x == 'F' else None))
    assert found_list.index('F') == 5
    co.select_idx(8)
    list_str = co.get_str(next_id=9)
    print(list_str)
    assert ".H" in list_str
    assert "*I" in list_str
    assert "~J" in list_str


def test_2():
    ff = FileFinder(".", True, "")
    ff.apply_to_each(lambda x: print(x))
    print("================")
    print(f"count: {ff.item_count()}")


def test_3():
    ff = FileFinder(".", True, ".apple_orange")
    assert "" == ff.selected_item()
    assert 1 == ff.item_count()


def test_4():
    arr = euclid_spacing(13, 5, 0)
    assert arr == [0, 3, 5, 8, 10]
    arr = euclid_spacing(13, 5, 5)
    assert arr == [8, 11, 0, 3, 5]
    arr = euclid_spacing(4, 5, 0)
    assert arr == [0, 1, 2, 3]
    arr = euclid_spacing(2, 8, 0)
    assert arr == [0, 1]


def test_5():
    line = euclid_pattern_str(13, 5, 0, 0)
    assert line == "!..!.!..!.!.."

    line = euclid_pattern_str(13, 5, 1, 0)
    assert line == "..!.!..!.!..!"

    line = euclid_pattern_str(13, 5, 5, 0)
    assert line == '!..!.!..!..!.'

    line = euclid_pattern_str(13, 5, 5, 2)
    assert line == '*..!.!..*..!.'


def test_6():
    assert lst_for_slice(0, 10, 3) == [0, 1, 2]
    assert lst_for_slice(1, 10, 3) == [3, 4, 5, 6]
    assert lst_for_slice(2, 10, 3) == [7, 8, 9]

    assert lst_for_slice(0, 3, 3) == [0]
    assert lst_for_slice(1, 3, 3) == [1]
    assert lst_for_slice(2, 3, 3) == [2]

    assert lst_for_slice(0, 2, 3) == [0]
    assert lst_for_slice(1, 2, 2) == [1]
    assert lst_for_slice(1, 2, 3) == [1]

    assert lst_for_slice(0, 5, 30) == [0]
    assert lst_for_slice(6, 5, 30) == [4]
    assert lst_for_slice(7, 5, 30) == [4]

    assert lst_for_slice(0, 30, 5) == [0, 1, 2, 3, 4, 5]
    assert lst_for_slice(3, 30, 5) == [18, 19, 20, 21, 22, 23]

    assert lst_for_slice(1, 5, 3) == [2]

    assert slice_for_elm(0, 20, 5) == 0
    assert slice_for_elm(1, 20, 5) == 0
    assert slice_for_elm(5, 20, 5) == 1
    assert slice_for_elm(19, 20, 5) == 4
    assert slice_for_elm(20, 20, 5) == 4


def test_7():
    print()
    for k in range(12):
        sl_id = slice_for_elm(k, 12, 3)
        sl = lst_for_slice(sl_id, 12, 3)
        assert k in sl, f"{k}, {sl}, {sl_id}"
        print(k, sl)
