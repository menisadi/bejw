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


def test_mark_read_by_number_marks_link_and_removes_from_unread_view() -> None:
    reading_list = ReadingList(capacity=3)
    first = reading_list.add_link("https://example.com/1", "One")
    second = reading_list.add_link("https://example.com/2", "Two")

    marked = reading_list.mark_read_by_number(1)

    assert marked is True
    refreshed_first = next(link for link in reading_list.links if link.id == first.id)
    refreshed_second = next(link for link in reading_list.links if link.id == second.id)
    assert refreshed_first.read_at is not None
    assert refreshed_second.read_at is None
    assert [link.id for link in reading_list.unread_links()] == [second.id]


def test_from_dict_defaults_read_at_for_legacy_entries() -> None:
    restored = ReadingList.from_dict(
        {
            "capacity": 2,
            "links": [
                {
                    "id": "id-1",
                    "url": "https://example.com",
                    "title": "Example",
                    "created_at": "2024-01-01T00:00:00+00:00",
                }
            ],
        }
    )

    assert len(restored.links) == 1
    assert restored.links[0].read_at is None
