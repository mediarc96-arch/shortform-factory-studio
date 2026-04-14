# Reference Shortform Workflow

This workspace is the operational home for `Shortform Factory` character-driven short-form video production.

## Default Rule

Start with reference-image-driven production.

- choose a protagonist
- curate canonical reference images
- create a shot packet
- generate keyframes or stills
- expand into clips
- edit, QA, disclose, and publish

Only escalate to character-specific LoRA or similar training when repeated episodes need tighter identity lock than reference-only generation can provide.

## Required Inputs Per Episode

- protagonist name
- character bible path
- reference folder path
- source issue id
- style target
- output ratio and duration
- disclosure placement
- shot list

## Required Inputs Per Recurring Character

- `bible.md`
- `prompts.md`
- `refs/`
- optional `lora/`
- rights note

## Working Folders

- `characters/`
  - recurring protagonists and their canonical assets
- `episodes/`
  - episode-by-episode packets, renders, and final media
- `shared/`
  - reusable overlays, styles, music, and SFX
- `inbound/references/`
  - raw inspiration or approved upstream reference drops

## Production Gate

Do not mark an episode ready for generation or publish if any of these are missing:

- protagonist
- reference path
- disclosure placement
- final file location plan
- QA signoff requirement
