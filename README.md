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
disk-tree                  # current directory, 3 levels deep
disk-tree /var/log         # a specific folder
disk-tree --depth 1 ~      # only the top level of your home folder
disk-tree --min-size 10M ~ # hide entries smaller than 10 MiB
disk-tree -f json . > sizes.json  # machine-readable output (also: csv)
disk-tree --progress /     # print a running file count to stderr while scanning
disk-tree --help           # all options
```

`--depth` (`-d`) only limits what is printed: folder sizes always include everything
below them. `--depth 0` prints just the total.

`--min-size` hides files and folders smaller than the given size. It takes plain bytes
or a 1024-based unit: `500`, `10K`, `1.5M`, `2G` (`MB`/`MiB` spellings work too). Hidden
entries still count toward their parent's total.

`--format` (`-f`) picks the output: `text` (the tree, default), `json` (nested objects
with `name`, `size` in bytes, `is_dir`, `denied` when a folder couldn't be read, and
`children` for folders) or `csv` (columns `path,size,is_dir,denied`, one row per entry,
parents before children). `--depth` and `--min-size` apply to every format; in JSON, a
folder below the depth limit has an empty `children` list.

Example output (`disk-tree --depth 2 projects`, on a made-up folder):

```
projects  5.9 MiB
├── photo-app  4.1 MiB
│   ├── node_modules  3.2 MiB
│   ├── build  878.9 KiB
│   └── src  23.4 KiB
├── game  1.7 MiB
│   ├── assets  1.7 MiB
│   └── src  14.6 KiB
├── notes  4.1 KiB
│   ├── todo.md  2.9 KiB
│   └── ideas.md  1.2 KiB
└── README.md  512 B
```

Sizes are apparent file sizes (bytes in each file), summed per folder, using 1024-based
units. Symlinks are not followed. A file with several hard links is counted once, at
the first link found; its other links show as 0 bytes. Folders that can't be read are counted as 0 bytes
and marked `[denied]`.

## Test

With the virtualenv from the install step active:

```bash
pip install pytest
pytest
```

## Plans

See [ROADMAP.md](ROADMAP.md).

## License

MIT, see [LICENSE](LICENSE).
