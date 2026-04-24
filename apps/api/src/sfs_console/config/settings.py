from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    workspace_root: Path
    service_name: str = "sfs-console-api"

    @classmethod
    def from_env(cls) -> "Settings":
        workspace_root = os.environ.get(
            "SFS_WORKSPACE_ROOT",
            "/workspace/shortform-factory-studio",
        )
        return cls(workspace_root=Path(workspace_root))
