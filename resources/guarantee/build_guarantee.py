#!/usr/bin/env python3
"""Overlay exact typography on Iowa Guarantee Clause backgrounds.

Outputs:
  IA_guarantee_clause.png        1080x1350
  IA_guarantee_clause_xcard.png  1600x900
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
REFS = ROOT / "refs"
FONT_DIR = Path("/tmp/ia-fonts")
CASLON = Path("/usr/share/fonts/truetype/sand-box/google/Libre Caslon Text")
PLAYFAIR_SC = Path("/usr/share/fonts/truetype/sand-box/google/Playfair Display SC")
CORMORANT_SC = Path("/usr/share/fonts/truetype/sand-box/google/Cormorant SC")

# Iowa-toned palette
NAVY = (16, 42, 84)
NAVY_DEEP = (10, 28, 58)
RED = (168, 28, 40)
GOLD = (168, 122, 42)
GOLD_SOFT = (112, 78, 26)
INK = (32, 24, 16)
INK_SOFT = (52, 40, 28)
CREAM = (248, 239, 220)
PANEL = (250, 243, 226)

HEADLINE = "Did you know? It's NOT your job to prove our elections are free and fair. The Guarantee Clause puts that on the government."
CLAUSE = "The United States shall guarantee to every State in this Union a Republican Form of Government"
CLAUSE_CITE = "U.S. Const. Art. IV, § 4"
EO_QUOTE = (
    "The Federal Government has an unavoidable duty under Article II of the "
    "Constitution of the United States to enforce Federal law, which includes "
    "preventing violations of Federal criminal law and maintaining public "
    "confidence in election outcomes."
)
EO_CITE = "Executive Order 14399, § 1  ·  91 FR 17125  ·  signed March 31, 2026"


def font(path: Path | str, size: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def F(*parts, size: int) -> ImageFont.FreeTypeFont:
    return font(FONT_DIR.joinpath(*parts) if len(parts) == 1 else Path(*parts), size)


def playfair(weight: int, size: int, italic: bool = False) -> ImageFont.FreeTypeFont:
    name = f"Playfair-Italic-{weight}.ttf" if italic else f"Playfair-{weight}.ttf"
    return font(FONT_DIR / name, size)


def garamond(weight: int, size: int, italic: bool = False) -> ImageFont.FreeTypeFont:
    name = f"EBGaramond-Italic-{weight}.ttf" if italic else f"EBGaramond-{weight}.ttf"
    return font(FONT_DIR / name, size)


def cinzel(weight: int, size: int) -> ImageFont.FreeTypeFont:
    return font(FONT_DIR / f"Cinzel-{weight}.ttf", size)


def caslon(style: str, size: int) -> ImageFont.FreeTypeFont:
    return font(CASLON / f"LibreCaslonText-{style}.ttf", size)


def sc_playfair(style: str, size: int) -> ImageFont.FreeTypeFont:
    return font(PLAYFAIR_SC / f"PlayfairDisplaySC-{style}.ttf", size)


def sc_cormorant(style: str, size: int) -> ImageFont.FreeTypeFont:
    return font(CORMORANT_SC / f"CormorantSC-{style}.ttf", size)


def wrap_text(text: str, font_obj: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if font_obj.getlength(trial) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_size(draw: ImageDraw.ImageDraw, text: str, font_obj: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font_obj)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_centered(
    draw: ImageDraw.ImageDraw,
    y: float,
    text: str,
    font_obj: ImageFont.FreeTypeFont,
    fill,
    x_center: float,
    stroke_width: int = 0,
    stroke_fill=None,
    tracking: int = 0,
) -> float:
    """Draw a single centered line. Returns the y just below the line (using font metrics)."""
    if tracking:
        # manual letter-spacing
        width = 0
        for i, ch in enumerate(text):
            width += draw.textlength(ch, font=font_obj)
            if i < len(text) - 1:
                width += tracking
        x = x_center - width / 2
        cx = x
        for i, ch in enumerate(text):
            draw.text((cx, y), ch, font=font_obj, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
            cx += draw.textlength(ch, font=font_obj) + tracking
    else:
        w = draw.textlength(text, font=font_obj)
        draw.text((x_center - w / 2, y), text, font=font_obj, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
    ascent, descent = font_obj.getmetrics()
    return y + ascent + descent


def draw_lines_centered(
    draw: ImageDraw.ImageDraw,
    y: float,
    lines: list[str],
    font_obj: ImageFont.FreeTypeFont,
    fill,
    x_center: float,
    leading: float | None = None,
) -> float:
    ascent, descent = font_obj.getmetrics()
    lh = (ascent + descent) if leading is None else leading
    for i, line in enumerate(lines):
        w = draw.textlength(line, font=font_obj)
        draw.text((x_center - w / 2, y), line, font=font_obj, fill=fill)
        y += lh * (0.95 if i == len(lines) - 1 else 1.0)
    return y


def draw_wrapped_centered(
    draw: ImageDraw.ImageDraw,
    y: float,
    text: str,
    font_obj: ImageFont.FreeTypeFont,
    fill,
    x_center: float,
    max_width: int,
    leading: float | None = None,
    quotes: bool = False,
) -> float:
    body = f"“{text}”" if quotes else text
    lines = wrap_text(body, font_obj, max_width)
    return draw_lines_centered(draw, y, lines, font_obj, fill, x_center, leading)


def gold_rule(draw: ImageDraw.ImageDraw, y: float, x0: float, x1: float, width: int = 2) -> None:
    mid = (x0 + x1) / 2
    # slightly narrower double rule with a gold diamond/dot
    draw.line([(x0, y), (x1, y)], fill=GOLD, width=width)
    draw.line([(x0 + 8, y + 4), (x1 - 8, y + 4)], fill=GOLD_SOFT, width=1)
    r = 4
    cx, cy = mid, y + 2
    draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=GOLD)


def draw_frame(img: Image.Image, inset: int = 18) -> None:
    """Formal Iowa-flag border: navy, gold, red, gold hairline."""
    d = ImageDraw.Draw(img)
    w, h = img.size
    # outer navy
    d.rectangle([0, 0, w - 1, h - 1], outline=NAVY_DEEP, width=10)
    d.rectangle([8, 8, w - 9, h - 9], outline=GOLD, width=3)
    d.rectangle([13, 13, w - 14, h - 14], outline=RED, width=2)
    d.rectangle([18, 18, w - 19, h - 19], outline=GOLD, width=1)
    # tiny flag-color corner ticks, no text
    for (x0, y0) in [(22, 22), (w - 70, 22), (22, h - 36), (w - 70, h - 36)]:
        d.rectangle([x0, y0, x0 + 48, y0 + 6], fill=NAVY)
        d.rectangle([x0, y0 + 6, x0 + 16, y0 + 14], fill=NAVY)
        d.rectangle([x0 + 16, y0 + 6, x0 + 32, y0 + 14], fill=(245, 245, 245))
        d.rectangle([x0 + 32, y0 + 6, x0 + 48, y0 + 14], fill=RED)


def prepare_portrait(src: Image.Image, tw: int = 1080, th: int = 1350) -> Image.Image:
    # Scale to width, then crop extra height from the empty top, keeping capitol + corn.
    scale = tw / src.width
    new = src.resize((tw, int(round(src.height * scale))), Image.Resampling.LANCZOS)
    if new.height >= th:
        top = new.height - th  # drop only top parchment; keep bottom
        new = new.crop((0, top, tw, top + th))
    else:
        canvas = Image.new("RGB", (tw, th), (236, 222, 196))
        canvas.paste(new, (0, th - new.height))
        new = canvas
    # gentle upscale sharpen
    new = new.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    return new


def prepare_landscape(src: Image.Image, tw: int = 1600, th: int = 900) -> Image.Image:
    new = src.resize((tw, th), Image.Resampling.LANCZOS)
    new = new.filter(ImageFilter.UnsharpMask(radius=1.1, percent=55, threshold=2))
    return new


def translucent_panel(base: Image.Image, box, radius: int = 16, alpha: int = 210, outline=True) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle(box, radius=radius, fill=(*PANEL, alpha), outline=(*GOLD, 230) if outline else None, width=2)
    composed = Image.alpha_composite(base.convert("RGBA"), overlay)
    base.paste(composed.convert("RGB"))


def render_portrait() -> Image.Image:
    src = Image.open(REFS / "bg_portrait.jpg").convert("RGB")
    img = prepare_portrait(src)
    w, h = img.size
    # Redraw a clean formal frame over the generated one
    draw_frame(img)
    draw = ImageDraw.Draw(img)
    cx = w / 2
    left, right = 80, w - 80
    max_w = int(right - left)

    y = 50
    y = draw_centered(draw, y, "THE GUARANTEE CLAUSE  ·  IOWA", sc_cormorant("SemiBold", 20), GOLD, cx, tracking=3)
    y += 8

    # Headline, typographically broken but exact words
    y = draw_centered(draw, y, "Did you know?", playfair(700, 44, italic=True), NAVY, cx)
    y += 6

    headline_font = playfair(700, 42)
    # Keep wording exact; typographic apostrophe only
    for line in [
        "It’s NOT your job",
        "to prove our elections",
        "are free and fair.",
    ]:
        y = draw_centered(draw, y, line, headline_font, INK, cx)
        y -= 4
    y += 10
    sub = playfair(600, 30)
    for line in [
        "The Guarantee Clause",
        "puts that on the government.",
    ]:
        y = draw_centered(draw, y, line, sub, NAVY, cx)
        y -= 2

    y += 14
    gold_rule(draw, y, left + 80, right - 80)
    y += 18

    # Constitution quote
    y = draw_centered(draw, y, "ARTICLE IV, SECTION 4", sc_cormorant("Medium", 18), GOLD_SOFT, cx, tracking=3)
    y += 8
    quote_font = garamond(500, 28, italic=True)
    clause_lines = [
        "“The United States shall guarantee",
        "to every State in this Union",
        "a Republican Form of Government.”",
    ]
    y = draw_lines_centered(draw, y, clause_lines, quote_font, INK, cx, leading=36)
    y += 2
    y = draw_centered(draw, y, CLAUSE_CITE, caslon("Italic", 18), GOLD_SOFT, cx)
    y += 14

    gold_rule(draw, y, left + 80, right - 80)
    y += 18

    # EO plaque — sits in the parchment sky above / over the upper building
    # Measure quote first
    eo_label = sc_cormorant("SemiBold", 18)
    eo_font = garamond(500, 22)
    eo_cite_font = caslon("Italic", 16)
    eo_lines = wrap_text(f"“{EO_QUOTE}”", eo_font, max_w - 60)
    ascent, descent = eo_font.getmetrics()
    quote_h = int(len(eo_lines) * (ascent + descent) * 0.95)
    panel_top = int(y)
    panel_bot = panel_top + 36 + quote_h + 44
    # Keep the prairie / lower capitol visible; cap the panel if needed
    panel_bot = min(panel_bot, 980)
    translucent_panel(img, [left - 8, panel_top, right + 8, panel_bot], radius=14, alpha=222)
    draw = ImageDraw.Draw(img)  # refresh after paste

    yy = panel_top + 12
    yy = draw_centered(draw, yy, "EXECUTIVE ORDER 14399", eo_label, NAVY, cx, tracking=3)
    yy += 4
    for line in eo_lines:
        ww = draw.textlength(line, font=eo_font)
        draw.text((cx - ww / 2, yy), line, font=eo_font, fill=INK)
        yy += ascent + descent - 2
    yy += 6
    draw_centered(draw, yy, EO_CITE, eo_cite_font, GOLD_SOFT, cx)
    return img


def render_landscape() -> Image.Image:
    src = Image.open(REFS / "bg_landscape.jpg").convert("RGB")
    img = prepare_landscape(src)
    w, h = img.size
    draw_frame(img, inset=16)
    draw = ImageDraw.Draw(img)

    # Text lives in the left parchment; keep clear of the capitol (~x=820)
    col_left, col_right = 70, 780
    cx = (col_left + col_right) / 2
    max_w = col_right - col_left

    # Soft parchment panel over the left so type stays crisp against any grain
    translucent_panel(img, [52, 36, 800, 755], radius=18, alpha=232, outline=True)
    draw = ImageDraw.Draw(img)

    y = 52
    y = draw_centered(draw, y, "THE GUARANTEE CLAUSE  ·  IOWA", sc_cormorant("SemiBold", 18), GOLD, cx, tracking=3)
    y += 4
    y = draw_centered(draw, y, "Did you know?", playfair(700, 36, italic=True), NAVY, cx)
    y += 2
    hf = playfair(700, 32)
    for line in [
        "It’s NOT your job to prove",
        "our elections are free and fair.",
    ]:
        y = draw_centered(draw, y, line, hf, INK, cx)
        y -= 4
    y += 6
    sf = playfair(600, 24)
    y = draw_centered(draw, y, "The Guarantee Clause puts that on the government.", sf, NAVY, cx)
    y += 10
    gold_rule(draw, y, col_left + 40, col_right - 40)
    y += 14

    y = draw_centered(draw, y, "ARTICLE IV, SECTION 4", sc_cormorant("Medium", 15), GOLD_SOFT, cx, tracking=2)
    y += 4
    qf = garamond(500, 22, italic=True)
    clause_lines = [
        "“The United States shall guarantee",
        "to every State in this Union",
        "a Republican Form of Government.”",
    ]
    y = draw_lines_centered(draw, y, clause_lines, qf, INK, cx, leading=28)
    y = draw_centered(draw, y, CLAUSE_CITE, caslon("Italic", 16), GOLD_SOFT, cx)
    y += 10
    gold_rule(draw, y, col_left + 40, col_right - 40)
    y += 12

    y = draw_centered(draw, y, "EXECUTIVE ORDER 14399", sc_cormorant("SemiBold", 16), NAVY, cx, tracking=2)
    y += 6
    eof = garamond(500, 20)
    eo_lines = [
        "“The Federal Government has an unavoidable duty",
        "under Article II of the Constitution of the United States",
        "to enforce Federal law, which includes preventing violations",
        "of Federal criminal law and maintaining public confidence",
        "in election outcomes.”",
    ]
    y = draw_lines_centered(draw, y, eo_lines, eof, INK, cx, leading=25)
    y += 6
    draw_centered(draw, y, EO_CITE, caslon("Italic", 15), GOLD_SOFT, cx)
    return img


def main() -> None:
    portrait = render_portrait()
    assert portrait.size == (1080, 1350), portrait.size
    ppath = ROOT / "IA_guarantee_clause.png"
    portrait.save(ppath, "PNG", optimize=True)
    print("wrote", ppath, portrait.size, ppath.stat().st_size)

    landscape = render_landscape()
    assert landscape.size == (1600, 900), landscape.size
    lpath = ROOT / "IA_guarantee_clause_xcard.png"
    landscape.save(lpath, "PNG", optimize=True)
    print("wrote", lpath, landscape.size, lpath.stat().st_size)


if __name__ == "__main__":
    main()
