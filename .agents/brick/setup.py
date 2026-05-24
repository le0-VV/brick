#!/usr/bin/env python3
from pathlib import Path
import sys


def _bootstrap() -> None:
    brick_root = Path(__file__).resolve().parent
    src = brick_root / "src"
    sys.path.insert(0, str(src))


_bootstrap()

from brick.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["setup", *sys.argv[1:]]))
