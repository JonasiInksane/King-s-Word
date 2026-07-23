#!/usr/bin/env python3
"""
Export The King's Word chapters to PDF.

Volume covers are taken from Generated_image.png, Generated_image2.png, ...
(also accepts assets/kings-word-*-cover.png as fallbacks).
Number of cover images = number of volumes.

Usage (from Story/):
  python scripts/export_pdf.py
  python scripts/export_pdf.py --combined
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS_DIR = ROOT / "chapters"
EXPORT_DIR = ROOT / "export"
ASSETS_DIR = ROOT / "assets"

# Volume chapter ranges (inclusive), ordered to match cover image order.
# Cover 1 → Vol 1, Cover 2 → Vol 2, …
VOLUME_DEFS = [
    {
        "title": "Volume 1 — The Before / Two Roads",
        "subtitle": "Chapters 1–8",
        "chapters": range(1, 9),
    },
    {
        "title": "Volume 2 — A Step Behind",
        "subtitle": "Chapters 9–24",
        "chapters": range(9, 25),
    },
    {
        "title": "Volume 3 — Quiet Field",
        "subtitle": "Chapters 25–36",
        "chapters": range(25, 37),
    },
    {
        "title": "Volume 4 — One Voice",
        "subtitle": "Chapters 37–50",
        "chapters": range(37, 51),
    },
]

TITLE_PAGE = {
    "title": "王の言霊",
    "english": "The King's Word",
}


def find_covers() -> list[Path]:
    """Discover cover images by Generated_image*.png count, then assets fallbacks."""
    generated = sorted(
        ROOT.glob("Generated_image*.png"),
        key=lambda p: (
            0 if p.name == "Generated_image.png" else 1,
            int(m.group(1)) if (m := re.search(r"Generated_image(\d+)\.png$", p.name)) else 0,
        ),
    )
    if generated:
        return generated

    asset_covers = []
    for name in (
        "kings-word-volume-1-cover.png",
        "kings-word-volume-2-cover.png",
        "kings-word-volume-3-cover.png",
        "kings-word-volume-4-cover.png",
    ):
        path = ASSETS_DIR / name
        if path.exists():
            asset_covers.append(path)
    return asset_covers


def find_font() -> Path:
    """Prefer novel-typical Mincho / serif faces that still cover Japanese."""
    home = Path.home()
    windir = Path("C:/Windows/Fonts")
    # Order: book serif (Mincho) first, then last-resort sans that can render JP.
    candidates = [
        # macOS — Hiragino Mincho is the standard Japanese book face
        Path("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"),
        Path("/System/Library/Fonts/Hiragino Mincho ProN.ttc"),
        # Windows — Yu Mincho / MS Mincho (common for JP novels / documents)
        windir / "yumin.ttf",
        windir / "yumindb.ttf",
        windir / "msmincho.ttc",
        windir / "msgothic.ttc",  # fallback if Mincho missing
        # Bundled / user-installed CJK serif
        home / "Library/Fonts/NotoSerifCJKjp-Regular.otf",
        ROOT / "assets" / "fonts" / "NotoSerifCJKjp-Regular.otf",
        # macOS Latin book serifs (weak JP coverage — last resort before sans)
        Path("/System/Library/Fonts/Supplemental/Baskerville.ttc"),
        Path("/System/Library/Fonts/Supplemental/Georgia.ttf"),
        Path("/System/Library/Fonts/Supplemental/Times New Roman.ttf"),
        Path("/System/Library/Fonts/Palatino.ttc"),
        # Absolute last resort: gothic (not novel-typical, but renders JP)
        Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
        windir / "YuGothR.ttc",
        windir / "meiryo.ttc",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "No novel-capable font found. Install Hiragino Mincho (macOS), "
        "Yu Mincho / MS Mincho (Windows), or place "
        "NotoSerifCJKjp-Regular.otf in assets/fonts/."
    )


def image_size(path: Path) -> tuple[float, float]:
    """Return (width, height) in pixels without requiring Pillow."""
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        # IHDR width/height
        import struct

        return struct.unpack(">II", data[16:24])
    if data[:2] == b"\xff\xd8":
        # JPEG SOF
        import struct

        i = 2
        while i < len(data) - 8:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5 : i + 9])
                return w, h
            length = struct.unpack(">H", data[i + 2 : i + 4])[0]
            i += 2 + length
    raise ValueError(f"Unsupported image format for sizing: {path}")


def chapter_path(n: int) -> Path:
    return CHAPTERS_DIR / f"chapter-{n:02d}.md"


def parse_chapter(md: str) -> tuple[str, str]:
    """Return (title, body_markdown_without_first_heading)."""
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    title = "Chapter"
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            body_start = i + 1
            break
    body = "\n".join(lines[body_start:]).strip()
    return title, body


def md_to_blocks(body: str) -> list[tuple[str, str]]:
    """
    Split markdown body into (kind, text) blocks.
    kind: 'p' paragraph, 'hr' break, 'h' subheading
    """
    blocks: list[tuple[str, str]] = []
    buf: list[str] = []

    def flush():
        nonlocal buf
        if not buf:
            return
        text = " ".join(s.strip() for s in buf if s.strip())
        if text:
            blocks.append(("p", text))
        buf = []

    for line in body.split("\n"):
        stripped = line.strip()
        if stripped == "---":
            flush()
            blocks.append(("hr", ""))
            continue
        if stripped.startswith("## "):
            flush()
            blocks.append(("h", stripped[3:].strip()))
            continue
        if not stripped:
            flush()
            continue
        buf.append(stripped)
    flush()
    return blocks


def strip_md_inline(text: str) -> str:
    """Lightweight inline markdown cleanup for PDF plain rendering."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = text.replace("—", "—").replace("…", "...")
    return text


# Book typography (A4 trade-paperback-ish)
MARGIN_LEFT = 25
MARGIN_RIGHT = 25
MARGIN_TOP = 24
MARGIN_BOTTOM = 24
BODY_SIZE = 11
BODY_LEADING = 6.8  # mm line height ≈ comfortable novel reading
TITLE_SIZE = 16
HALF_TITLE_SIZE = 15


class NovelPDF(FPDF):
    def __init__(self, font_path: Path):
        super().__init__(unit="mm", format="A4")
        self.set_margins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT)
        self.set_auto_page_break(auto=True, margin=MARGIN_BOTTOM)
        # TTC: fpdf2 picks face 0 by default (Hiragino Mincho / Yu Mincho W3-ish).
        self.add_font("Story", fname=str(font_path))
        self.add_font("Story", style="B", fname=str(font_path))
        self.font_family_name = "Story"
        self._cover_pages: set[int] = set()

    def footer(self):
        if self.page_no() in self._cover_pages:
            return
        self.set_y(-14)
        self.set_font(self.font_family_name, size=9)
        self.set_text_color(110, 110, 110)
        self.cell(0, 8, f"{self.page_no()}", align="C")

    def add_cover(self, image: Path, volume_title: str = "", volume_subtitle: str = ""):
        """Full-bleed cover: image fills the entire page (cover-fit, no letterbox)."""
        # Zero margins so nothing insets the bleed
        prev_l, prev_t, prev_r = self.l_margin, self.t_margin, self.r_margin
        self.set_margins(0, 0, 0)
        self.set_auto_page_break(auto=False)

        self.add_page()
        self._cover_pages.add(self.page_no())

        page_w, page_h = self.w, self.h
        try:
            iw, ih = image_size(image)
            img_ratio = iw / float(ih)
            page_ratio = page_w / page_h
            if img_ratio > page_ratio:
                # Image wider than page — fill height, crop sides
                h = page_h
                w = h * img_ratio
                x = (page_w - w) / 2
                y = 0.0
            else:
                # Image taller / narrower — fill width, crop top/bottom
                w = page_w
                h = w / img_ratio
                x = 0.0
                y = (page_h - h) / 2
            self.image(str(image), x=x, y=y, w=w, h=h)
        except Exception:
            # Fallback: stretch to exact page (still full-bleed)
            self.image(str(image), x=0, y=0, w=page_w, h=page_h)

        # Restore body margins for following pages
        self.set_margins(prev_l, prev_t, prev_r)
        self.set_auto_page_break(auto=True, margin=MARGIN_BOTTOM)

        # Half-title on the next page (cover art already carries branding)
        if volume_title:
            self.add_page()
            self.ln(80)
            self.set_font(self.font_family_name, size=HALF_TITLE_SIZE)
            self.set_text_color(25, 25, 25)
            self.cell(0, 10, volume_title, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if volume_subtitle:
                self.ln(3)
                self.set_font(self.font_family_name, size=11)
                self.set_text_color(90, 90, 90)
                self.cell(0, 8, volume_subtitle, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_title_page(self):
        self.add_page()
        self.ln(70)
        self.set_font(self.font_family_name, size=26)
        self.set_text_color(20, 20, 20)
        self.cell(0, 14, TITLE_PAGE["title"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)
        self.set_font(self.font_family_name, size=14)
        self.set_text_color(70, 70, 70)
        self.cell(0, 10, TITLE_PAGE["english"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_chapter(self, title: str, body: str):
        self.add_page()
        self.set_font(self.font_family_name, size=TITLE_SIZE)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 9, title, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(6)
        self.set_draw_color(190, 190, 190)
        mid = self.w / 2
        y = self.get_y()
        self.line(mid - 12, y, mid + 12, y)
        self.ln(10)

        self.set_font(self.font_family_name, size=BODY_SIZE)
        self.set_text_color(30, 30, 30)
        for kind, text in md_to_blocks(body):
            if kind == "hr":
                self.ln(5)
                y = self.get_y()
                self.set_draw_color(200, 200, 200)
                mid = self.w / 2
                self.line(mid - 10, y, mid + 10, y)
                self.ln(7)
                continue
            if kind == "h":
                self.ln(4)
                self.set_font(self.font_family_name, size=12)
                self.multi_cell(
                    0, 7, strip_md_inline(text), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT
                )
                self.set_font(self.font_family_name, size=BODY_SIZE)
                self.ln(3)
                continue
            # paragraph — first-line indent (novel convention)
            cleaned = "\u3000" + strip_md_inline(text)
            self.multi_cell(
                0,
                BODY_LEADING,
                cleaned,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            self.ln(2.8)


def build_volume_pdf(
    pdf: NovelPDF,
    cover: Path | None,
    volume: dict,
    include_series_title: bool = False,
) -> None:
    if include_series_title:
        pdf.add_title_page()
    if cover and cover.exists():
        pdf.add_cover(cover, volume["title"], volume["subtitle"])
    else:
        pdf.add_page()
        pdf.ln(80)
        pdf.set_font(pdf.font_family_name, size=20)
        pdf.cell(0, 12, volume["title"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font(pdf.font_family_name, size=12)
        pdf.cell(0, 8, volume["subtitle"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    for n in volume["chapters"]:
        path = chapter_path(n)
        if not path.exists():
            print(f"  skip missing {path.name}", file=sys.stderr)
            continue
        title, body = parse_chapter(path.read_text(encoding="utf-8"))
        print(f"  + {path.name} — {title}")
        pdf.add_chapter(title, body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export King's Word chapters to PDF")
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Also write one combined PDF with all volumes",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=EXPORT_DIR,
        help="Output directory (default: export/)",
    )
    args = parser.parse_args()

    covers = find_covers()
    if not covers:
        print("No cover images found (Generated_image*.png or assets covers).", file=sys.stderr)
        return 1

    n_covers = len(covers)
    volumes = VOLUME_DEFS[:n_covers]
    if n_covers > len(VOLUME_DEFS):
        print(
            f"Warning: {n_covers} covers but only {len(VOLUME_DEFS)} volume defs; "
            f"extra covers ignored.",
            file=sys.stderr,
        )
    if n_covers < len(VOLUME_DEFS):
        # If only one cover, dump all written chapters into volume 1.
        if n_covers == 1:
            last = max(
                (int(p.stem.split("-")[1]) for p in CHAPTERS_DIR.glob("chapter-*.md")),
                default=10,
            )
            volumes = [
                {
                    "title": "Volume 1 — The King's Word",
                    "subtitle": f"Chapters 1–{last}",
                    "chapters": range(1, last + 1),
                }
            ]

    print(f"Covers found: {n_covers}")
    for i, c in enumerate(covers[: len(volumes)], 1):
        print(f"  Vol {i}: {c.name}")

    font = find_font()
    print(f"Font: {font}")

    args.out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for i, volume in enumerate(volumes):
        cover = covers[i] if i < len(covers) else None
        pdf = NovelPDF(font)
        print(f"\nBuilding {volume['title']}...")
        build_volume_pdf(pdf, cover, volume, include_series_title=(i == 0))
        out_path = args.out / f"Kings-Word-Volume-{i + 1}.pdf"
        pdf.output(str(out_path))
        written.append(out_path)
        print(f"Wrote {out_path}")

    if args.combined:
        print("\nBuilding combined PDF...")
        pdf = NovelPDF(font)
        pdf.add_title_page()
        for i, volume in enumerate(volumes):
            cover = covers[i] if i < len(covers) else None
            build_volume_pdf(pdf, cover, volume, include_series_title=False)
        combined = args.out / "Kings-Word-Complete.pdf"
        pdf.output(str(combined))
        written.append(combined)
        print(f"Wrote {combined}")

    print("\nDone:")
    for p in written:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
