"""Safe file writing shared by every command that writes output."""

import os
import tempfile
from collections.abc import Callable
from pathlib import Path


def atomic_write(path: Path, force: bool, write_fn: Callable[[Path], None]) -> None:
    """Write through a temp file in the target folder, refusing to overwrite unless forced."""
    if path.exists() and not force:
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    os.close(fd)  # Closed at once so Windows allows the writer and the cleanup to open it.
    tmp = Path(name)
    try:
        write_fn(tmp)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
