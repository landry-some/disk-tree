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
    """Build a size tree for path. Symlinks are counted by their own size, not followed."""
    st = os.lstat(path)
    if not stat.S_ISDIR(st.st_mode):
        return Node(path, st.st_size)
    return _scan_dir(path, path, on_file)


def _scan_dir(path: str, name: str, on_file: Callable[[], None] | None) -> Node:
    node = Node(name, is_dir=True)
    try:
        with os.scandir(path) as it:
            entries = list(it)
    except PermissionError:
        node.denied = True
        return node

    for entry in entries:
        if entry.is_dir(follow_symlinks=False):
            child = _scan_dir(entry.path, entry.name, on_file)
        else:
            try:
                size = entry.stat(follow_symlinks=False).st_size
            except OSError:
                size = 0
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
