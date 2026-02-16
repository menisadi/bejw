from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import uuid4


class CapacityError(Exception):
    """Raised when trying to add a link to a full reading list."""

    def __init__(self, message: str = "Reading list is full") -> None:
        super().__init__(message)


@dataclass(frozen=True)
class Link:
    id: str
    url: str
    title: str
    created_at: str
    read_at: str | None = None

    @staticmethod
    def create(url: str, title: str) -> "Link":
        created_at = datetime.now(timezone.utc).isoformat()
        return Link(id=str(uuid4()), url=url, title=title, created_at=created_at)


def _created_at_key(link: Link) -> datetime:
    try:
        created_at = datetime.fromisoformat(link.created_at)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if created_at.tzinfo is None:
        return created_at.replace(tzinfo=timezone.utc)
    return created_at


class ReadingList:
    def __init__(self, capacity: int = 10, links: Iterable[Link] | None = None) -> None:
        self.capacity = capacity
        self.links: list[Link] = list(links or [])

    def add_link(self, url: str, title: str) -> Link:
        if len(self.links) >= self.capacity:
            raise CapacityError("Reading list is full")
        link = Link.create(url, title)
        self.links.append(link)
        return link

    def ordered_links(self) -> list[Link]:
        return sorted(self.links, key=_created_at_key)

    def unread_links(self) -> list[Link]:
        return [link for link in self.ordered_links() if link.read_at is None]

    def read_links(self) -> list[Link]:
        return [link for link in self.ordered_links() if link.read_at is not None]

    def remove_link(self, link_id: str) -> bool:
        before = len(self.links)
        self.links = [link for link in self.links if link.id != link_id]
        return len(self.links) < before

    def remove_by_number(self, number: int, include_read: bool = False) -> bool:
        visible_links = self.ordered_links() if include_read else self.unread_links()
        if number < 1 or number > len(visible_links):
            return False
        target_id = visible_links[number - 1].id
        return self.remove_link(target_id)

    def clear_links(self) -> None:
        self.links = []

    def mark_read_by_number(self, number: int, include_read: bool = False) -> bool:
        visible_links = self.ordered_links() if include_read else self.unread_links()
        if number < 1 or number > len(visible_links):
            return False

        target_id = visible_links[number - 1].id
        read_at = datetime.now(timezone.utc).isoformat()
        self.links = [
            link if link.id != target_id else Link(**{**link.__dict__, "read_at": read_at})
            for link in self.links
        ]
        return True

    def to_dict(self) -> dict:
        return {
            "capacity": self.capacity,
            "links": [link.__dict__ for link in self.links],
        }

    @staticmethod
    def from_dict(data: dict) -> "ReadingList":
        raw_links = data.get("links", [])
        base_time = datetime(1970, 1, 1, tzinfo=timezone.utc)
        links = []
        for index, item in enumerate(raw_links):
            if "created_at" not in item:
                item = {
                    **item,
                    "created_at": (base_time + timedelta(seconds=index)).isoformat(),
                }
            if "read_at" not in item:
                item = {**item, "read_at": None}
            links.append(Link(**item))
        capacity = data.get("capacity", 10)
        return ReadingList(capacity=capacity, links=links)
