import os
from typing import Dict, Iterable, Tuple
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select

from backend.persistance.base import get_sessionmaker
from backend.db.init_schema import ensure_sqlite_schema
from backend.persistance.category import Category
from backend.persistance.subcategory import Subcategory

ASSETS_DIR = os.path.join("backend", "images", "categories and subcategories")


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _file_index(folder: str) -> Dict[str, str]:
    idx: Dict[str, str] = {}
    if not os.path.isdir(folder):
        return idx
    for name in os.listdir(folder):
        path = os.path.join(folder, name)
        if os.path.isfile(path):
            idx[name.lower()] = name
    return idx


def _target_filename(display_name: str) -> str:
    # Keep human-readable names with spaces and symbols for nicer URLs
    # Save as .jpg to match most existing assets
    return f"{display_name}.jpg"


def _choose_bg(name: str) -> Tuple[int, int, int]:
    # Deterministic color per name
    h = abs(hash(name))
    r = 80 + (h % 120)
    g = 80 + ((h // 3) % 120)
    b = 80 + ((h // 7) % 120)
    return (r, g, b)


def _draw_centered_text(img: Image.Image, text: str) -> None:
    draw = ImageDraw.Draw(img)
    W, H = img.size
    # Try to load a common font; fall back to default
    font = None
    for fname in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf",
    ]:
        try:
            font = ImageFont.truetype(fname, size=64)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()
    # Wrap text if very long
    text = text.strip()
    # Compute text size and position (Pillow 9/10 compatibility)
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except Exception:
        # Older Pillow versions
        tw, th = draw.textsize(text, font=font)
    x = (W - tw) // 2
    y = (H - th) // 2
    # Draw shadow for contrast
    shadow_color = (0, 0, 0)
    draw.text((x+2, y+2), text, font=font, fill=shadow_color)
    # Draw main text
    draw.text((x, y), text, font=font, fill=(255, 255, 255))


def generate_missing_images(names: Iterable[str]) -> int:
    _ensure_dir(ASSETS_DIR)
    index = _file_index(ASSETS_DIR)
    created = 0
    for display_name in names:
        fname = _target_filename(display_name)
        # If any file with same base (case-insensitive) exists, skip
        if fname.lower() in index:
            continue
        # Create a simple banner image
        img = Image.new("RGB", (1000, 650), _choose_bg(display_name))
        _draw_centered_text(img, display_name)
        out_path = os.path.join(ASSETS_DIR, fname)
        try:
            img.save(out_path, format="JPEG", quality=92)
            created += 1
        except Exception:
            # If Windows path or name causes issues, fallback to underscores
            safe_name = display_name.replace('/', '_').replace('\\', '_')
            safe_fname = safe_name + ".jpg"
            out_path = os.path.join(ASSETS_DIR, safe_fname)
            img.save(out_path, format="JPEG", quality=92)
            created += 1
    return created


def main() -> None:
    ensure_sqlite_schema()
    Session = get_sessionmaker()
    with Session() as session:
        cat_names = [c.name for c in session.execute(select(Category)).scalars().all()]
        sub_names = [s.name for s in session.execute(select(Subcategory)).scalars().all()]
    # Generate for both sets; duplicates are skipped by filename index
    total_created = generate_missing_images(cat_names + sub_names)
    print(f"Generated images: {total_created}")


if __name__ == "__main__":
    main()
