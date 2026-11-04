import csv
import io
import json

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


def render(root: Node, max_depth: int | None = None) -> str:
    """Draw root and its descendants; max_depth counts levels below root (None = all)."""
    lines = [label(root)]
    _add_children(root, "", 1, max_depth, lines)
    return "\n".join(lines)


def _add_children(
    node: Node, prefix: str, depth: int, max_depth: int | None, lines: list[str]
) -> None:
    if max_depth is not None and depth > max_depth:
        return
    for i, child in enumerate(node.children):
        last = i == len(node.children) - 1
        lines.append(prefix + ("└── " if last else "├── ") + label(child))
        _add_children(child, prefix + ("    " if last else "│   "), depth + 1, max_depth, lines)


def to_dict(node: Node, max_depth: int | None = None) -> dict:
    """Nested dict of node; folders past max_depth get an empty children list."""
    data: dict = {"name": node.name, "size": node.size, "is_dir": node.is_dir}
    if node.denied:
        data["denied"] = True
    if node.is_dir:
        deeper = None if max_depth is None else max_depth - 1
        data["children"] = [] if max_depth == 0 else [to_dict(c, deeper) for c in node.children]
    return data


def render_json(root: Node, max_depth: int | None = None) -> str:
    return json.dumps(to_dict(root, max_depth), indent=2, ensure_ascii=False)


def render_csv(root: Node, max_depth: int | None = None) -> str:
    """One row per entry: path (joined with /), size in bytes, is_dir, denied."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["path", "size", "is_dir", "denied"])
    _add_rows(root, root.name, 0, max_depth, writer)
    return out.getvalue().rstrip("\n")


def _add_rows(node: Node, path: str, depth: int, max_depth: int | None, writer) -> None:
    writer.writerow([path, node.size, int(node.is_dir), int(node.denied)])
    if max_depth is not None and depth >= max_depth:
        return
    for child in node.children:
        _add_rows(child, f"{path.rstrip('/')}/{child.name}", depth + 1, max_depth, writer)
