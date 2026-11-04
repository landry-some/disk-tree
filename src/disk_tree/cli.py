import argparse
import re
import sys
from typing import TextIO

from disk_tree import __version__
from disk_tree.render import render, render_csv, render_json
from disk_tree.scan import ScanInterrupted, prune, scan, sort_by_size


def non_negative_int(text: str) -> int:
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError("must be 0 or more")
    return value


SIZE_UNITS = {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4, "P": 1024**5}


def size_arg(text: str) -> int:
    """Parse sizes like 500, 10K, 1.5M or 2GiB (1024-based) into bytes."""
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(?:([KMGTP])i?)?B?", text.strip(), re.IGNORECASE)
    if not match:
        raise argparse.ArgumentTypeError(f"invalid size: {text!r} (try 500, 10K, 1.5M, 2G)")
    number, unit = match.groups()
    return int(float(number) * SIZE_UNITS[(unit or "").upper()])


RENDERERS = {"text": render, "json": render_json, "csv": render_csv}


class Progress:
    """Running file count, redrawn in place on one line."""

    def __init__(self, stream: TextIO, every: int = 500):
        self.stream = stream
        self.every = every
        self.count = 0

    def tick(self) -> None:
        self.count += 1
        if self.count % self.every == 0:
            self._write("")

    def done(self) -> None:
        self._write("\n")

    def _write(self, end: str) -> None:
        self.stream.write(f"\rscanned {self.count} files{end}")
        self.stream.flush()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="disk-tree",
        description="Show directory sizes as a tree, largest first.",
    )
    parser.add_argument("path", nargs="?", default=".", help="folder to scan (default: .)")
    parser.add_argument(
        "-d", "--depth", type=non_negative_int, default=3,
        help="levels below PATH to show; sizes always include everything (default: 3)",
    )
    parser.add_argument(
        "--min-size", type=size_arg, default=0, metavar="SIZE",
        help="hide entries smaller than SIZE, e.g. 10M; totals still include them",
    )
    parser.add_argument(
        "-f", "--format", choices=RENDERERS, default="text",
        help="output as a text tree, JSON or CSV (sizes in bytes) (default: text)",
    )
    parser.add_argument(
        "--progress", action="store_true",
        help="show a running file count on stderr while scanning",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    progress = Progress(sys.stderr) if args.progress else None
    status = 0
    try:
        root = scan(args.path, on_file=progress.tick if progress else None)
    except OSError as e:
        print(f"disk-tree: {args.path}: {e.strerror}", file=sys.stderr)
        return 1
    except ScanInterrupted as e:
        root, status = e.node, 130
    except KeyboardInterrupt:
        return 130
    if progress:
        progress.done()
    if status:
        print("disk-tree: interrupted, showing partial results", file=sys.stderr)
    sort_by_size(root)
    if args.min_size:
        prune(root, args.min_size)
    print(RENDERERS[args.format](root, args.depth))
    return status


if __name__ == "__main__":
    sys.exit(main())
