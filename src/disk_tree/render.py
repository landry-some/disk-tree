from disk_tree.scan import Node

UNITS = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]


def format_size(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    value = float(size)
    for unit in UNITS[1:]:
        value /= 1024
        if value < 1024 or unit == UNITS[-1]:
            return f"{value:.1f} {unit}"
    raise AssertionError("unreachable")


def label(node: Node) -> str:
    text = f"{node.name}  {format_size(node.size)}"
    return text + "  [denied]" if node.denied else text


def render(root: Node) -> str:
    lines = [label(root)]
    _add_children(root, "", lines)
    return "\n".join(lines)


def _add_children(node: Node, prefix: str, lines: list[str]) -> None:
    for i, child in enumerate(node.children):
        last = i == len(node.children) - 1
        lines.append(prefix + ("└── " if last else "├── ") + label(child))
        _add_children(child, prefix + ("    " if last else "│   "), lines)
