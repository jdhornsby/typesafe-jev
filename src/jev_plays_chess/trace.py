"""One JSON line per move."""

import json
from pathlib import Path
from typing import Any


class Tracer:
    def __init__(self, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self._file = path.open("w")

    def record(self, **fields: Any) -> None:
        self._file.write(json.dumps(fields) + "\n")

    def close(self) -> None:
        self._file.close()
