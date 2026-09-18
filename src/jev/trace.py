"""One JSON line per record."""

import json
from pathlib import Path
from typing import Any


class Tracer:
    def __init__(self, path: str | Path, append: bool = False):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._file = path.open("a" if append else "w")

    def record(self, **fields: Any) -> None:
        self._file.write(json.dumps(fields) + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()
