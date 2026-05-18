from love_bot.utils import get_indexes


def test_get_indexes_single():
    assert get_indexes("1, 2, 3") == [1, 2, 3]


def test_get_indexes_ranges():
    assert get_indexes("1-3") == [1, 2, 3]


def test_get_indexes_mixed():
    assert get_indexes("1, 3-5, 7") == [1, 3, 4, 5, 7]
