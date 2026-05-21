import pytest

from love_bot.utils import get_date_with_month_written_by_letters, get_indexes


def test_get_indexes_single():
    assert get_indexes("1, 2, 3") == [1, 2, 3]


def test_get_indexes_ranges():
    assert get_indexes("1-3") == [1, 2, 3]


def test_get_indexes_mixed():
    assert get_indexes("1, 3-5, 7") == [1, 3, 4, 5, 7]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("01.01", "1 января "),
        ("15.10.2025", "15 октября 2025"),
    ],
)
def test_get_date_with_month_written_by_letters(
    source,
    expected,
):
    assert (
        get_date_with_month_written_by_letters(source)
        == expected
    )
