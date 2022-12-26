from utils.utilother import FileFinder, CollectionOwner


# noinspection PyProtectedMember


def test1():
    import logging

    lst = [chr(k) for k in range(65, 80)]
    co = CollectionOwner(lst[0])
    for k in lst[1:]:
        co.attach(k)
    found_list = list()
    co.apply_to_each(lambda x: found_list.append(x if x == 'F' else None))
    assert 'F' in found_list
    find1 = found_list.index('F')
    assert find1 == 5
    co.set_id(8)  # letter I
    assert "I" == co.get_item()
    list_str = co.get_str()
    logging.debug(list_str)
    assert ".7) H" in list_str
    assert "~8) I" in list_str


def test2():
    import logging

    ff = FileFinder(".", True, "")
    for k in range(ff.item_count()):
        logging.debug(ff.get_item())
        ff.iterate(True)
    logging.debug("================")
    found_list = list()
    ff.apply_to_each(lambda x: found_list.append(x if 'lo' in x else None))
    for item in [x for x in found_list if x]:
        logging.debug(item)


def test3():
    ff = FileFinder(".", True, ".lkjlkjhkj")
    assert "" == ff.get_item()
    assert 1 == ff.item_count()


test1()
test2()
test3()
