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


def test_progress_reports_file_count_on_stderr(make_tree, capsys):
    main(["--progress", str(make_tree({"a": 1, "b/c": 1, "b/d": 1}))])
    out = capsys.readouterr()
    assert out.err == "\rscanned 3 files\n"
    assert "scanned" not in out.out


def test_no_progress_output_by_default(make_tree, capsys):
    main([str(make_tree({"a": 1}))])
    assert capsys.readouterr().err == ""


def test_progress_redraws_every_n_files():
    import io

    from disk_tree.cli import Progress

    stream = io.StringIO()
    progress = Progress(stream, every=2)
    for _ in range(5):
        progress.tick()
    progress.done()
    assert stream.getvalue() == "\rscanned 2 files\rscanned 4 files\rscanned 5 files\n"


@pytest.mark.parametrize(
    "text, expected",
    [
        ("0", 0),
        ("500", 500),
        ("10K", 10 * 1024),
        ("10k", 10 * 1024),
        ("1.5M", int(1.5 * 1024**2)),
        ("2G", 2 * 1024**3),
        ("2GiB", 2 * 1024**3),
        ("3 MB", 3 * 1024**2),
        ("1T", 1024**4),
    ],
)
def test_size_arg_parses_units(text, expected):
    from disk_tree.cli import size_arg

    assert size_arg(text) == expected


@pytest.mark.parametrize("text", ["", "abc", "-5", "10X", "1.2.3M", "5iB"])
def test_size_arg_rejects_garbage(text):
    import argparse

    from disk_tree.cli import size_arg

    with pytest.raises(argparse.ArgumentTypeError):
        size_arg(text)


def test_min_size_option_hides_small_entries(make_tree, capsys):
    root = make_tree({"big.bin": 2048, "small.txt": 10})

    main(["--min-size", "1K", str(root)])

    assert capsys.readouterr().out.splitlines() == [
        f"{root}  2.0 KiB",
        "└── big.bin  2.0 KiB",
    ]


def test_invalid_min_size_is_rejected(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--min-size", "lots"])
    assert exc.value.code == 2
    assert "invalid size" in capsys.readouterr().err
