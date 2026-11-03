# disk-tree

A command-line tool that shows where disk space goes, as a size-sorted tree in the
terminal. Point it at a folder and it prints each subfolder with its total size,
largest first, down to the depth you choose.

## Who it's for

Anyone who lives in a terminal and wants a quick answer to "what is filling this disk?"
without opening a GUI or chaining `du | sort | head` by hand.

## Built with

Python 3.11+ standard library only. Tests use pytest.

## Install

```bash
git clone https://github.com/landry-some/disk-tree.git
cd disk-tree
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## Run

```bash
disk-tree                  # current directory, depth 3
disk-tree /var/log         # a specific folder
disk-tree --depth 1 ~      # only the top level of your home folder
disk-tree --progress /     # print a running file count to stderr while scanning
```

Example output:

```
examples/sample  1.2 MiB
├── photos  1.0 MiB
│   ├── 2024  800.0 KiB
│   └── 2025  224.0 KiB
├── notes  150.0 KiB
└── todo.txt  12.0 B
```

Sizes are apparent file sizes (bytes in each file), summed per folder, using 1024-based
units. Symlinks are not followed. Folders that can't be read are counted as 0 bytes
and marked `[denied]`.

## Test

```bash
pip install pytest
pytest
```

## Plans

See [ROADMAP.md](ROADMAP.md).

## License

MIT, see [LICENSE](LICENSE).
