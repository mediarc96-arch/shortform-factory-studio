from __future__ import annotations

from typing import Protocol

from sfs_console.domain import WorkspaceSnapshot


class WorkspaceScanner(Protocol):
    def scan(self) -> WorkspaceSnapshot:
        """Return a read-only snapshot of the production workspace."""
