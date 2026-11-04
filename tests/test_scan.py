import os

import pytest

from disk_tree.scan import ScanInterrupted, prune, scan, sort_by_size


def child(node, name):
    return next(c for c in node.children if c.name == name)


def test_sums_file_sizes_per_folder(make_tree):
    root = scan(str(make_tree({"a.txt": 10, "sub/b.txt": 20, "sub/deep/c.txt": 5})))

    assert root.size == 35
    assert root.is_dir
    sub = child(root, "sub")
    assert sub.size == 25
    assert child(sub, "deep").size == 5
    assert child(root, "a.txt").size == 10


def test_root_keeps_path_as_given(make_tree):
    path = str(make_tree({"a.txt": 1}))
    assert scan(path).name == path


def test_empty_folder_is_zero(tmp_path):
    (tmp_path / "empty").mkdir()
    root = scan(str(tmp_path))
    assert root.size == 0
    assert child(root, "empty").is_dir


def test_single_file_path(make_tree):
    path = make_tree({"only.bin": 42}) / "only.bin"
    node = scan(str(path))
    assert node.size == 42
    assert not node.is_dir


def test_symlinks_are_not_followed(make_tree):
    root_path = make_tree({"big/data.bin": 1000})
    os.symlink(root_path / "big", root_path / "link")

    root = scan(str(root_path))

    assert root.size == 1000 + os.lstat(root_path / "link").st_size
    assert not child(root, "link").is_dir


def test_on_file_called_once_per_file(make_tree):
    calls = []
    scan(str(make_tree({"a": 1, "b/c": 1, "b/d/e": 1})), on_file=lambda: calls.append(1))
    assert len(calls) == 3


@pytest.mark.skipif(os.geteuid() == 0, reason="root can read any folder")
def test_unreadable_folder_is_marked_denied(make_tree):
    root_path = make_tree({"ok.txt": 3, "locked/secret.txt": 50})
    locked = root_path / "locked"
    locked.chmod(0)
    try:
        root = scan(str(root_path))
    finally:
        locked.chmod(0o755)

    assert child(root, "locked").denied
    assert child(root, "locked").size == 0
    assert root.size == 3


def test_sort_by_size_orders_largest_first_at_every_level(make_tree):
    root = scan(str(make_tree({
        "small.txt": 1,
        "big/a.bin": 5,
        "big/b.bin": 50,
        "mid.txt": 20,
    })))

    sort_by_size(root)

    assert [c.name for c in root.children] == ["big", "mid.txt", "small.txt"]
    assert [c.name for c in child(root, "big").children] == ["b.bin", "a.bin"]


def test_sort_by_size_breaks_ties_by_name(make_tree):
    root = scan(str(make_tree({"c": 7, "a": 7, "b": 7})))
    sort_by_size(root)
    assert [c.name for c in root.children] == ["a", "b", "c"]


def test_prune_hides_small_entries_but_keeps_sizes(make_tree):
    root = scan(str(make_tree({"big/a.bin": 100, "big/b.bin": 5, "tiny.txt": 3})))

    prune(root, 10)

    assert [c.name for c in root.children] == ["big"]
    assert [c.name for c in child(root, "big").children] == ["a.bin"]
    assert root.size == 108
    assert child(root, "big").size == 105


def test_hard_linked_file_is_counted_once(make_tree):
    root_path = make_tree({"a/data.bin": 1000, "other.txt": 7})
    os.link(root_path / "a/data.bin", root_path / "b-link.bin")

    root = scan(str(root_path))

    assert root.size == 1007
    sizes = sorted([child(child(root, "a"), "data.bin").size, child(root, "b-link.bin").size])
    assert sizes == [0, 1000]


def test_hard_links_in_the_same_folder_are_counted_once(make_tree):
    root_path = make_tree({"x.bin": 500})
    os.link(root_path / "x.bin", root_path / "y.bin")
    os.link(root_path / "x.bin", root_path / "z.bin")

    assert scan(str(root_path)).size == 500


def interrupt_after(n):
    calls = []

    def on_file():
        calls.append(1)
        if len(calls) == n:
            raise KeyboardInterrupt

    return on_file


def total(node):
    return node.size if not node.is_dir else sum(total(c) for c in node.children)


def test_ctrl_c_raises_with_partial_tree(make_tree):
    path = str(make_tree({f"d{i}/f{j}.bin": 10 for i in range(3) for j in range(3)}))

    with pytest.raises(ScanInterrupted) as exc:
        scan(path, on_file=interrupt_after(5))

    root = exc.value.node
    assert root.name == path
    assert root.size == total(root) == 40
    assert all(c.size == total(c) for c in root.children)


def test_ctrl_c_before_any_file_gives_empty_root(make_tree):
    path = str(make_tree({"a.bin": 10}))
    with pytest.raises(ScanInterrupted) as exc:
        scan(path, on_file=interrupt_after(1))
    assert exc.value.node.size == 0
    assert exc.value.node.children == []
