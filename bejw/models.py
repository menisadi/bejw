from __future__ import annotations

from dataclasses import dataclass
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

    @staticmethod
    def create(url: str, title: str) -> "Link":
        return Link(id=str(uuid4()), url=url, title=title)


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

    def remove_link(self, link_id: str) -> bool:
        before = len(self.links)
        self.links = [link for link in self.links if link.id != link_id]
        return len(self.links) < before

    def clear_links(self) -> None:
        self.links = []

    def to_dict(self) -> dict:
        return {
            "capacity": self.capacity,
            "links": [link.__dict__ for link in self.links],
        }

    @staticmethod
    def from_dict(data: dict) -> "ReadingList":
        links = [Link(**item) for item in data.get("links", [])]
        capacity = data.get("capacity", 10)
        return ReadingList(capacity=capacity, links=links)
