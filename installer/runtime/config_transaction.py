from __future__ import annotations

from pathlib import Path

from .errors import InstallerError
from .fs_atomic import atomic_delete, atomic_write_bytes
from .models import FileChange
from .rollback import RollbackJournal


class StaleConfigurationPreimageError(InstallerError):
    pass


class FileChangePlan:
    """Compose configuration-file edits before any destination is overwritten."""

    def __init__(self) -> None:
        self._preimages: dict[Path, bytes | None] = {}
        self._desired: dict[Path, bytes | None] = {}

    def text(self, path: Path) -> str:
        self._read(path)
        return (self._desired.get(path, self._preimages[path]) or b"").decode("utf-8")

    def replace_text(self, path: Path, text: str) -> None:
        self.replace_bytes(path, text.encode("utf-8"))

    def replace_bytes(self, path: Path, content: bytes | None) -> None:
        self._read(path)
        self._desired[path] = content

    def changes(self) -> tuple[FileChange, ...]:
        return tuple(
            FileChange(path=path, preimage=preimage, desired=self._desired.get(path, preimage))
            for path, preimage in self._preimages.items()
            if self._desired.get(path, preimage) != preimage
        )

    def _read(self, path: Path) -> bytes | None:
        if path not in self._preimages:
            self._preimages[path] = path.read_bytes() if path.exists() else None
        return self._preimages[path] or b""


def apply_file_change_plan(
    changes: tuple[FileChange, ...], *, journal: RollbackJournal
) -> None:
    """Reject stale inputs before applying any planned configuration replacement."""
    for change in changes:
        current = change.path.read_bytes() if change.path.exists() else None
        if current != change.preimage:
            raise StaleConfigurationPreimageError(
                f"Configuration changed after planning: {change.path}"
            )
    for change in changes:
        journal.note_write()
        if change.desired is None:
            if change.path.exists():
                atomic_delete(change.path)
        else:
            atomic_write_bytes(change.path, change.desired)
