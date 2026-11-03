import argparse
import sys

from disk_tree import __version__
from disk_tree.render import render
from disk_tree.scan import scan, sort_by_size


def non_negative_int(text: str) -> int:
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError("must be 0 or more")
    return value


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
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        root = scan(args.path)
    except OSError as e:
        print(f"disk-tree: {args.path}: {e.strerror}", file=sys.stderr)
        return 1
    sort_by_size(root)
    print(render(root, args.depth))
    return 0


if __name__ == "__main__":
    sys.exit(main())
