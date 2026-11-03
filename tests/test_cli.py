import pytest

from disk_tree.cli import main


def test_prints_sorted_tree(make_tree, capsys):
    root = make_tree({"small.txt": 10, "big/a.bin": 2048, "big/b.bin": 1024})

    assert main([str(root)]) == 0

    assert capsys.readouterr().out.splitlines() == [
        f"{root}  3.0 KiB",
        "├── big  3.0 KiB",
        "│   ├── a.bin  2.0 KiB",
        "│   └── b.bin  1.0 KiB",
        "└── small.txt  10 B",
    ]


def test_default_path_is_current_folder(make_tree, capsys, monkeypatch):
    monkeypatch.chdir(make_tree({"a.txt": 5}))
    main([])
    assert capsys.readouterr().out.splitlines()[0] == ".  5 B"


def test_default_depth_is_three(make_tree, capsys):
    main([str(make_tree({"1/2/3/4/f.txt": 1}))])
    assert len(capsys.readouterr().out.splitlines()) == 4


def test_depth_option(make_tree, capsys):
    main(["--depth", "1", str(make_tree({"a/b/c.txt": 1}))])
    assert capsys.readouterr().out.splitlines()[1:] == ["└── a  1 B"]


def test_negative_depth_is_rejected(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--depth", "-1"])
    assert exc.value.code == 2
    assert "must be 0 or more" in capsys.readouterr().err


def test_missing_path_reports_error(tmp_path, capsys):
    missing = tmp_path / "nope"
    assert main([str(missing)]) == 1
    assert capsys.readouterr().err == f"disk-tree: {missing}: No such file or directory\n"
