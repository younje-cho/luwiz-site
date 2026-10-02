# -*- coding: utf-8 -*-
"""옵시디언 원고 → 홈페이지 블로그 (`blog/`).

    py build.py

원고 한 벌만 둔다 - 옵시디언에 쓰고 여기서 뽑는다. 빌드 도구도 의존성도 없다.
`slug` 에 없는 파일은 안 뽑는다(초안이 홈페이지에 새지 않게).

네이버에 붙여 넣을 판은 다른 곳에서 만든다 - 거기는 서식이 살아야 해서 모양이 다르다.
"""
import html
import io
import os
import re

SRC = "C:/Users/Lenovo/Documents/Obsidian/Younje/1. Project/루위즈/마케팅/글/"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "blog")
SITE = "https://luwiz.co.kr"

#: 파일 이름 → 주소. 새 글을 내려면 여기에 한 줄 더한다.
SLUG = {
    "01 재무는 침묵의 장기이자 근력이다": "finance-is-silent",
    "02 연결회계, 이론보다 작성이 어렵다": "consolidation-is-hard",
    "03 미래는 과거에서 출발한다": "future-starts-from-past",
    "04 AI는 정리된 숫자에서 시작한다": "ai-starts-from-clean-numbers",
}

GA = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-KMZVP6S2VE"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-KMZVP6S2VE');
</script>"""

CSS = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="/style.css">"""

TOP = """<div class="top"><a class="brand" href="/"><img src="/logo.png" alt="루위즈"><span>주식회사 루위즈</span></a><nav><span class="menu"><a href="/product/">제품</a><span class="sub"><a href="/product/consolidation.html">연결재무제표</a><a href="/product/cash-flow-statement.html">현금흐름표</a><a href="/product/management-accounting.html">관리회계</a><a href="/product/daily-cash-report.html">자금일보</a></span></span><a href="/blog/">글</a><a class="btn" href="mailto:contact@luwiz.co.kr">문의</a></nav></div>"""
FOOTER = """<hr>
  <footer><strong>주식회사 루위즈</strong><br>사업자등록번호 333-87-04299<br><a href="/notice/">공고</a></footer>"""


def inline(t):
    t = html.escape(t)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def body_of(md):
    """앞머리와 첫 제목은 떼고 본문만 돌려준다 - 제목은 따로 그린다."""
    md = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    out, lines, i = [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            out.append("<pre>" + "\n".join(buf) + "</pre>")
        elif ln.startswith("#"):
            n = len(ln) - len(ln.lstrip("#"))
            if not out and n == 1:          # 글 제목은 건너뛴다
                i += 1
                continue
            lv = 2 if n <= 2 else 3
            out.append(f"<h{lv}>{inline(ln[n:].strip())}</h{lv}>")
        elif ln.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append("<p>" + inline(lines[i][2:]) + "</p>")
                i += 1
            i -= 1
            out.append("<blockquote>" + "".join(buf) + "</blockquote>")
        elif ln.startswith("!["):                      # ![설명](주소) - 그래프
            m = re.match(r"!\[(.*?)\]\((.+?)\)", ln)
            out.append(f'<figure><img src="{m.group(2)}" alt="{inline(m.group(1))}">'
                       f'<figcaption>{inline(m.group(1))}</figcaption></figure>')
        elif ln.startswith("|") and ln.rstrip().endswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            i -= 1
            tag, buf = "th", []
            for r in rows:
                buf.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in r) + "</tr>")
                tag = "td"
            out.append("<table>" + "".join(buf) + "</table>")
        elif ln.startswith("* ") or ln.startswith("- "):
            buf = []
            while i < len(lines) and (lines[i].startswith("* ") or lines[i].startswith("- ")):
                buf.append("<li>" + inline(lines[i][2:]) + "</li>")
                i += 1
            i -= 1
            out.append("<ul>" + "".join(buf) + "</ul>")
        elif ln.strip():
            out.append("<p>" + inline(ln) + "</p>")
        i += 1
    return "\n".join(out)


def first_para(md):
    """미리보기 문장 - og:description 에 쓴다."""
    for ln in re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S).split("\n"):
        if ln.strip() and not ln.startswith("#"):
            return re.sub(r"\*\*", "", ln.strip())[:150]
    return ""


def main():
    os.makedirs(OUT, exist_ok=True)
    posts = []
    for name, slug in SLUG.items():
        p = SRC + name + ".md"
        md = io.open(p, encoding="utf-8").read()
        title = re.search(r"^# (.+)$", md, flags=re.M).group(1).strip()
        # **발행일이 있으면 그것을 쓴다** - 독자는 이 날짜를 발행일로 읽는다.
        # 앞머리에 `발행: 2026-09-29` 를 적는다. 없으면 쓴 날로 떨어진다.
        m = re.search(r"^발행:\s*(\S+)", md, flags=re.M) or re.search(r"^쓴 날:\s*(\S+)", md, flags=re.M)
        date = m.group(1) if m else ""
        desc = first_para(md)
        doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
{GA}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)} — 루위즈</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article">
<link rel="canonical" href="{SITE}/blog/{slug}.html">
<link rel="icon" href="/logo.png">
{CSS}
</head>
<body>
<div class="wrap">
  {TOP}
  <article>
    <h1>{html.escape(title)}</h1>
    <p class="date">{date}</p>
{body_of(md)}
  </article>
  <hr>
  <p class="foot">루위즈 — 연결결산 · FP&amp;A 도구를 만듭니다.
     <a href="/">luwiz.co.kr</a> · <a href="mailto:contact@luwiz.co.kr">contact@luwiz.co.kr</a></p>
  <p class="foot"><a href="/blog/">다른 글 보기 →</a></p>
  {FOOTER}
</div>
</body>
</html>
"""
        io.open(os.path.join(OUT, slug + ".html"), "w", encoding="utf-8", newline="\n").write(doc)
        posts.append((title, slug, date))

    items = "\n".join(
        f'      <li><a href="/blog/{s}.html">{html.escape(t)}<span class="d">{d}</span></a></li>'
        for t, s, d in reversed(posts))
    idx = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
{GA}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>글 — 주식회사 루위즈</title>
<meta name="description" content="연결결산 · 월 마감 · FP&amp;A에 대해 쓴 글입니다.">
<meta property="og:title" content="글 — 주식회사 루위즈">
<meta property="og:description" content="연결결산 · 월 마감 · FP&amp;A에 대해 쓴 글입니다.">
<link rel="canonical" href="{SITE}/blog/">
<link rel="icon" href="/logo.png">
{CSS}
</head>
<body>
<div class="wrap">
  {TOP}
  <div class="list">
    <h1>글</h1>
    <ol>
{items}
    </ol>
  </div>
  {FOOTER}
</div>
</body>
</html>
"""
    io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n").write(idx)
    print(f"ok  글 {len(posts)}장 + 목록")
    for t, s, d in posts:
        print(f"    /blog/{s}.html   {t}")
    sitemap()

def sitemap():
    """저장소의 .html 을 훑어 sitemap.xml · robots.txt 를 쓴다.
    손으로 만든 제품 페이지도 같이 들어가므로, 목록을 적는 것보다 파일을 훑는 쪽이 안 빠뜨린다."""
    import datetime
    rows = []
    for root, _dirs, files in os.walk(HERE):
        if os.sep + "." in root:
            continue
        for f in sorted(files):
            if not f.endswith(".html"):
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, HERE).replace(os.sep, "/")
            url = SITE + "/" + rel
            if rel.endswith("index.html"):                 # 목록은 폴더 주소로
                url = SITE + "/" + rel[:-len("index.html")]
            mod = datetime.date.fromtimestamp(os.path.getmtime(full)).isoformat()
            pri = "1.0" if rel == "index.html" else ("0.8" if rel.endswith("index.html") else "0.6")
            rows.append((url, mod, pri))
    line = '  <url><loc>{}</loc><lastmod>{}</lastmod><priority>{}</priority></url>'
    body = "\n".join(line.format(u, m, p) for u, m, p in sorted(rows))
    io.open(os.path.join(HERE, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n")
    io.open(os.path.join(HERE, "robots.txt"), "w", encoding="utf-8", newline="\n").write(
        "User-agent: *\nAllow: /\n\nSitemap: " + SITE + "/sitemap.xml\n")
    print("    sitemap.xml  주소 %d개 · robots.txt" % len(rows))


if __name__ == "__main__":
    main()

