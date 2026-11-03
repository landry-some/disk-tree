import pytest

from disk_tree.render import format_size, render
from disk_tree.scan import Node


@pytest.mark.parametrize(
    "size, expected",
    [
        (0, "0 B"),
        (1023, "1023 B"),
        (1024, "1.0 KiB"),
        (1536, "1.5 KiB"),
        (5 * 1024**2, "5.0 MiB"),
        (3 * 1024**3 + 1024**3 // 2, "3.5 GiB"),
        (2 * 1024**5, "2.0 PiB"),
        (2048 * 1024**5, "2048.0 PiB"),
    ],
)
def test_format_size(size, expected):
    assert format_size(size) == expected


def test_render_draws_tree_with_sizes():
    root = Node("top", 3072, is_dir=True, children=[
        Node("a", 2048, is_dir=True, children=[
            Node("x.bin", 1024),
            Node("y.bin", 1024),
        ]),
        Node("b.txt", 1024),
    ])

    assert render(root) == "\n".join([
        "top  3.0 KiB",
        "├── a  2.0 KiB",
        "│   ├── x.bin  1.0 KiB",
        "│   └── y.bin  1.0 KiB",
        "└── b.txt  1.0 KiB",
    ])


def test_render_marks_denied_folders():
    root = Node("top", 0, is_dir=True, children=[Node("locked", 0, is_dir=True, denied=True)])
    assert render(root).splitlines()[1] == "└── locked  0 B  [denied]"


def test_render_single_node():
    assert render(Node("file.txt", 12)) == "file.txt  12 B"
