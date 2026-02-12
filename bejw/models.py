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

    def remove_link(self, link_id: str) -> bool:
        before = len(self.links)
        self.links = [link for link in self.links if link.id != link_id]
        return len(self.links) < before

    def remove_by_number(self, number: int) -> bool:
        ordered = self.ordered_links()
        if number < 1 or number > len(ordered):
            return False
        target_id = ordered[number - 1].id
        return self.remove_link(target_id)

    def clear_links(self) -> None:
        self.links = []

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
            links.append(Link(**item))
        capacity = data.get("capacity", 10)
        return ReadingList(capacity=capacity, links=links)
