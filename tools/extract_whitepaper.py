"""Extract the Bitcoin white paper (EN original, PL translation by meeDamian) from the
PDFs hosted on the site into content/whitepaper.json, the source of the text pages.

The PDFs are the source of truth and are never modified. Run once, commit the JSON:

    C:/Python314/python.exe tools/extract_whitepaper.py

Figures are cropped from the PDF pages (assets/whitepaper/*.png). Equations are written
by hand as MathML in build.py (the PDF holds only positioned glyphs). Everything else is
the paper's own wording; only extraction artefacts are fixed (line joins, double spaces).
"""
import json
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
PDFS = {"en": ROOT / "assets/media/files/2023/02/bitcoin.pdf",
        "pl": ROOT / "assets/media/files/2023/02/bitcoin_pl.pdf"}
FIG_NAMES = ["transactions", "timestamp", "pow", "merkle", "spv", "split", "privacy"]

# Figure boxes (PDF points) found from the vector drawings; order = FIG_NAMES.
FIGS = {
    "en": [(2, (195, 161, 434, 312)), (2, (207, 593, 405, 650)), (3, (211, 231, 424, 283)),
           (4, (158, 446, 454, 608)), (5, (124, 188, 476, 344)), (5, (273, 555, 334, 621)),
           (6, (158, 200, 458, 289))],
    "pl": [(2, (197, 210, 437, 360)), (3, (146, 108, 464, 166)), (3, (188, 361, 424, 431)),
           (5, (157, 97, 453, 259)), (5, (124, 478, 477, 634)), (6, (273, 256, 334, 322)),
           (6, (157, 515, 457, 604))],
}
# Zones of non-prose content: (page, y0, y1, kind, id). Lines inside are not prose.
ZONES = {
    "pl": [(7, 288, 322, "defs", "defs"), (7, 336, 362, "eq", "q"), (7, 636, 660, "eq", "lambda"),
           (8, 130, 170, "eq", "sum"), (8, 195, 232, "eq", "tail"), (8, 266, 410, "pre", "code"),
           (8, 458, 565, "pre", "t1"), (8, 575, 682, "pre", "t2"), (9, 116, 196, "pre", "t3")],
    "en": [(6, 568, 598, "defs", "defs"), (6, 615, 640, "eq", "q"), (7, 288, 312, "eq", "lambda"),
           (7, 360, 392, "eq", "sum"), (7, 424, 456, "eq", "tail"), (7, 490, 635, "pre", "code"),
           (8, 100, 209, "pre", "t1"), (8, 220, 328, "pre", "t2"), (8, 362, 445, "pre", "t3")],
}


def lines_of(doc, lang):
    figs = {}
    for pg, box in FIGS[lang]:
        figs.setdefault(pg, []).append(pymupdf.Rect(box) + (-3, -3, 3, 3))
    out = []
    for pi, page in enumerate(doc):
        for b in page.get_text("dict")["blocks"]:
            for ln in b.get("lines", []):
                r = pymupdf.Rect(ln["bbox"])
                t = "".join(s["text"] for s in ln["spans"])
                if any(rc.intersects(r) and r.width < 230 for rc in figs.get(pi + 1, [])):
                    continue
                if re.fullmatch(r"\d{1,2}", t.strip()) and r.y0 > 690:
                    continue  # page number
                out.append(dict(page=pi + 1, x0=r.x0, y0=r.y0, t=t))
    out.sort(key=lambda d: (d["page"], d["y0"], d["x0"]))
    return out


def clean(s):
    s = s.replace("\u00a0", " ")
    return re.sub(r"\s+", " ", s).strip()


def join(parts):
    """Join wrapped lines. A trailing hyphen is kept (compounds); reviewed below."""
    text = ""
    for p in parts:
        p = clean(p)
        if not text:
            text = p
        elif text.endswith("-"):
            text += p
        else:
            text += " " + p
    return text


def build(lang):
    doc = pymupdf.open(PDFS[lang])
    lines = lines_of(doc, lang)
    zones = ZONES[lang]
    figs = [(pg, box[1], name) for (pg, box), name in zip(FIGS[lang], FIG_NAMES)]

    def zone_of(l):
        for z in zones:
            if z[0] == l["page"] and z[1] <= l["y0"] <= z[2]:
                return z
        return None

    # Merge lone "N." / "N)" / "[N]" labels with the next line at the same height.
    merged = []
    i = 0
    while i < len(lines):
        l = lines[i]
        if re.fullmatch(r"(\d{1,2}\.|\d\)|\[\d+\])", l["t"].strip()) and i + 1 < len(lines) \
                and abs(lines[i + 1]["y0"] - l["y0"]) < 3 and lines[i + 1]["page"] == l["page"]:
            n = lines[i + 1]
            merged.append(dict(page=l["page"], x0=l["x0"], y0=l["y0"], t=l["t"].strip() + " " + n["t"],
                               label=l["t"].strip()))
            i += 2
        else:
            merged.append(l)
            i += 1
    lines = merged

    meta, abstract = {}, []
    sections, refs = [], []
    cur = None          # current section
    para = None         # [first_x0, [lines]]
    lst = None          # list items
    mode = "body"
    zone_buf = {}
    pending_figs = []
    next_n = 1
    events = [("line", l["page"], l["y0"], l) for l in lines] + \
             [("fig", pg, y, name) for pg, y, name in figs]
    events.sort(key=lambda e: (e[1], e[2], 0 if e[0] == "line" else 1))

    def flush():
        nonlocal para, lst
        if para and cur is not None:
            cur["blocks"].append({"type": "p", "text": join(para)})
        para = None
        if lst and cur is not None:
            cur["blocks"].append({"type": "list", "items": [join(x) for x in lst]})
        lst = None

    def emit_figs():
        nonlocal pending_figs
        for name in pending_figs:
            cur["blocks"].append({"type": "fig", "id": name})
        pending_figs = []

    def flush_zone(key):
        z, buf = key
        if cur is None:
            return
        flush()
        emit_figs()
        if z[3] == "pre":
            cur["blocks"].append({"type": "pre", "id": z[4], "text": "\n".join(buf)})
        else:
            cur["blocks"].append({"type": z[3], "id": z[4], "lines": [clean(x) for x in buf]})

    open_zone = None
    force_new = False
    for kind, pg, y, item in events:
        if kind == "fig":
            pending_figs.append(item)
            force_new = True
            continue
        l = item
        z = zone_of(l)
        if open_zone and (z is None or z != open_zone[0]):
            flush_zone(open_zone)
            open_zone = None
        if z:
            if not open_zone:
                open_zone = (z, [])
            open_zone[1].append(l["t"].rstrip())
            continue
        t = clean(l["t"])
        if not t:
            continue
        if pg == 1 and cur is None:
            if not meta.get("title"):
                meta["title"] = t
            elif t.startswith("Satoshi"):
                meta["author"] = t
            elif "@" in t and "." in t and " " not in t:
                meta["email"] = t
            elif t.startswith("www."):
                meta["site"] = t
            elif l["x0"] > 130 and l["x0"] < 150 and l["y0"] > 200:
                abstract.append(t)
            elif not re.match(r"^1\. ", t):
                meta.setdefault("note", []).append(t)
            if not re.match(r"^1\. ", t):
                continue
        m = re.match(r"^(\d{1,2})\. ?(.*)$", t)
        if m and int(m.group(1)) == next_n and l["x0"] < 112 and len(t) < 60 and mode == "body":
            flush()
            emit_figs() if cur else None
            cur = {"n": next_n, "title": m.group(2), "blocks": []}
            sections.append(cur)
            next_n += 1
            continue
        if t in ("Źródła", "References") and l["x0"] < 112:
            flush()
            emit_figs()
            mode = "refs"
            continue
        if mode == "refs":
            if re.match(r"^\[\d+\]", t):
                refs.append([t])
            else:
                refs[-1].append(t)
            continue
        # body prose
        if re.match(r"^\d\) ", t):
            if para:
                flush()
            if lst is None:
                emit_figs()
            lst = (lst or []) + [[t]]
            continue
        if lst is not None and l["x0"] > 130:
            lst[-1].append(t)
            continue
        indented = 118 < l["x0"] < 126
        if lst is not None:
            flush()
        if para is None or indented or force_new:
            flush()
            emit_figs()
            force_new = False
            para = [t]
        else:
            para.append(t)
    if open_zone:
        flush_zone(open_zone)
    flush()
    emit_figs()
    for sec in sections:
        pass
    return dict(lang=lang, **meta, abstract=join(abstract), sections=sections,
                references=[join(r) for r in refs])


def export_figures():
    out = ROOT / "assets/whitepaper"
    out.mkdir(exist_ok=True)
    for lang in ("pl", "en"):
        doc = pymupdf.open(PDFS[lang])
        for (pg, box), name in zip(FIGS[lang], FIG_NAMES):
            clip = pymupdf.Rect(box) + (-6, -6, 6, 6)
            doc[pg - 1].get_pixmap(matrix=pymupdf.Matrix(2.5, 2.5), clip=clip).save(out / f"{name}-{lang}.png")


def main():
    export_figures()
    data = {lang: build(lang) for lang in ("pl", "en")}
    out = ROOT / "content/whitepaper.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    for lang, d in data.items():
        print(lang, len(d["sections"]), "sections", sum(len(s["blocks"]) for s in d["sections"]), "blocks",
              len(d["references"]), "refs")


if __name__ == "__main__":
    sys.exit(main())
