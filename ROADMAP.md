# Roadmap

Work planned after v0.1. Estimates are rough. Total: about 28.5 hours.

## Features

- [ ] JSON and CSV output (`--format json|csv`) for scripting (2h)
- [ ] `--min-size` to hide entries below a threshold (1.5h)
- [ ] Ignore patterns (`--exclude`, plus reading `.gitignore`) (2.5h)
- [ ] `--follow-symlinks` option with loop detection (1.5h)
- [ ] Colored output that highlights the largest entries (2h)
- [ ] Disk usage mode (allocated blocks) alongside apparent size (1.5h)
- [ ] `--one-file-system` to stay on one mount (1h)
- [ ] Cache of previous scans to show growth since last run (3h)

## Bugs and edge cases

- [ ] Count hard-linked files once (1.5h)
- [ ] Handle names with newlines or invalid UTF-8 in output (1h)
- [ ] Clean exit and partial results on Ctrl-C (1h)

## Performance and refactors

- [ ] Parallel scanning of sibling folders with a thread pool (3h)
- [ ] Split rendering into a formatter interface shared by text/JSON/CSV (1.5h)

## Tests

- [ ] Tests for permission errors, symlink loops and hard links (2h)
- [ ] Benchmark script on a generated large tree (1h)

## Docs

- [ ] Man page and shell completions for bash/zsh/fish (2h)
- [ ] Usage recipes in the README (0.5h)
