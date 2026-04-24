from __future__ import annotations

import json
from pathlib import Path


class FileSystemCharacterWriter:
    def __init__(self, workspace_root: Path | str) -> None:
        self._root = Path(workspace_root).resolve()
        self._characters_root = (self._root / "characters").resolve()

    def create_template(
        self,
        *,
        slug: str,
        display_name: str,
        series: str,
        voice_default: str,
        rights_status: str,
        negative_prompt: str,
    ) -> tuple[Path, tuple[Path, ...]]:
        root = (self._characters_root / slug).resolve()
        if self._characters_root not in root.parents:
            raise ValueError("character path escapes workspace")
        if root.exists():
            raise ValueError("character already exists")

        root.mkdir(parents=True, exist_ok=False)
        (root / "refs").mkdir()

        files = {
            root / "bible.md": self._bible(display_name, series),
            root / "prompts.md": self._prompts(display_name, negative_prompt),
            root / "rights.md": self._rights(display_name, rights_status),
            root / "voice.json": json.dumps(
                {
                    "display_name": display_name,
                    "voice_default": voice_default,
                    "take_policy": "manual_review_required",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            root / "refs" / "README.md": (
                f"# {display_name} reference pack\n\n"
                "Add only production-safe canonical images or clips here.\n"
            ),
        }

        for path, content in files.items():
            path.write_text(content, encoding="utf-8")

        return root, tuple(files.keys())

    def _bible(self, display_name: str, series: str) -> str:
        return "\n".join(
            [
                f"# {display_name}",
                "",
                f"- series: {series}",
                "- identity: TODO",
                "- visual canon: TODO",
                "- behavior canon: TODO",
                "- continuity risks: TODO",
                "",
            ]
        )

    def _prompts(self, display_name: str, negative_prompt: str) -> str:
        return "\n".join(
            [
                f"# {display_name} prompts",
                "",
                "## Default prompt lock",
                "- Keep the character aligned with canonical references.",
                "",
                "## Negative prompt",
                negative_prompt,
                "",
            ]
        )

    def _rights(self, display_name: str, rights_status: str) -> str:
        return "\n".join(
            [
                f"# {display_name} rights",
                "",
                f"- status: {rights_status}",
                "- external use: blocked until reviewed",
                "- owner approval: TODO",
                "- source notes: TODO",
                "",
            ]
        )
