"""Render the Bitcoin white paper text pages (PL translation, EN original) for build.py.

Source: content/whitepaper.json, made by tools/extract_whitepaper.py from the PDFs hosted
on the site. Equations are MathML written here; figures are PNG crops of the PDF pages
(assets/whitepaper/). Wording of the paper is not edited.
"""
import html
import re

e = html.escape

SHA = {"en": "b1674191a88ec5cdd733e4240a81803105dc412d6c6708d53ab94fc248f4f553",
       "pl": "b59471f6edbf101a63b1bd88080c23b072ea0b1c34b4f0d4ba396fc7dc831248"}
PDF = {"en": "/assets/media/files/2023/02/bitcoin.pdf", "pl": "/assets/media/files/2023/02/bitcoin_pl.pdf"}
SIZE = {"en": "180 KB", "pl": "191 KB"}
FIG_SCALE = 1.7  # PNGs are cropped at 2.5x; shown at about 1.5 CSS px per PDF point
FIG_PX = {  # filled by build from the PNG headers
}

FIG_ALT = {
    "pl": {
        "transactions": "Schemat łańcucha transakcji. Każdy właściciel podpisuje swoim kluczem prywatnym hash poprzedniej transakcji razem z kluczem publicznym następnego właściciela. Podpis można zweryfikować kluczem publicznym poprzedniego właściciela.",
        "timestamp": "Łańcuch znaczników czasu. Hash bloku elementów jest ogłaszany, a każdy kolejny blok zawiera hash poprzedniego.",
        "pow": "Dwa bloki połączone w łańcuch. Każdy blok zawiera hash poprzedniego bloku, nonce i transakcje.",
        "merkle": "Po lewej transakcje Tx0 do Tx3 haszowane w drzewie Merkle, z korzeniem w nagłówku bloku. Po prawej to samo drzewo po usunięciu Tx0 do Tx2: zostają tylko hashe potrzebne do Tx3.",
        "spv": "Najdłuższy łańcuch proof-of-work: trzy nagłówki bloków z hashem poprzedniego bloku, nonce i korzeniem Merkle. Gałąź Merkle łączy transakcję Tx3 z korzeniem jednego z bloków.",
        "split": "Transakcja z wieloma wejściami i wyjściami.",
        "privacy": "Dwa modele prywatności. W tradycyjnym tożsamości, transakcje, zaufana strona trzecia i kontrahent są oddzielone od publiki. W nowym publika widzi transakcje, ale bez tożsamości.",
    },
    "en": {
        "transactions": "Diagram of a chain of transactions. Each owner signs with their private key the hash of the previous transaction together with the next owner's public key. The signature is verified with the previous owner's public key.",
        "timestamp": "A chain of timestamps. The hash of a block of items is published, and each block contains the hash of the previous one.",
        "pow": "Two blocks linked in a chain. Each block holds the previous block's hash, a nonce and transactions.",
        "merkle": "On the left, transactions Tx0 to Tx3 hashed in a Merkle tree, with the root in the block header. On the right, the same tree after pruning Tx0 to Tx2: only the hashes needed for Tx3 remain.",
        "spv": "The longest proof-of-work chain: three block headers with the previous hash, nonce and Merkle root. A Merkle branch links transaction Tx3 to the root of one block.",
        "split": "A transaction with several inputs and outputs.",
        "privacy": "Two privacy models. In the traditional one, identities, transactions, a trusted third party and the counterparty are kept apart from the public. In the new one the public sees the transactions, but not the identities.",
    },
}

T = {
    "pl": {"toc": "Spis treści", "refs": "Źródła", "abstract": "Abstrakt.", "if": "if", "sec": "sekcja-",
           "ref_label": "Źródło"},
    "en": {"toc": "Contents", "refs": "References", "abstract": "Abstract.", "if": "if", "sec": "section-",
           "ref_label": "Reference"},
}

# ------------------------------------------------------------------ equations (MathML)

def _frac(a, b):
    return f"<mfrac><mi>{a}</mi><mi>{b}</mi></mfrac>"


QP = f"<mrow><mo>(</mo>{_frac('q', 'p')}<mo>)</mo></mrow>"
QPZK = f"<msup>{QP}<mrow><mi>z</mi><mo>&#8722;</mo><mi>k</mi></mrow></msup>"
POIS = ("<mfrac><mrow><msup><mi>&#955;</mi><mi>k</mi></msup><msup><mi>e</mi><mrow><mo>&#8722;</mo><mi>&#955;</mi></mrow></msup></mrow>"
        "<mrow><mi>k</mi><mo>!</mo></mrow></mfrac>")
EQ = {
    "q": ("q_z = 1 if p ≤ q; (q/p)^z if p > q",
          "<msub><mi>q</mi><mi>z</mi></msub><mo>=</mo><mrow><mo>{</mo><mtable columnalign=\"left left\">"
          "<mtr><mtd><mn>1</mn></mtd><mtd><mtext>if&#160;</mtext><mi>p</mi><mo>&#8804;</mo><mi>q</mi></mtd></mtr>"
          f"<mtr><mtd><msup>{QP}<mi>z</mi></msup></mtd><mtd><mtext>if&#160;</mtext><mi>p</mi><mo>&gt;</mo><mi>q</mi></mtd></mtr>"
          "</mtable></mrow>"),
    "lambda": ("lambda = z q/p",
               f"<mi>&#955;</mi><mo>=</mo><mi>z</mi>{_frac('q', 'p')}"),
    "sum": ("sum for k from 0 to infinity of (lambda^k e^-lambda / k!) times (q/p)^(z-k) if k <= z, 1 if k > z",
            "<munderover><mo>&#8721;</mo><mrow><mi>k</mi><mo>=</mo><mn>0</mn></mrow><mi>&#8734;</mi></munderover>"
            f"{POIS}<mo>&#8901;</mo><mrow><mo>{{</mo><mtable columnalign=\"left left\">"
            f"<mtr><mtd>{QPZK}</mtd><mtd><mtext>if&#160;</mtext><mi>k</mi><mo>&#8804;</mo><mi>z</mi></mtd></mtr>"
            "<mtr><mtd><mn>1</mn></mtd><mtd><mtext>if&#160;</mtext><mi>k</mi><mo>&gt;</mo><mi>z</mi></mtd></mtr>"
            "</mtable></mrow>"),
    "tail": ("1 - sum for k from 0 to z of (lambda^k e^-lambda / k!) times (1 - (q/p)^(z-k))",
             "<mn>1</mn><mo>&#8722;</mo><munderover><mo>&#8721;</mo><mrow><mi>k</mi><mo>=</mo><mn>0</mn></mrow><mi>z</mi></munderover>"
             f"{POIS}<mrow><mo>(</mo><mn>1</mn><mo>&#8722;</mo>{QPZK}<mo>)</mo></mrow>"),
}


def eq_html(eid):
    alt, body = EQ[eid]
    return f'<div class="wp-eq"><math display="block" alttext="{e(alt)}">{body}</math></div>'


# ------------------------------------------------------------------ text

def inline(text):
    s = e(text)
    s = re.sub("\U0001d467(?=[A-Za-z\u0104-\u017c])", "<var>z</var> ", s)
    s = s.replace("\U0001d467", "<var>z</var>")
    s = re.sub(r"\[(\d+)(?:-(\d+))?\]", lambda m: f'<a class="wp-cite" href="#ref-{m.group(1)}">{m.group(0)}</a>', s)
    return s


def url_links(text):
    s = e(text)
    return re.sub(r"(https?://[^\s,]+)", lambda m: f'<a href="{m.group(1)}" rel="noopener">{m.group(1)}</a>', s)


def defs_html(lines):
    out = []
    for ln in lines:
        left, _, right = ln.partition(" = ")
        name = {"p": "<var>p</var>", "q": "<var>q</var>", "qz": "<var>q</var><sub><var>z</var></sub>"}[left.strip()]
        out.append(f"<dt>{name}</dt><dd>{inline(right)}</dd>")
    return '<dl class="wp-defs">' + "".join(out) + "</dl>"


def figure_html(lang, name, b, px):
    w, h = px[name + "-" + lang]
    src = b(f"/assets/whitepaper/{name}-{lang}.png")
    return (f'<figure class="wp-fig"><img src="{src}" width="{round(w / FIG_SCALE)}" height="{round(h / FIG_SCALE)}" '
            f'alt="{e(FIG_ALT[lang][name])}" loading="lazy"></figure>')


def sec_id(lang, n):
    return f"{T[lang]['sec']}{n}"


def toc_html(lang, d):
    items = "".join(f'<a href="#{sec_id(lang, s["n"])}">{s["n"]}. {e(s["title"])}</a>' for s in d["sections"])
    items += f'<a href="#{"zrodla" if lang == "pl" else "references"}">{e(T[lang]["refs"])}</a>'
    return f'<nav class="toc wp-toc" aria-label="{e(T[lang]["toc"])}">{items}</nav>'


def paper_html(lang, d, b, px):
    t = T[lang]
    note = " ".join(d.get("note", []))
    note = e(note).replace("@meeDamian", '<a href="https://github.com/meeDamian/bitcoinwhitepaper">@meeDamian</a>')
    head = (f'<header class="wp-head"><h2 class="wp-title">{e(d["title"])}</h2>'
            f'<p class="wp-author">{e(d["author"])}<br>{e(d["email"])}<br>'
            f'<a href="https://{e(d["site"])}" rel="noopener">{e(d["site"])}</a></p>'
            + (f'<p class="wp-note">{note}</p>' if note else "") + "</header>")
    ab = d["abstract"]
    assert ab.startswith(t["abstract"]), ab[:20]
    out = [head, f'<p class="wp-abstract"><strong>{t["abstract"]}</strong>{inline(ab[len(t["abstract"]):])}</p>']
    for s in d["sections"]:
        out.append(f'<section class="wp-sec" id="{sec_id(lang, s["n"])}"><h3>{s["n"]}. {e(s["title"])}</h3>')
        for blk in s["blocks"]:
            k = blk["type"]
            if k == "p":
                out.append(f"<p>{inline(blk['text'])}</p>")
            elif k == "list":
                out.append("<ol class=\"wp-steps\">" + "".join(
                    f"<li>{inline(re.sub(r'^\d\) ', '', x))}</li>" for x in blk["items"]) + "</ol>")
            elif k == "fig":
                out.append(figure_html(lang, blk["id"], b, px))
            elif k == "eq":
                out.append(eq_html(blk["id"]))
            elif k == "defs":
                out.append(defs_html(blk["lines"]))
            elif k == "pre":
                out.append(f'<pre class="wp-pre"><code>{e(blk["text"])}</code></pre>')
        out.append("</section>")
    rid = "zrodla" if lang == "pl" else "references"
    refs = []
    for r in d["references"]:
        m = re.match(r"^\[(\d+)\]\s*(.*)$", r)
        refs.append(f'<li id="ref-{m.group(1)}"><span class="wp-ref-n">[{m.group(1)}]</span> {url_links(m.group(2))}</li>')
    out.append(f'<section class="wp-sec" id="{rid}"><h3>{e(t["refs"])}</h3><ol class="wp-refs">{"".join(refs)}</ol></section>')
    return f'<div class="wp-paper" lang="{lang}">' + "".join(out) + "</div>"


def footer_html(lang, b, home):
    """Short bar: thanks to the author, shared mission, original PDF, unmodified note, quiet link home."""
    if lang == "pl":
        thanks = "Dziękujemy Satoshiemu Nakamoto za Bitcoina i za dziewięć stron, które go opisały."
        mission = "Wspólna sprawa: pieniądz bez pośredników, otwarty dla każdego."
        labels = {"en": "Oryginał (angielski)", "pl": "Tłumaczenie meeDamian"}
        unmod, order = "bez zmian, SHA-256", ("en", "pl")
    else:
        thanks = "Thank you, Satoshi Nakamoto, for Bitcoin and for the nine pages that described it."
        mission = "A shared cause: money without intermediaries, open to everyone."
        labels = {"en": "Original PDF"}
        unmod, order = "unmodified, SHA-256", ("en",)
    files = " · ".join(
        f'<a href="{b(PDF[k])}">{labels[k]}, PDF&nbsp;{SIZE[k].replace(" ", "&nbsp;")}</a> ({unmod} <code title="{SHA[k]}">{SHA[k][:8]}</code>)'
        for k in order)
    return (f'<aside class="wp-foot"><p class="wp-foot__thanks">{e(thanks)}</p><p>{e(mission)}</p>'
            f'<p>{files}</p><p class="wp-foot__home"><a href="{home}">Dwadzieścia Jeden</a></p></aside>')
