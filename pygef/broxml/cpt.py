from __future__ import annotations

import io
from pathlib import Path


class BroCPT:
    def __init__(self, file: io.BytesIO | Path | str):
        self.file = file
