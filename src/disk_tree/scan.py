import os
import stat
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class Node:
    name: str
    size: int = 0
    is_dir: bool = False
    denied: bool = False
    children: list["Node"] = field(default_factory=list)


def scan(path: str, on_file: Callable[[], None] | None = None) -> Node:
    """Build a size tree for path.

    Symlinks are counted by their own size, not followed. A file with several hard
    links is counted once, at the first link found; the others show as 0 bytes.
    """
    st = os.lstat(path)
    if not stat.S_ISDIR(st.st_mode):
        return Node(path, st.st_size)
    return _scan_dir(path, path, on_file, set())


def _scan_dir(
    path: str, name: str, on_file: Callable[[], None] | None, seen: set[tuple[int, int]]
) -> Node:
    node = Node(name, is_dir=True)
    try:
        with os.scandir(path) as it:
            entries = list(it)
    except PermissionError:
        node.denied = True
        return node

    for entry in entries:
        if entry.is_dir(follow_symlinks=False):
            child = _scan_dir(entry.path, entry.name, on_file, seen)
        else:
            try:
                st = entry.stat(follow_symlinks=False)
            except OSError:
                size = 0
            else:
                size = st.st_size
                if st.st_nlink > 1:
                    if (st.st_dev, st.st_ino) in seen:
                        size = 0
                    seen.add((st.st_dev, st.st_ino))
            child = Node(entry.name, size)
            if on_file:
                on_file()
        node.children.append(child)
        node.size += child.size
    return node


def sort_by_size(node: Node) -> None:
    """Order every folder's children largest first, ties broken by name."""
    node.children.sort(key=lambda c: (-c.size, c.name))
    for child in node.children:
        sort_by_size(child)


def prune(node: Node, min_size: int) -> None:
    """Drop entries smaller than min_size at every level; folder sizes stay unchanged."""
    node.children = [c for c in node.children if c.size >= min_size]
    for child in node.children:
        prune(child, min_size)
