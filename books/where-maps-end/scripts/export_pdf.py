#!/usr/bin/env python3
"""
Export Where Maps End as a clean novel PDF.

Structure:
  1. Full-page cover (only image in the book)
  2. Half-title
  3. Title page
  4. Copyright
  5. Table of contents (with page numbers)
  6. Chapters
  7. End matter

Usage (from books/where-maps-end/):
  python scripts/export_pdf.py
  python scripts/export_pdf.py --through 10
  python scripts/export_pdf.py --cover ../../assets/where-maps-end-cover-ln.png
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS_DIR = ROOT / "chapters"
EXPORT_DIR = ROOT / "exports"
ASSETS_DIR = ROOT / "assets"
WORKSPACE_ASSETS = ROOT.parents[1] / "assets"
COVER_CANDIDATES = [
    WORKSPACE_ASSETS / "where-maps-end-cover-ln.png",
    ASSETS_DIR / "where-maps-end-cover-ln.png",
    ASSETS_DIR / "covers" / "Cover.png",
    ASSETS_DIR / "covers" / "cover.png",
]

BOOK = {
    "title_series": "Where Maps End",
    "title_volume": "Where the Maps Disagree",
    "book_label": "Volume 1",
    "author": "",
}

MARGIN_LEFT = 28
MARGIN_RIGHT = 28
MARGIN_TOP = 26
MARGIN_BOTTOM = 26
BODY_SIZE = 11
BODY_LEADING = 6.6
CHAPTER_TITLE_SIZE = 15


def find_cover() -> Path | None:
    for path in COVER_CANDIDATES:
        if path.exists():
            return path
    return None


def find_font() -> Path:
    home = Path.home()
    windir = Path("C:/Windows/Fonts")
    candidates = [
        windir / "georgia.ttf",
        windir / "georgiab.ttf",
        windir / "times.ttf",
        windir / "timesnr.ttf",
        Path("/System/Library/Fonts/Supplemental/Georgia.ttf"),
        Path("/System/Library/Fonts/Supplemental/Times New Roman.ttf"),
        windir / "yumin.ttf",
        windir / "msmincho.ttc",
        home / "Library/Fonts/NotoSerifCJKjp-Regular.otf",
        ASSETS_DIR / "fonts" / "NotoSerifCJKjp-Regular.otf",
        windir / "YuGothR.ttc",
        windir / "meiryo.ttc",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "No novel-capable font found. Install Georgia / Times (Windows), "
        "or place a serif TTF/OTF in assets/fonts/."
    )


def chapter_path(n: int) -> Path:
    return CHAPTERS_DIR / f"chapter-{n:02d}.md"


def list_chapters(through: int | None = None) -> list[int]:
    nums = sorted(
        int(p.stem.split("-")[1])
        for p in CHAPTERS_DIR.glob("chapter-*.md")
        if re.fullmatch(r"chapter-\d+", p.stem)
    )
    if through is not None:
        nums = [n for n in nums if n <= through]
    return nums


def parse_chapter(md: str) -> tuple[str, str]:
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
    blocks: list[tuple[str, str]] = []
    buf: list[str] = []

    def flush() -> None:
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
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = text.replace("\u2026", "...")
    return text


def estimate_toc_pages(n_chapters: int) -> int:
    return max(1, 1 + (n_chapters - 1) // 36)


class NovelPDF(FPDF):
    def __init__(self, font_path: Path):
        super().__init__(unit="mm", format="A4")
        self.set_margins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT)
        self.set_auto_page_break(auto=True, margin=MARGIN_BOTTOM)
        self.add_font("Story", fname=str(font_path))
        self.add_font("Story", style="B", fname=str(font_path))
        self.font_family_name = "Story"
        self._no_footer: set[int] = set()
        self._body_start_page: int | None = None

    def footer(self) -> None:
        page = self.page_no()
        if page in self._no_footer:
            return
        self.set_y(-16)
        self.set_font(self.font_family_name, size=9)
        self.set_text_color(120, 120, 120)
        if self._body_start_page is None or page < self._body_start_page:
            return
        body_no = page - self._body_start_page + 1
        self.cell(0, 8, str(body_no), align="C")

    def _centered_text(self, text: str, line_h: float) -> None:
        self.multi_cell(
            0,
            line_h,
            text,
            align="C",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    def add_full_page_cover(self, image: Path) -> None:
        prev_l, prev_t, prev_r = self.l_margin, self.t_margin, self.r_margin
        self.set_margins(0, 0, 0)
        self.set_auto_page_break(auto=False)
        self.add_page()
        self._no_footer.add(self.page_no())
        self.image(
            str(image),
            x=0,
            y=0,
            w=self.w,
            h=self.h,
            keep_aspect_ratio=False,
        )
        self.set_margins(prev_l, prev_t, prev_r)
        self.set_auto_page_break(auto=True, margin=MARGIN_BOTTOM)

    def add_half_title(self) -> None:
        self.add_page()
        self._no_footer.add(self.page_no())
        self.ln(90)
        self.set_font(self.font_family_name, size=18)
        self.set_text_color(25, 25, 25)
        self._centered_text(BOOK["title_series"], 10)

    def add_title_page(self) -> None:
        self.add_page()
        self._no_footer.add(self.page_no())
        self.ln(55)
        self.set_font(self.font_family_name, size=28)
        self.set_text_color(20, 20, 20)
        self._centered_text(BOOK["title_series"], 14)
        self.ln(4)
        self.set_font(self.font_family_name, size=16)
        self.set_text_color(40, 40, 40)
        self._centered_text(BOOK["title_volume"], 10)
        self.ln(10)
        self.set_font(self.font_family_name, size=12)
        self.set_text_color(80, 80, 80)
        self._centered_text(BOOK["book_label"], 8)
        if BOOK["author"]:
            self.ln(28)
            self.set_font(self.font_family_name, size=12)
            self.set_text_color(50, 50, 50)
            self._centered_text(BOOK["author"], 8)

    def add_copyright_page(self) -> None:
        self.add_page()
        self._no_footer.add(self.page_no())
        self.set_auto_page_break(auto=False)
        self.set_y(self.h - 95)
        self.set_font(self.font_family_name, size=9)
        self.set_text_color(70, 70, 70)
        year = date.today().year
        lines = [
            BOOK["title_series"],
            BOOK["title_volume"],
            "",
            f"Copyright (c) {year}",
            "All rights reserved.",
            "",
            "This is a work of fiction. Names, characters, places, and",
            "incidents are products of the author's imagination or are",
            "used fictitiously.",
            "",
            "Cover art included with permission of the rights holder.",
            f"First digital edition {year}.",
        ]
        for line in lines:
            if line:
                self.set_x(self.l_margin)
                self.cell(
                    self.epw,
                    4.5,
                    line,
                    align="C",
                    new_x=XPos.LMARGIN,
                    new_y=YPos.NEXT,
                )
            else:
                self.ln(3.5)
        self.set_auto_page_break(auto=True, margin=MARGIN_BOTTOM)

    def add_chapter(self, title: str, body: str, *, new_page: bool = True) -> None:
        if new_page or self.page == 0:
            self.add_page()
        if self._body_start_page is None:
            self._body_start_page = self.page_no()
        self.start_section(title, level=0)

        self.ln(20)
        self.set_font(self.font_family_name, size=CHAPTER_TITLE_SIZE)
        self.set_text_color(20, 20, 20)
        safe_title = (
            title.replace("\u2014", " - ")
            .replace("\u2013", " - ")
        )
        self._centered_text(safe_title, 8)
        self.ln(4)
        self.set_draw_color(180, 180, 180)
        mid = self.w / 2
        y = self.get_y()
        self.line(mid - 14, y, mid + 14, y)
        self.ln(12)

        self.set_font(self.font_family_name, size=BODY_SIZE)
        self.set_text_color(30, 30, 30)
        first_para = True
        for kind, text in md_to_blocks(body):
            if kind == "hr":
                self.ln(4)
                y = self.get_y()
                self.set_draw_color(200, 200, 200)
                mid = self.w / 2
                self.line(mid - 10, y, mid + 10, y)
                self.ln(6)
                first_para = True
                continue
            if kind == "h":
                self.ln(3)
                self.set_font(self.font_family_name, size=12)
                self.multi_cell(
                    0, 7, strip_md_inline(text), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT
                )
                self.set_font(self.font_family_name, size=BODY_SIZE)
                self.ln(2)
                first_para = True
                continue
            cleaned = strip_md_inline(text)
            if not first_para:
                cleaned = "    " + cleaned
            first_para = False
            self.multi_cell(
                0,
                BODY_LEADING,
                cleaned,
                new_x=XPos.LMARGIN,
                new_y=YPos.NEXT,
            )
            self.ln(2.4)

    def add_end_matter(self) -> None:
        self.add_page()
        self.ln(80)
        self.set_font(self.font_family_name, size=12)
        self.set_text_color(60, 60, 60)
        self._centered_text("End of Volume 1", 8)
        self.ln(6)
        self.set_font(self.font_family_name, size=10)
        self._centered_text(f"{BOOK['title_series']} - {BOOK['title_volume']}", 6)


def render_toc(pdf: NovelPDF, outline) -> None:
    start_page = pdf.page
    reserved = pdf.toc_placeholder.pages if pdf.toc_placeholder else 1
    pdf.set_x(pdf.l_margin)
    usable = pdf.epw

    pdf.set_font(pdf.font_family_name, size=16)
    pdf.set_text_color(25, 25, 25)
    pdf.cell(usable, 10, "Contents", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(8)
    pdf.set_font(pdf.font_family_name, size=10)
    pdf.set_text_color(40, 40, 40)
    for section in outline:
        if getattr(section, "level", 0) != 0:
            continue
        title = (
            section.name.replace("\u2014", " - ")
            .replace("\u2013", " - ")
        )
        abs_page = section.page_number
        if pdf._body_start_page is not None:
            page_str = str(max(1, abs_page - pdf._body_start_page + 1))
        else:
            page_str = str(abs_page)
        page_w = pdf.get_string_width(page_str) + 1
        max_title_w = usable - page_w - pdf.get_string_width(" ... ")
        while title and pdf.get_string_width(title) > max_title_w and len(title) > 12:
            title = title[:-1]
        if title and pdf.get_string_width(title) > max_title_w:
            title = title[:12] + "..."
        title_w = pdf.get_string_width(title)
        gap = usable - title_w - page_w
        n_dots = max(2, int(gap / max(pdf.get_string_width("."), 0.1)) - 1)
        line = f"{title} {'.' * n_dots} {page_str}"
        if pdf.get_string_width(line) > usable:
            line = f"{title}  {page_str}"
        pdf.set_x(pdf.l_margin)
        pdf.cell(usable, 5.8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    final_page = start_page + reserved - 1
    while pdf.page < final_page:
        pdf.add_page()
        pdf._no_footer.add(pdf.page_no())


def build_book(pdf: NovelPDF, cover: Path | None, chapter_nums: list[int]) -> None:
    if cover and cover.exists():
        pdf.add_full_page_cover(cover)
    else:
        print("Warning: no cover image; starting without cover page.", file=sys.stderr)

    pdf.add_half_title()
    pdf.add_title_page()
    pdf.add_copyright_page()

    chapters: list[tuple[str, str]] = []
    for n in chapter_nums:
        path = chapter_path(n)
        if not path.exists():
            print(f"  skip missing {path.name}", file=sys.stderr)
            continue
        title, body = parse_chapter(path.read_text(encoding="utf-8"))
        chapters.append((title, body))
        print(f"  + {path.name} — {title}")

    pdf.add_page()
    pdf._no_footer.add(pdf.page_no())
    toc_pages = estimate_toc_pages(len(chapters))
    pdf.insert_toc_placeholder(render_toc, pages=toc_pages, allow_extra_pages=False)

    for i, (title, body) in enumerate(chapters):
        pdf.add_chapter(title, body, new_page=(i > 0))

    pdf.add_end_matter()


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Where Maps End as a novel PDF")
    parser.add_argument("--out", type=Path, default=EXPORT_DIR, help="Output directory")
    parser.add_argument(
        "--through",
        type=int,
        default=None,
        help="Include chapters 1 through N (default: all written)",
    )
    parser.add_argument("--cover", type=Path, default=None, help="Override cover image path")
    args = parser.parse_args()

    cover = args.cover if args.cover else find_cover()
    print(f"Cover: {cover}" if cover else "Cover: (none found)")

    chapter_nums = list_chapters(args.through)
    if not chapter_nums:
        print("No chapters found in chapters/.", file=sys.stderr)
        return 1
    print(f"Chapters: {chapter_nums[0]}–{chapter_nums[-1]} ({len(chapter_nums)} files)")

    font = find_font()
    print(f"Font: {font}")

    args.out.mkdir(parents=True, exist_ok=True)
    pdf = NovelPDF(font)
    print("\nBuilding novel PDF...")
    build_book(pdf, cover, chapter_nums)

    out_path = args.out / "where-maps-end-vol1.pdf"
    pdf.output(str(out_path))
    print(f"\nWrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
