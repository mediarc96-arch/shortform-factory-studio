#!/usr/bin/env python3
"""Compose the final Daehan pilot video:

  opening.mp4 (0–3s) → scene-1..4 → ending.mp4 (26.7–30s)

with 0.3s fadeblack transitions at clip boundaries, TTS narration layered at
per-segment `startSec` offsets, chalkboard typography overlays from
`post/chalkboard-text-spec.json`, and English SRT subtitles.

Scope (pilot v0):
  * Typography is static within each layer's [absoluteStart, absoluteEnd] window
    (stroke-reveal, blink, circle-draw animations are TODO).
  * Fade transitions are implemented as half-overlap FadeIn/FadeOut (0.15s each
    side), giving a ~0.3s black window at each boundary.

Scene/clip media that isn't on disk yet triggers an explicit error listing the
missing paths — intentional, since we don't want silent placeholders.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    ImageSequenceClip,
    VideoFileClip,
    concatenate_videoclips,
    vfx,
    afx,
)

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

HALF_FADE_SEC = 0.15  # half of the 0.3s fadeblack → one side applied to each clip
WIPE_FPS = 30          # frame count for generated wipe bridge clips


# ---------------------------------------------------------------------------
# Spec loaders
# ---------------------------------------------------------------------------


@dataclass
class Zone:
    x: int
    y: int
    w: int
    h: int


def load_job_spec(job_path: Path) -> dict:
    return json.loads(job_path.read_text(encoding="utf-8"))


def load_text_spec(spec_path: Path) -> dict:
    return json.loads(spec_path.read_text(encoding="utf-8"))


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


# ---------------------------------------------------------------------------
# Font / color resolution
# ---------------------------------------------------------------------------


def hex_to_rgba(raw: str) -> tuple[int, int, int, int]:
    value = raw.lstrip("#")
    if len(value) == 6:
        r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
        return (r, g, b, 255)
    if len(value) == 8:
        r, g, b, a = (int(value[i : i + 2], 16) for i in (0, 2, 4, 6))
        return (r, g, b, a)
    raise ValueError(f"Unsupported color literal: {raw}")


def resolve_font_path(raw: str, *, repo_root: Path) -> Path:
    if raw.startswith(("characters/", "shared/", "episodes/")):
        return (repo_root / raw).resolve()
    return Path(raw).resolve()


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    if not path.exists():
        raise FileNotFoundError(f"Font missing: {path}")
    return ImageFont.truetype(str(path), size)


# ---------------------------------------------------------------------------
# Layer rendering (PIL → ImageClip)
# ---------------------------------------------------------------------------


def _resolve_text_bounds(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def render_text_layer_image(
    canvas_w: int,
    canvas_h: int,
    *,
    text: str,
    zone: Zone,
    font: ImageFont.FreeTypeFont,
    color: tuple[int, int, int, int],
    align: str = "left",
    x_offset: int = 0,
    y_offset: int = 0,
    stroke_color: tuple[int, int, int, int] | None = None,
    stroke_width: int = 0,
) -> Image.Image:
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    text_w, text_h = _resolve_text_bounds(draw, text, font)

    base_x = zone.x + x_offset
    if align == "center":
        base_x = zone.x + (zone.w - text_w) // 2 + x_offset
    base_y = zone.y + y_offset

    draw.text(
        (base_x, base_y),
        text,
        font=font,
        fill=color,
        stroke_width=stroke_width,
        stroke_fill=stroke_color,
    )
    return img


def render_text_with_blank_image(
    canvas_w: int,
    canvas_h: int,
    *,
    text: str,
    blank_token: str,
    blank_width: int,
    zone: Zone,
    font: ImageFont.FreeTypeFont,
    color: tuple[int, int, int, int],
    align: str = "center",
    y_offset: int = 0,
) -> tuple[Image.Image, tuple[int, int, int, int] | None]:
    """Render text with [BLANK] replaced by an empty gap of `blank_width` px.
    Returns (image, absolute-canvas blank bbox). bbox is None if token missing."""
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if blank_token not in text:
        text_w, text_h = _resolve_text_bounds(draw, text, font)
        if align == "center":
            base_x = zone.x + (zone.w - text_w) // 2
        else:
            base_x = zone.x
        base_y = zone.y + y_offset
        draw.text((base_x, base_y), text, font=font, fill=color)
        return img, None

    before, after = text.split(blank_token, 1)
    before_w, text_h = _resolve_text_bounds(draw, before, font) if before else (0, 0)
    after_w, after_h = _resolve_text_bounds(draw, after, font) if after else (0, 0)
    text_h = max(text_h, after_h)
    total_w = before_w + blank_width + after_w

    if align == "center":
        base_x = zone.x + (zone.w - total_w) // 2
    else:
        base_x = zone.x
    base_y = zone.y + y_offset

    if before:
        draw.text((base_x, base_y), before, font=font, fill=color)
    if after:
        draw.text((base_x + before_w + blank_width, base_y), after, font=font, fill=color)

    blank_bbox = (base_x + before_w, base_y, blank_width, text_h)
    return img, blank_bbox


def render_button_layer_image(
    canvas_w: int,
    canvas_h: int,
    *,
    zone: Zone,
    text: str,
    font: ImageFont.FreeTypeFont,
    text_color: tuple[int, int, int, int],
    bg_color: tuple[int, int, int, int],
    accent_color: tuple[int, int, int, int] | None,
    corner_radius: int,
    padding_x: int,
    padding_y: int,
) -> Image.Image:
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    text_w, text_h = _resolve_text_bounds(draw, text, font)
    btn_w = text_w + padding_x * 2
    btn_h = text_h + padding_y * 2
    bx = zone.x + (zone.w - btn_w) // 2
    by = zone.y + (zone.h - btn_h) // 2
    draw.rounded_rectangle((bx, by, bx + btn_w, by + btn_h), radius=corner_radius, fill=bg_color)
    if accent_color is not None:
        underline_y = by + btn_h - max(4, corner_radius // 3)
        draw.rectangle(
            (bx + corner_radius, underline_y, bx + btn_w - corner_radius, by + btn_h - 2),
            fill=accent_color,
        )
    draw.text((bx + padding_x, by + padding_y), text, font=font, fill=text_color)
    return img


def render_absolute_rect_image(
    canvas_w: int,
    canvas_h: int,
    *,
    x: int,
    y: int,
    w: int,
    h: int,
    stroke_color: tuple[int, int, int, int],
    stroke_width: int,
    fill_color: tuple[int, int, int, int] | None = None,
) -> Image.Image:
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if fill_color is not None and fill_color[3] > 0:
        draw.rectangle((x, y, x + w, y + h), fill=fill_color)
    draw.rectangle((x, y, x + w, y + h), outline=stroke_color, width=stroke_width)
    return img


def render_rect_layer_image(
    canvas_w: int,
    canvas_h: int,
    *,
    zone: Zone,
    x: int,
    y: int,
    w: int,
    h: int,
    stroke_color: tuple[int, int, int, int],
    stroke_width: int,
) -> Image.Image:
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    ax = zone.x + x
    ay = zone.y + y
    draw.rectangle((ax, ay, ax + w, ay + h), outline=stroke_color, width=stroke_width)
    return img


def render_circle_layer_image(
    canvas_w: int,
    canvas_h: int,
    *,
    zone: Zone,
    cx: int,
    cy: int,
    r: int,
    stroke_color: tuple[int, int, int, int],
    stroke_width: int,
) -> Image.Image:
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    ax, ay = zone.x + cx, zone.y + cy
    draw.ellipse((ax - r, ay - r, ax + r, ay + r), outline=stroke_color, width=stroke_width)
    return img


# ---------------------------------------------------------------------------
# Chalkboard typography compilation
# ---------------------------------------------------------------------------


def build_typography_clips(
    text_spec: dict,
    *,
    canvas_w: int,
    canvas_h: int,
    repo_root: Path,
) -> list[ImageClip]:
    zones = {k: Zone(**v) for k, v in text_spec.get("zones", {}).items()}
    fonts_raw = text_spec.get("fonts", {})
    colors_raw = text_spec.get("colors", {})
    resolved_colors = {k: hex_to_rgba(v) for k, v in colors_raw.items()}
    font_paths = {k: resolve_font_path(v["path"], repo_root=repo_root) for k, v in fonts_raw.items()}

    clips: list[ImageClip] = []
    layers = text_spec.get("layers", [])
    # Index layers by id so attach-to lookups work.
    layers_by_id = {layer["layerId"]: layer for layer in layers}

    for layer in layers:
        start = layer.get("absoluteStartSec")
        end = layer.get("absoluteEndSec")
        if start is None or end is None or end <= start:
            continue

        layer_type = layer.get("type")

        if layer_type == "text-stroke-reveal":
            text = layer.get("text", "")
            blank_token = layer.get("blankToken")
            if blank_token:
                text = text.replace(blank_token, "____")
            font_key = layer.get("font", "chalkboardKo")
            font = load_font(font_paths[font_key], int(layer.get("fontSize", 48)))
            color_key = layer.get("color", "chalkWhite")
            color = resolved_colors.get(color_key, (255, 255, 255, 255))
            zone = zones[layer.get("zone", "chalkboard")]
            align = layer.get("align", "left")
            x_offset = int(layer.get("xOffset", 0))
            y_offset = int(layer.get("yOffset", 0))
            sec_per_char = max(0.02, float(layer.get("strokeRevealSecPerChar", 0.15)))

            n = len(text)
            if n == 0:
                continue
            for i in range(1, n + 1):
                partial = text[:i]
                clip_start = start + (i - 1) * sec_per_char
                if clip_start >= end:
                    break
                clip_end = end if i == n else min(start + i * sec_per_char, end)
                duration = clip_end - clip_start
                if duration <= 0:
                    continue
                image = render_text_layer_image(
                    canvas_w, canvas_h,
                    text=partial,
                    zone=zone,
                    font=font,
                    color=color,
                    align=align,
                    x_offset=x_offset,
                    y_offset=y_offset,
                )
                clips.append(
                    ImageClip(_pil_to_numpy(image))
                    .with_start(clip_start)
                    .with_duration(duration)
                )

        elif layer_type in {"text-fade-in", "text-static"}:
            text = layer.get("text", "")
            blank_token = layer.get("blankToken")
            if blank_token:
                text = text.replace(blank_token, "____")
            font_key = layer.get("font", "chalkboardKo")
            font = load_font(font_paths[font_key], int(layer.get("fontSize", 48)))
            color_key = layer.get("color", "chalkWhite")
            color = resolved_colors.get(color_key, (255, 255, 255, 255))
            zone = zones[layer.get("zone", "chalkboard")]
            align = layer.get("align", "left")
            x_offset = int(layer.get("xOffset", 0))
            y_offset = int(layer.get("yOffset", 0))

            image = render_text_layer_image(
                canvas_w, canvas_h,
                text=text,
                zone=zone,
                font=font,
                color=color,
                align=align,
                x_offset=x_offset,
                y_offset=y_offset,
            )
            clip = (
                ImageClip(_pil_to_numpy(image))
                .with_start(start)
                .with_duration(end - start)
            )
            if layer_type == "text-fade-in":
                fade = float(layer.get("fadeInSec", 0.3))
                clip = clip.with_effects([vfx.FadeIn(fade)])
            clips.append(clip)

        elif layer_type == "text-static-with-blank":
            text = layer.get("text", "")
            blank_token = layer.get("blankToken", "[BLANK]")
            blank_width = int(layer.get("blankWidth", 100))
            font_key = layer.get("font", "chalkboardKo")
            font = load_font(font_paths[font_key], int(layer.get("fontSize", 48)))
            color_key = layer.get("color", "chalkWhite")
            color = resolved_colors.get(color_key, (255, 255, 255, 255))
            zone = zones[layer.get("zone", "chalkboard")]
            align = layer.get("align", "center")
            y_offset = int(layer.get("yOffset", 0))

            image, blank_bbox = render_text_with_blank_image(
                canvas_w, canvas_h,
                text=text,
                blank_token=blank_token,
                blank_width=blank_width,
                zone=zone,
                font=font,
                color=color,
                align=align,
                y_offset=y_offset,
            )
            layer["_blankBboxAbsolute"] = blank_bbox
            clips.append(
                ImageClip(_pil_to_numpy(image))
                .with_start(start)
                .with_duration(end - start)
            )

        elif layer_type == "button-fade-in":
            text = layer.get("text", "")
            font_key = layer.get("font", "ctaButton")
            font = load_font(font_paths[font_key], int(layer.get("fontSize", 48)))
            zone = zones[layer.get("zone", "ctaButton")]
            text_color = resolved_colors.get(layer.get("textColor"), (26, 26, 26, 255))
            bg_color = resolved_colors.get(layer.get("bgColor"), (255, 255, 255, 230))
            accent_key = layer.get("accentColor")
            accent_color = resolved_colors.get(accent_key) if accent_key else None
            corner_radius = int(layer.get("cornerRadius", 16))
            padding_x = int(layer.get("paddingX", 40))
            padding_y = int(layer.get("paddingY", 18))
            fade_in = float(layer.get("fadeInSec", 0.3))

            image = render_button_layer_image(
                canvas_w, canvas_h,
                zone=zone,
                text=text,
                font=font,
                text_color=text_color,
                bg_color=bg_color,
                accent_color=accent_color,
                corner_radius=corner_radius,
                padding_x=padding_x,
                padding_y=padding_y,
            )
            clip = (
                ImageClip(_pil_to_numpy(image))
                .with_start(start)
                .with_duration(end - start)
                .with_effects([vfx.FadeIn(fade_in)])
            )
            clips.append(clip)

        elif layer_type == "rect-blink":
            attach_id = layer.get("attachToLayer")
            target = layers_by_id.get(attach_id)
            if not target:
                continue
            if target.get("type") == "text-static-with-blank":
                abs_bbox = target.get("_blankBboxAbsolute")
                if abs_bbox is None:
                    continue
                ax, ay, bw, bh = abs_bbox
            else:
                token = layer.get("attachToToken", "___")
                rel_bbox = _estimate_token_bbox(
                    target,
                    token=token,
                    zones=zones,
                    font_paths=font_paths,
                )
                if rel_bbox is None:
                    continue
                rx, ry, bw, bh = rel_bbox
                target_zone = zones[target.get("zone", "chalkboard")]
                ax = target_zone.x + rx
                ay = target_zone.y + ry

            padding = int(layer.get("padding", 8))
            stroke_color = resolved_colors.get(layer.get("strokeColor"), (255, 224, 102, 255))
            stroke_width = int(layer.get("strokeWidth", 4))
            fill_color = resolved_colors.get(layer.get("fillColor")) if layer.get("fillColor") else None

            rect_image = render_absolute_rect_image(
                canvas_w, canvas_h,
                x=ax - padding,
                y=ay - padding,
                w=bw + padding * 2,
                h=bh + padding * 2,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                fill_color=fill_color,
            )
            rect_numpy = _pil_to_numpy(rect_image)

            blink_interval = float(layer.get("blinkIntervalSec", 0.0))
            duration = end - start
            if blink_interval <= 0:
                clips.append(
                    ImageClip(rect_numpy).with_start(start).with_duration(duration)
                )
            else:
                t = 0.0
                show = True
                while t < duration:
                    seg_end = min(t + blink_interval, duration)
                    if show:
                        clips.append(
                            ImageClip(rect_numpy)
                            .with_start(start + t)
                            .with_duration(seg_end - t)
                        )
                    show = not show
                    t = seg_end

        elif layer_type == "shape-circle-highlight":
            attach_id = layer.get("attachToLayer")
            target = layers_by_id.get(attach_id)
            if not target:
                continue
            font_key = target.get("font", "chalkboardKo")
            font = load_font(font_paths[font_key], int(target.get("fontSize", 48)))
            zone = zones[target.get("zone", "chalkboard")]
            # Centre on the target text's bounding box.
            dummy = Image.new("RGBA", (1, 1))
            draw = ImageDraw.Draw(dummy)
            tw, th = _resolve_text_bounds(draw, target.get("text", ""), font)
            cx = int(target.get("xOffset", 0)) + tw // 2
            cy = int(target.get("yOffset", 0)) + th // 2
            padding = int(layer.get("padding", 12))
            radius = max(tw, th) // 2 + padding
            image = render_circle_layer_image(
                canvas_w, canvas_h,
                zone=zone,
                cx=cx,
                cy=cy,
                r=radius,
                stroke_color=resolved_colors.get(layer.get("strokeColor"), (255, 224, 102, 255)),
                stroke_width=int(layer.get("strokeWidth", 6)),
            )
            clips.append(
                ImageClip(_pil_to_numpy(image)).with_start(start).with_duration(end - start)
            )
        # text-static handled in the text-stroke-reveal branch by layer_type match above.

    return clips


def _estimate_token_bbox(
    target_layer: dict,
    *,
    token: str,
    zones: dict[str, Zone],
    font_paths: dict[str, Path],
) -> tuple[int, int, int, int] | None:
    """Best-effort: estimate where `token` sits within `target_layer`'s rendered
    text, relative to the target's zone origin. Returns (x, y, w, h)."""
    text = target_layer.get("text", "")
    if token not in text:
        return None
    font = load_font(font_paths[target_layer.get("font", "chalkboardKo")], int(target_layer.get("fontSize", 48)))
    zone = zones[target_layer.get("zone", "chalkboard")]
    dummy = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy)
    full_w, full_h = _resolve_text_bounds(draw, text, font)
    before_w, _ = _resolve_text_bounds(draw, text.split(token)[0], font)
    token_w, token_h = _resolve_text_bounds(draw, token, font)

    align = target_layer.get("align", "left")
    x_offset = int(target_layer.get("xOffset", 0))
    y_offset = int(target_layer.get("yOffset", 0))

    if align == "center":
        base_x = (zone.w - full_w) // 2 + x_offset
    else:
        base_x = x_offset

    return (base_x + before_w, y_offset, token_w, token_h)


def _pil_to_numpy(image: Image.Image):
    import numpy as np

    return np.asarray(image)


# ---------------------------------------------------------------------------
# Subtitle rendering (SRT → ImageClips)
# ---------------------------------------------------------------------------


SRT_TIME_RE = re.compile(r"(\d{2}):(\d{2}):(\d{2})[,.](\d{3})")


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    text = path.read_text(encoding="utf-8")
    entries: list[tuple[float, float, str]] = []
    for block in re.split(r"\r?\n\r?\n", text.strip()):
        lines = [line for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        times_line = lines[1] if SRT_TIME_RE.search(lines[1]) else lines[0]
        matches = SRT_TIME_RE.findall(times_line)
        if len(matches) != 2:
            continue
        start = _srt_time_to_sec(matches[0])
        end = _srt_time_to_sec(matches[1])
        caption = "\n".join(lines[2:] if SRT_TIME_RE.search(lines[1]) else lines[1:])
        entries.append((start, end, caption))
    return entries


def _srt_time_to_sec(parts: tuple[str, str, str, str]) -> float:
    h, m, s, ms = parts
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000.0


def build_subtitle_clips(
    srt_path: Path,
    *,
    subtitle_spec: dict,
    zones: dict[str, Zone],
    font_paths: dict[str, Path],
    colors: dict[str, tuple[int, int, int, int]],
    canvas_w: int,
    canvas_h: int,
) -> list[ImageClip]:
    if not srt_path.exists():
        return []
    font = load_font(font_paths[subtitle_spec["font"]], int(subtitle_spec.get("fontSize", 36)))
    zone = zones[subtitle_spec.get("zone", "subtitle")]
    color = colors.get(subtitle_spec.get("color", "subtitleText"), (255, 255, 255, 255))
    shadow_cfg = subtitle_spec.get("shadow") or {}
    shadow_color = colors.get(shadow_cfg.get("color"), (0, 0, 0, 153))
    bg_cfg = subtitle_spec.get("background") or {}
    bg_color = colors.get(bg_cfg.get("color")) if bg_cfg.get("color") else None
    bg_pad_x = int(bg_cfg.get("paddingX", 24))
    bg_pad_y = int(bg_cfg.get("paddingY", 12))
    bg_corner = int(bg_cfg.get("cornerRadius", 10))

    clips: list[ImageClip] = []
    for start, end, caption in parse_srt(srt_path):
        image = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        text_w, text_h = _resolve_text_bounds(draw, caption, font)
        base_x = zone.x + (zone.w - text_w) // 2
        base_y = zone.y + 10
        if bg_color is not None:
            draw.rounded_rectangle(
                (base_x - bg_pad_x, base_y - bg_pad_y, base_x + text_w + bg_pad_x, base_y + text_h + bg_pad_y),
                radius=bg_corner,
                fill=bg_color,
            )
        draw.text(
            (base_x, base_y),
            caption,
            font=font,
            fill=color,
            stroke_fill=shadow_color,
            stroke_width=2,
        )
        clips.append(
            ImageClip(_pil_to_numpy(image)).with_start(start).with_duration(end - start)
        )
    return clips


# ---------------------------------------------------------------------------
# Clip assembly
# ---------------------------------------------------------------------------


def load_and_trim_clip(path: Path, *, duration: float, trim_from_start: bool = True) -> VideoFileClip:
    clip = VideoFileClip(str(path))
    if trim_from_start:
        clip = clip.subclipped(0, min(duration, clip.duration))
    else:
        clip = clip.subclipped(max(0.0, clip.duration - duration), clip.duration)
    return clip


def apply_fade_pair(clip, *, fade_in: float = 0.0, fade_out: float = 0.0):
    effects = []
    if fade_in > 0:
        effects.append(vfx.FadeIn(fade_in))
    if fade_out > 0:
        effects.append(vfx.FadeOut(fade_out))
    if effects:
        clip = clip.with_effects(effects)
    return clip


def _actual_scene_duration(scene: dict) -> float:
    pp = scene.get("postProduction") or {}
    if "trimToSec" in pp:
        return float(pp["trimToSec"])
    return float(scene["durationSec"])


def _first_frame(clip):
    return clip.get_frame(0.0)


def _last_frame(clip):
    step = 1.0 / (clip.fps or WIPE_FPS)
    return clip.get_frame(max(0.0, clip.duration - step))


def _build_wipe_bridge(
    out_frame,
    in_frame,
    *,
    duration_sec: float,
    canvas_size: tuple[int, int],
    fps: int = WIPE_FPS,
    direction: str = "right",
):
    import numpy as np

    cw, ch = canvas_size

    def _ensure_size(arr):
        if arr.shape[1] == cw and arr.shape[0] == ch:
            return arr
        pil = Image.fromarray(arr).resize((cw, ch), Image.LANCZOS)
        return np.asarray(pil)

    out_frame = _ensure_size(out_frame)
    in_frame = _ensure_size(in_frame)
    num = max(1, int(round(duration_sec * fps)))
    frames = []
    for i in range(num):
        progress = (i + 1) / num
        threshold = max(1, int(cw * progress))
        frame = out_frame.copy()
        if direction == "right":
            frame[:, :threshold] = in_frame[:, :threshold]
        else:  # left
            frame[:, cw - threshold:] = in_frame[:, cw - threshold:]
        frames.append(frame)
    return ImageSequenceClip(frames, fps=fps)


def _load_and_normalize(path: Path, *, canvas_size: tuple[int, int], duration: float, from_start: bool = True) -> VideoFileClip:
    clip = VideoFileClip(str(path))
    if from_start:
        clip = clip.subclipped(0, min(duration, clip.duration))
    else:
        clip = clip.subclipped(max(0.0, clip.duration - duration), clip.duration)
    if tuple(clip.size) != tuple(canvas_size):
        clip = clip.resized(canvas_size)
    return clip


def build_video_track(job: dict, episode_dir: Path, repo_root: Path, *, canvas_size: tuple[int, int]):
    fixed = job.get("fixedClips") or {}
    opening_cfg = fixed.get("opening") or {}
    ending_cfg = fixed.get("ending") or {}

    transitions = job.get("transitionsBetweenClips") or {}
    has_wipe = any((t or {}).get("type") == "wipe-right" for t in transitions.values())

    opening_clip = None
    opening_path = (repo_root / opening_cfg["source"]).resolve() if opening_cfg else None
    if opening_path and opening_path.exists():
        opening_clip = _load_and_normalize(
            opening_path,
            canvas_size=canvas_size,
            duration=float(opening_cfg.get("durationSec", 3.0)),
        )
        if not has_wipe:
            opening_clip = apply_fade_pair(opening_clip, fade_out=HALF_FADE_SEC)

    scene_clips = []
    for scene in job.get("scenes") or []:
        scene_path = (episode_dir / scene["outputPath"]).resolve()
        if not scene_path.exists():
            raise FileNotFoundError(
                f"Scene video missing: {scene_path.relative_to(episode_dir)}  (run orchestrate_scenes.py first)"
            )
        actual_dur = _actual_scene_duration(scene)
        scene_clip = VideoFileClip(str(scene_path)).subclipped(0, actual_dur).without_audio()
        if tuple(scene_clip.size) != tuple(canvas_size):
            scene_clip = scene_clip.resized(canvas_size)
        if not has_wipe:
            scene_clip = apply_fade_pair(scene_clip, fade_in=HALF_FADE_SEC, fade_out=HALF_FADE_SEC)
        scene_clips.append(scene_clip)

    ending_clip = None
    ending_path = (repo_root / ending_cfg["source"]).resolve() if ending_cfg else None
    if ending_path and ending_path.exists():
        ending_clip = _load_and_normalize(
            ending_path,
            canvas_size=canvas_size,
            duration=float(ending_cfg.get("durationSec", 3.3)),
        )
        if not has_wipe:
            ending_clip = apply_fade_pair(ending_clip, fade_in=HALF_FADE_SEC)

    timeline = []
    if opening_clip is not None:
        timeline.append(opening_clip)

    opening_to_scene1 = (transitions.get("openingToScene1") or {})
    if (
        opening_clip is not None
        and scene_clips
        and opening_to_scene1.get("type") == "wipe-right"
    ):
        bridge = _build_wipe_bridge(
            _last_frame(opening_clip),
            _first_frame(scene_clips[0]),
            duration_sec=float(opening_to_scene1.get("durationSec", 0.5)),
            canvas_size=canvas_size,
        )
        timeline.append(bridge)

    timeline.extend(scene_clips)

    last_to_ending_key = f"scene{len(scene_clips)}ToEnding"
    last_to_ending = transitions.get(last_to_ending_key) or {}
    if (
        scene_clips
        and ending_clip is not None
        and last_to_ending.get("type") == "wipe-right"
    ):
        bridge = _build_wipe_bridge(
            _last_frame(scene_clips[-1]),
            _first_frame(ending_clip),
            duration_sec=float(last_to_ending.get("durationSec", 0.5)),
            canvas_size=canvas_size,
        )
        timeline.append(bridge)

    if ending_clip is not None:
        timeline.append(ending_clip)

    if not timeline:
        raise RuntimeError("No clips to concatenate. Check fixedClips and scene outputs.")

    return concatenate_videoclips(timeline, method="compose")


def _safe_audio_clip(path: Path) -> AudioFileClip | None:
    """Return an AudioFileClip if `path` has an audio stream, else None.
    MoviePy raises KeyError('audio_bitrate') on audio-less mp4s; guard explicitly."""
    if not path.exists():
        return None
    try:
        return AudioFileClip(str(path))
    except (KeyError, IOError) as exc:
        print(f"warn  {path.name} has no usable audio stream ({exc}); skipping")
        return None


def build_audio_track(job: dict, episode_dir: Path, *, total_duration: float, narration_dir: Path, timing_path: Path | None):
    layers = []

    fixed = job.get("fixedClips") or {}
    opening_cfg = fixed.get("opening") or {}
    ending_cfg = fixed.get("ending") or {}

    if opening_cfg.get("keepOriginalAudio", True):
        opening_path = (REPO_ROOT / opening_cfg["source"]).resolve()
        a = _safe_audio_clip(opening_path)
        if a is not None:
            dur = min(float(opening_cfg.get("durationSec", 3.0)), a.duration)
            layers.append(a.subclipped(0, dur).with_start(float(opening_cfg.get("startSec", 0.0))))

    if ending_cfg.get("keepOriginalAudio", True):
        ending_path = (REPO_ROOT / ending_cfg["source"]).resolve()
        a = _safe_audio_clip(ending_path)
        if a is not None:
            dur = min(float(ending_cfg.get("durationSec", 3.3)), a.duration)
            layers.append(a.subclipped(0, dur).with_start(float(ending_cfg.get("startSec", 26.7))))

    if timing_path and timing_path.exists():
        timing = json.loads(timing_path.read_text(encoding="utf-8"))
        for seg in timing.get("segments", []):
            seg_path = (episode_dir / seg["file"]).resolve()
            if not seg_path.exists():
                print(f"warn  missing TTS clip: {seg_path}")
                continue
            a = AudioFileClip(str(seg_path))
            layers.append(a.with_start(float(seg["startSec"])))

    if not layers:
        return None
    return CompositeAudioClip(layers)


# ---------------------------------------------------------------------------
# Top-level entry
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compose final Daehan pilot video with typography and TTS.")
    parser.add_argument("--episode-dir", required=True)
    parser.add_argument("--job-file", default="video-generation-job.json", help="Relative to episode-dir")
    parser.add_argument("--text-spec", default="post/chalkboard-text-spec.json", help="Relative to episode-dir")
    parser.add_argument("--srt", default="post/subtitles-en.srt", help="Relative to episode-dir")
    parser.add_argument("--narration-dir", default="audio", help="Relative to episode-dir")
    parser.add_argument("--narration-timing", default="audio/narration-timing.json", help="Relative to episode-dir")
    parser.add_argument("--output", default=None, help="Relative to episode-dir (defaults to renders/<slug>.mp4)")
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--env-file", default=".env")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_env_file(Path(args.env_file).resolve())

    episode_dir = Path(args.episode_dir).resolve()
    job = load_job_spec(episode_dir / args.job_file)
    text_spec = load_text_spec(episode_dir / args.text_spec)

    canvas = text_spec.get("canvas") or {}
    canvas_res = canvas.get("resolution") or {"w": 1920, "h": 1080}
    canvas_w = int(canvas_res["w"])
    canvas_h = int(canvas_res["h"])

    video = build_video_track(job, episode_dir, REPO_ROOT, canvas_size=(canvas_w, canvas_h))

    # Assemble typography + subtitle overlays
    zones = {k: Zone(**v) for k, v in text_spec.get("zones", {}).items()}
    fonts_raw = text_spec.get("fonts", {})
    font_paths = {k: resolve_font_path(v["path"], repo_root=REPO_ROOT) for k, v in fonts_raw.items()}
    colors = {k: hex_to_rgba(v) for k, v in (text_spec.get("colors") or {}).items()}

    overlay_clips = build_typography_clips(text_spec, canvas_w=canvas_w, canvas_h=canvas_h, repo_root=REPO_ROOT)

    srt_path = episode_dir / args.srt
    subtitle_spec = text_spec.get("subtitlesEn") or {}
    if subtitle_spec:
        overlay_clips.extend(
            build_subtitle_clips(
                srt_path,
                subtitle_spec=subtitle_spec,
                zones=zones,
                font_paths=font_paths,
                colors=colors,
                canvas_w=canvas_w,
                canvas_h=canvas_h,
            )
        )

    composite = CompositeVideoClip([video.resized((canvas_w, canvas_h))] + overlay_clips, size=(canvas_w, canvas_h))

    audio = build_audio_track(
        job,
        episode_dir,
        total_duration=composite.duration,
        narration_dir=episode_dir / args.narration_dir,
        timing_path=episode_dir / args.narration_timing,
    )
    if audio is not None:
        composite = composite.with_audio(audio)

    output_rel = args.output or f"renders/{episode_dir.name}.mp4"
    output_path = (episode_dir / output_rel).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    composite.write_videofile(
        str(output_path),
        fps=args.fps,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="medium",
        ffmpeg_params=["-pix_fmt", "yuv420p"],
    )

    print(str(output_path))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise
