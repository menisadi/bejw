import pytest

from bejw.models import CapacityError, Link, ReadingList


def test_add_link_increases_size_and_returns_link() -> None:
    reading_list = ReadingList(capacity=2)

    link = reading_list.add_link("https://example.com", "Example")

    assert isinstance(link, Link)
    assert link.url == "https://example.com"
    assert link.title == "Example"
    assert link.created_at
    assert len(reading_list.links) == 1


def test_add_link_raises_when_capacity_reached() -> None:
    reading_list = ReadingList(capacity=1)
    reading_list.add_link("https://first.com", "First")

    with pytest.raises(CapacityError):
        reading_list.add_link("https://second.com", "Second")


def test_remove_by_number_returns_true_when_found() -> None:
    reading_list = ReadingList()
    reading_list.add_link("https://example.com", "Example")

    removed = reading_list.remove_by_number(1)

    assert removed is True
    assert reading_list.links == []


def test_remove_by_number_returns_false_when_missing() -> None:
    reading_list = ReadingList()

    removed = reading_list.remove_by_number(2)

    assert removed is False


def test_to_dict_and_from_dict_round_trip() -> None:
    original = ReadingList(capacity=3)
    added = original.add_link("https://example.com", "Example")

    payload = original.to_dict()
    restored = ReadingList.from_dict(payload)

    assert restored.capacity == 3
    assert len(restored.links) == 1
    assert restored.links[0] == added
