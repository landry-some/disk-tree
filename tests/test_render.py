import pytest

from disk_tree.render import format_size, render, render_csv, render_json
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


def deep_tree():
    return Node("top", 3, is_dir=True, children=[
        Node("l1", 3, is_dir=True, children=[
            Node("l2", 3, is_dir=True, children=[Node("l3.txt", 3)]),
        ]),
    ])


@pytest.mark.parametrize(
    "max_depth, names",
    [
        (0, ["top"]),
        (1, ["top", "l1"]),
        (2, ["top", "l1", "l2"]),
        (3, ["top", "l1", "l2", "l3.txt"]),
        (None, ["top", "l1", "l2", "l3.txt"]),
    ],
)
def test_render_respects_max_depth(max_depth, names):
    lines = render(deep_tree(), max_depth).splitlines()
    assert [line.lstrip("│├└─ ").split("  ")[0] for line in lines] == names


def test_depth_limit_keeps_full_sizes():
    assert render(deep_tree(), 1).splitlines()[1] == "└── l1  3 B"


def test_render_json_nests_children_with_byte_sizes():
    import json

    root = Node("top", 3, is_dir=True, children=[
        Node("locked", 0, is_dir=True, denied=True),
        Node("f.txt", 3),
    ])

    assert json.loads(render_json(root)) == {
        "name": "top", "size": 3, "is_dir": True, "children": [
            {"name": "locked", "size": 0, "is_dir": True, "denied": True, "children": []},
            {"name": "f.txt", "size": 3, "is_dir": False},
        ],
    }


@pytest.mark.parametrize("max_depth, depth_seen", [(0, 0), (1, 1), (2, 2), (None, 3)])
def test_render_json_respects_max_depth(max_depth, depth_seen):
    import json

    node, depth = json.loads(render_json(deep_tree(), max_depth)), 0
    while node.get("children"):
        node, depth = node["children"][0], depth + 1
    assert depth == depth_seen
    assert json.loads(render_json(deep_tree(), 0))["size"] == 3


def test_render_csv_lists_one_row_per_entry():
    root = Node("top", 3, is_dir=True, children=[
        Node("a, b", 2, is_dir=True, children=[Node("x.txt", 2)]),
        Node("locked", 0, is_dir=True, denied=True),
    ])

    assert render_csv(root).splitlines() == [
        "path,size,is_dir,denied",
        "top,3,1,0",
        '"top/a, b",2,1,0',
        '"top/a, b/x.txt",2,0,0',
        "top/locked,0,1,1",
    ]


def test_render_csv_respects_max_depth_and_root_slash():
    root = Node("/", 3, is_dir=True, children=[deep_tree()])
    assert [r.split(",")[0] for r in render_csv(root, 2).splitlines()[1:]] == [
        "/", "/top", "/top/l1",
    ]
