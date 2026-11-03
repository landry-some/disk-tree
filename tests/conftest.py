import pytest


@pytest.fixture
def make_tree(tmp_path):
    """Create files from a {relative_path: size_in_bytes} mapping under tmp_path."""

    def make(files: dict[str, int]):
        for rel, size in files.items():
            p = tmp_path / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(b"x" * size)
        return tmp_path

    return make
