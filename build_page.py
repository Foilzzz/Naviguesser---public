#!/usr/bin/env python3
"""build_page.py — generate public/index.html from public/T2_LIVE_PRECOMMITMENT.md.

Generated, never transcribed: the page is a pure function of the source
document. The source's sha256 is embedded in the page footer, and --check
verifies the committed page is byte-identical to a fresh render.

Usage:
    python build_page.py            # write public/index.html
    python build_page.py --check    # exit 1 if index.html != fresh render

No third-party dependencies. The renderer handles exactly the Markdown
subset the source document uses (headings, paragraphs, bold, italic,
links, lists, blockquote, horizontal rule) and escapes everything else.
"""
import hashlib
import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T2_LIVE_PRECOMMITMENT.md"
OUTPUT = HERE / "index.html"

CSS = """
:root { color-scheme: dark; }
* { box-sizing: border-box; }
body { margin: 0; background: #0b0f14; color: #d7dee6;
       font: 17px/1.65 Georgia, 'Times New Roman', serif; }
main { max-width: 760px; margin: 0 auto; padding: 48px 22px 96px; }
h1 { font-size: 1.9rem; line-height: 1.25; color: #f2f5f8; margin: 0 0 .4em; }
h2 { font-size: 1.25rem; color: #8fd0ff; margin: 2.2em 0 .6em;
     font-family: ui-monospace, 'Cascadia Mono', Consolas, monospace;
     letter-spacing: .02em; }
p { margin: 1em 0; }
a { color: #8fd0ff; }
strong { color: #f2f5f8; }
ul { padding-left: 1.4em; }
li { margin: .4em 0; }
blockquote { border-left: 3px solid #2b3d4d; margin: 1.4em 0;
             padding: .2em 1.2em; color: #aebac6; }
hr { border: none; border-top: 1px solid #22303d; margin: 2.6em 0; }
code { font-family: ui-monospace, 'Cascadia Mono', Consolas, monospace;
       font-size: .88em; background: #131b23; padding: .12em .35em;
       border-radius: 4px; word-break: break-all; }
.meta { font-family: ui-monospace, 'Cascadia Mono', Consolas, monospace;
        font-size: .78rem; color: #6f8191; margin-top: 3.2em;
        border-top: 1px solid #22303d; padding-top: 1.2em; }
.meta div { margin: .3em 0; }
.meta .k { color: #42566a; display: inline-block; min-width: 11em; }
.badge { display: inline-block; font-family: ui-monospace, monospace;
         font-size: .72rem; letter-spacing: .12em; color: #ffd27a;
         border: 1px solid #5c4a20; border-radius: 3px;
         padding: .25em .7em; margin-bottom: 1.6em; }
"""

PIN_RE = re.compile(r"sha256:\s*`([0-9a-f]{16,64})`")


def render_inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                  r'<a href="\2" rel="noopener">\1</a>', text)
    return text


def render_markdown(md: str) -> str:
    out, para, listbuf = [], [], []
    in_bq = False

    def flush_para():
        if para:
            out.append("<p>" + render_inline(" ".join(para)) + "</p>")
            para.clear()

    def flush_list():
        if listbuf:
            out.append("<ul>" + "".join(f"<li>{render_inline(x)}</li>"
                                       for x in listbuf) + "</ul>")
            listbuf.clear()

    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("> "):
            flush_para(); flush_list()
            out.append("<blockquote><p>" + render_inline(line[2:]) + "</p></blockquote>")
            continue
        if line.startswith("#"):
            flush_para(); flush_list()
            level = len(line) - len(line.lstrip("#"))
            text = line[level:].strip()
            out.append(f"<h{level}>{render_inline(text)}</h{level}>")
            continue
        if line.strip() in ("---", "***"):
            flush_para(); flush_list()
            out.append("<hr>")
            continue
        if line.startswith("- "):
            flush_para()
            listbuf.append(line[2:])
            continue
        if not line.strip():
            flush_para(); flush_list()
            continue
        para.append(line.strip())
    flush_para(); flush_list()
    return "\n".join(out)


def build() -> bytes:
    src_bytes = SOURCE.read_bytes()
    digest = hashlib.sha256(src_bytes).hexdigest()
    md = src_bytes.decode("utf-8")
    pins = PIN_RE.findall(md)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    body = render_markdown(md)
    pin_items = "\n".join(
        f'<div><span class="k">pinned document</span>'
        f'<code>{p[:16]}&hellip;{p[-5:]}</code></div>'
        for p in pins
    )
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Naviguesser — public pre-commitment: the live fleet-drift verdict</title>
<meta name="description" content="We are committing, publicly and in advance, to a result we have not seen.">
<style>{CSS}</style>
</head>
<body>
<main>
<div class="badge">PRE-REGISTERED &middot; BLIND &middot; IN PROGRESS</div>
{body}
<div class="meta">
<div><span class="k">this page is</span>generated from the source document, never hand-edited</div>
<div><span class="k">source</span>public/T2_LIVE_PRECOMMITMENT.md</div>
<div><span class="k">source sha256</span><code>{digest[:16]}&hellip;{digest[-5:]}</code></div>
{pin_items}
<div><span class="k">statistic amendment</span>slot open — pinned here by 4 September 2026, before window 1 opens</div>
<div><span class="k">page generated</span>{generated}</div>
</div>
</main>
</body>
</html>
"""
    return page.encode("utf-8")


def main() -> int:
    page = build()
    if "--check" in sys.argv:
        if not OUTPUT.exists():
            print("CHECK FAIL: public/index.html does not exist")
            return 1
        current = OUTPUT.read_bytes()
        if current != page:
            print("CHECK FAIL: public/index.html is stale — regenerate with build_page.py")
            return 1
        print("CHECK OK: public/index.html is a current render of the source")
        return 0
    OUTPUT.write_bytes(page)
    print(f"wrote {OUTPUT} ({len(page)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
