from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path("/home/kindsr/projects/shortform-factory-studio")
EPISODE_DIR = ROOT / "episodes" / "nabi-korea-trip-001"
FRAMES_DIR = EPISODE_DIR / "renders" / "frames"
FINAL_DIR = EPISODE_DIR / "final"
SOURCE_IMAGE = ROOT / "characters" / "nabi" / "나비_IMG_1286.png"
FONT_PATH = Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
BACKGROUND_SEARCH_DIRS = [
    EPISODE_DIR / "assets" / "backgrounds" / "images",
    ROOT / "shared" / "backgrounds" / "images",
    ROOT / "inbound" / "references" / "backgrounds" / "images",
]
BACKGROUND_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

WIDTH = 1080
HEIGHT = 1920
FPS = 12
SECONDS = 15
TOTAL_FRAMES = FPS * SECONDS


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_PATH), size=size)


def make_gradient(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), top)
    draw = ImageDraw.Draw(image)
    for y in range(HEIGHT):
        ratio = y / max(HEIGHT - 1, 1)
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line([(0, y), (WIDTH, y)], fill=color)
    return image


def cover_resize(image: Image.Image) -> Image.Image:
    source_ratio = image.width / image.height
    target_ratio = WIDTH / HEIGHT
    if source_ratio > target_ratio:
        new_height = HEIGHT
        new_width = int(new_height * source_ratio)
    else:
        new_width = WIDTH
        new_height = int(new_width / source_ratio)
    resized = image.resize((new_width, new_height), Image.LANCZOS)
    left = (new_width - WIDTH) // 2
    top = (new_height - HEIGHT) // 2
    return resized.crop((left, top, left + WIDTH, top + HEIGHT))


def find_background_image(scene_key: str) -> Path | None:
    candidates = [
        scene_key,
        f"{scene_key}-",
        f"{scene_key}_",
    ]
    for directory in BACKGROUND_SEARCH_DIRS:
        if not directory.exists():
            continue
        for path in sorted(directory.iterdir()):
            if not path.is_file() or path.suffix.lower() not in BACKGROUND_EXTENSIONS:
                continue
            name = path.stem.lower()
            if name == scene_key or any(name.startswith(prefix) for prefix in candidates):
                return path
    return None


def build_background(scene_key: str, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image_path = find_background_image(scene_key)
    if image_path:
        image = Image.open(image_path).convert("RGBA")
        bg = cover_resize(image)
        darken = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 70))
        bg.alpha_composite(darken)
        return bg
    return make_gradient(top, bottom).convert("RGBA")


def crop_nabi() -> Image.Image:
    image = Image.open(SOURCE_IMAGE).convert("RGBA")
    width, height = image.size
    crop = image.crop((0, 0, width // 3 + 40, height))
    pixels = crop.load()
    for y in range(crop.height):
        for x in range(crop.width):
            r, g, b, a = pixels[x, y]
            if r < 20 and g < 20 and b < 20:
                pixels[x, y] = (0, 0, 0, 0)
    bbox = crop.getbbox()
    if bbox:
        crop = crop.crop(bbox)
    target_height = 860
    target_width = int(crop.width * (target_height / crop.height))
    return crop.resize((target_width, target_height), Image.LANCZOS)


NABI = crop_nabi()


def draw_text_block(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], font, fill, anchor="la"):
    draw.text(xy, text, font=font, fill=fill, anchor=anchor)


def draw_disclosure(draw: ImageDraw.ImageDraw):
    font = load_font(34)
    text = "AI로 만들어진 영상입니다."
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = WIDTH - 48
    y = HEIGHT - 44
    draw.rounded_rectangle((x - w - 24, y - h - 18, x + 12, y + 10), radius=24, fill=(0, 0, 0, 150))
    draw.text((x, y), text, font=font, fill=(255, 255, 255), anchor="rs")


def draw_nabi(base: Image.Image, t: float, side: str):
    offset_x = int(math.sin(t * 2.8) * 18)
    offset_y = int(math.sin(t * 4.1) * 12)
    x = 650 if side == "right" else 120
    if side == "left":
        nabi = ImageOps.mirror(NABI)
    else:
        nabi = NABI
    base.alpha_composite(nabi, (x + offset_x, 760 + offset_y))


def scene_seoul(t: float) -> Image.Image:
    bg = build_background("seoul", (132, 92, 194), (30, 34, 69))
    draw = ImageDraw.Draw(bg, "RGBA")
    title_font = load_font(92)
    subtitle_font = load_font(56)
    small_font = load_font(42)

    if not find_background_image("seoul"):
        draw.rectangle((0, 1360, WIDTH, HEIGHT), fill=(28, 26, 54, 255))
        for i, x in enumerate(range(40, WIDTH, 120)):
            h = 250 + (i % 5) * 60
            draw.rounded_rectangle((x, 1360 - h, x + 80, 1360), radius=8, fill=(34, 40, 77, 255))
        tower_x = 250
        draw.rectangle((tower_x - 10, 560, tower_x + 10, 1320), fill=(244, 235, 214, 255))
        draw.ellipse((tower_x - 54, 500, tower_x + 54, 608), fill=(255, 136, 88, 255))
        draw.line((tower_x, 390, tower_x, 560), fill=(244, 235, 214, 255), width=6)

    draw.rounded_rectangle((52, 72, 820, 340), radius=44, fill=(0, 0, 0, 96))
    draw.rounded_rectangle((52, 1500, 760, 1696), radius=36, fill=(0, 0, 0, 112))

    draw_text_block(draw, "나비의 한국 여행", (72, 128), title_font, (255, 255, 255), anchor="la")
    draw_text_block(draw, "서울의 밤", (76, 276), subtitle_font, (247, 214, 150), anchor="la")
    draw_text_block(draw, "서울의 밤부터", (76, 1560), small_font, (255, 255, 255), anchor="la")
    draw_text_block(draw, "나비랑 15초 만에 한 바퀴", (76, 1634), small_font, (218, 227, 255), anchor="la")
    bg.alpha_composite(NABI, (640 + int(math.sin(t * 2.4) * 18), 820 + int(math.sin(t * 4.3) * 12)))
    draw_disclosure(draw)
    return bg


def scene_busan(t: float) -> Image.Image:
    bg = build_background("busan", (124, 199, 255), (255, 228, 178))
    draw = ImageDraw.Draw(bg, "RGBA")
    title_font = load_font(92)
    subtitle_font = load_font(56)
    small_font = load_font(42)

    if not find_background_image("busan"):
        draw.rectangle((0, 1260, WIDTH, HEIGHT), fill=(233, 208, 159, 255))
        draw.rectangle((0, 980, WIDTH, 1380), fill=(37, 145, 213, 255))
        for y in range(1020, 1380, 56):
            draw.arc((-50, y - 18, WIDTH + 50, y + 28), 0, 180, fill=(98, 210, 255, 180), width=4)
        for x in range(120, 960, 200):
            draw.arc((x, 760, x + 260, 1040), 180, 360, fill=(236, 248, 255, 255), width=12)
        draw.line((120, 900, 960, 900), fill=(236, 248, 255, 255), width=10)

    draw.rounded_rectangle((52, 72, 820, 340), radius=44, fill=(255, 255, 255, 88))
    draw.rounded_rectangle((52, 1500, 760, 1696), radius=36, fill=(255, 255, 255, 104))

    draw_text_block(draw, "나비의 한국 여행", (72, 128), title_font, (18, 48, 92), anchor="la")
    draw_text_block(draw, "부산의 바다", (76, 276), subtitle_font, (255, 255, 255), anchor="la")
    draw_text_block(draw, "부산의 바다를 지나", (76, 1560), small_font, (35, 63, 84), anchor="la")
    draw_text_block(draw, "시원한 바람까지 담아왔어", (76, 1634), small_font, (46, 88, 109), anchor="la")
    bg.alpha_composite(NABI, (120 + int(math.sin(t * 2.7) * 16), 820 + int(math.sin(t * 3.7) * 10)))
    draw_disclosure(draw)
    return bg


def scene_jeju(t: float) -> Image.Image:
    bg = build_background("jeju", (150, 229, 190), (106, 170, 222))
    draw = ImageDraw.Draw(bg, "RGBA")
    title_font = load_font(92)
    subtitle_font = load_font(56)
    small_font = load_font(42)

    if not find_background_image("jeju"):
        draw.rectangle((0, 1280, WIDTH, HEIGHT), fill=(84, 156, 92, 255))
        draw.polygon([(140, 1280), (420, 840), (700, 1280)], fill=(61, 122, 82, 255))
        draw.polygon([(320, 1280), (610, 760), (920, 1280)], fill=(48, 108, 70, 255))
        draw.rounded_rectangle((120, 980, 280, 1300), radius=32, fill=(123, 105, 79, 255))
        draw.ellipse((150, 1040, 190, 1080), fill=(20, 20, 20, 255))
        draw.ellipse((210, 1040, 250, 1080), fill=(20, 20, 20, 255))
        draw.arc((160, 1120, 240, 1180), 0, 180, fill=(20, 20, 20, 255), width=6)

    draw.rounded_rectangle((52, 72, 820, 340), radius=44, fill=(0, 0, 0, 86))
    draw.rounded_rectangle((52, 1500, 760, 1696), radius=36, fill=(0, 0, 0, 104))

    draw_text_block(draw, "나비의 한국 여행", (72, 128), title_font, (255, 255, 255), anchor="la")
    draw_text_block(draw, "제주의 바람", (76, 276), subtitle_font, (245, 255, 222), anchor="la")
    draw_text_block(draw, "제주의 바람까지", (76, 1560), small_font, (255, 255, 255), anchor="la")
    draw_text_block(draw, "다음 여행도 같이 갈래?", (76, 1634), small_font, (232, 255, 232), anchor="la")
    bg.alpha_composite(NABI, (640 + int(math.sin(t * 2.5) * 14), 820 + int(math.sin(t * 3.9) * 10)))
    draw_disclosure(draw)
    return bg


def render_frames():
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    for file in FRAMES_DIR.glob("frame-*.png"):
        file.unlink()

    for frame in range(TOTAL_FRAMES):
        scene_index = min(frame // (FPS * 5), 2)
        scene_t = (frame % (FPS * 5)) / FPS
        if scene_index == 0:
            image = scene_seoul(scene_t)
        elif scene_index == 1:
            image = scene_busan(scene_t)
        else:
            image = scene_jeju(scene_t)
        image.save(FRAMES_DIR / f"frame-{frame:04d}.png")

    thumb = scene_seoul(1.0)
    thumb.save(FINAL_DIR / "nabi-korea-trip-001-thumb.png")


def encode_video():
    output = FINAL_DIR / "nabi-korea-trip-001-v1.mp4"
    cmd = [
        "ffmpeg",
        "-y",
        "-framerate",
        str(FPS),
        "-i",
        str(FRAMES_DIR / "frame-%04d.png"),
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(output),
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    render_frames()
    encode_video()
