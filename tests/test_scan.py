import os

import pytest

from disk_tree.scan import scan


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
