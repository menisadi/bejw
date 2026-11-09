from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
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
    def create(url: str, title: str) -> Link:
        created_at = datetime.now(UTC).isoformat()
        return Link(id=str(uuid4()), url=url, title=title, created_at=created_at)


def _created_at_key(link: Link) -> datetime:
    try:
        created_at = datetime.fromisoformat(link.created_at)
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)
    if created_at.tzinfo is None:
        return created_at.replace(tzinfo=UTC)
    return created_at


class ReadingList:
    def __init__(
        self,
        capacity: int = 10,
        links: Iterable[Link] | None = None,
        capacity_changed_at: str | None = None,
        previous_capacity: int | None = None,
    ) -> None:
        self.capacity = capacity
        self.links: list[Link] = list(links or [])
        self.capacity_changed_at = capacity_changed_at
        self.previous_capacity = previous_capacity

    def set_capacity(self, value: int) -> None:
        """Set the capacity, refusing to raise it while the list is full.

        Lowering is always allowed. Raising requires headroom, so a full list
        cannot be escaped by moving the cap instead of reading something.
        """
        if value < 1:
            raise ValueError("Capacity must be at least 1")
        if value > self.capacity and len(self.unread_links()) >= self.capacity:
            raise CapacityError(
                "Reading list is full. Mark something read before raising capacity."
            )
        if value == self.capacity:
            return
        self.previous_capacity = self.capacity
        self.capacity_changed_at = datetime.now(UTC).isoformat()
        self.capacity = value

    def add_link(self, url: str, title: str) -> Link:
        if len(self.unread_links()) >= self.capacity:
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

    def replace_by_number(self, number: int, url: str, title: str) -> Link | None:
        """Remove unread link at *number* and add a new link in its place."""
        unread = self.unread_links()
        if number < 1 or number > len(unread):
            return None
        target_id = unread[number - 1].id
        self.links = [link for link in self.links if link.id != target_id]
        link = Link.create(url, title)
        self.links.append(link)
        return link

    def clear_links(self) -> None:
        self.links = []

    def mark_read_by_number(
        self, number: int, include_read: bool = False
    ) -> Link | None:
        visible_links = self.ordered_links() if include_read else self.unread_links()
        if number < 1 or number > len(visible_links):
            return None

        target = visible_links[number - 1]
        marked = Link(**{**target.__dict__, "read_at": datetime.now(UTC).isoformat()})
        self.links = [link if link.id != target.id else marked for link in self.links]
        return marked

    def to_dict(self) -> dict:
        return {
            "capacity": self.capacity,
            "capacity_changed_at": self.capacity_changed_at,
            "previous_capacity": self.previous_capacity,
            "links": [link.__dict__ for link in self.links],
        }

    @staticmethod
    def from_dict(data: dict) -> ReadingList:
        raw_links = data.get("links", [])
        base_time = datetime(1970, 1, 1, tzinfo=UTC)
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
        return ReadingList(
            capacity=capacity,
            links=links,
            capacity_changed_at=data.get("capacity_changed_at"),
            previous_capacity=data.get("previous_capacity"),
        )
