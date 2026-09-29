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
    # 04 는 다음 주에 낸다 - 낼 때 이 줄의 # 를 뗀다
    # "04 AI는 정리된 숫자에서 시작한다": "ai-starts-from-clean-numbers",
}

GA = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-KMZVP6S2VE"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-KMZVP6S2VE');
</script>"""

CSS = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>
  :root{--navy:#193248;--gold:#AC8540;--ink:#1c2b3a;--muted:#5f6f7e;--line:#e3e1d9;--bg:#faf9f5;--card:#fff}
  *{margin:0;padding:0;box-sizing:border-box}
  html{-webkit-text-size-adjust:100%}
  body{font-family:Pretendard,-apple-system,BlinkMacSystemFont,"Segoe UI","Malgun Gothic",sans-serif;
       background:var(--bg);color:var(--ink);line-height:1.85;letter-spacing:-.01em}
  .wrap{max-width:720px;margin:0 auto;padding:0 24px}
  .top{display:flex;align-items:center;gap:10px;padding:28px 0 0}
  .top a{display:flex;align-items:center;gap:10px;text-decoration:none}
  .top img{height:30px;width:auto}
  .top span{font-size:14px;font-weight:600;color:var(--navy);letter-spacing:.02em}
  article{padding:48px 0 8px}
  article h1{font-size:30px;line-height:1.4;font-weight:700;color:var(--navy);letter-spacing:-.02em}
  .date{margin-top:12px;font-size:13.5px;color:var(--muted)}
  article h2{font-size:20px;font-weight:700;color:var(--navy);margin:44px 0 14px;letter-spacing:-.02em}
  article h3{font-size:17px;font-weight:700;color:var(--navy);margin:32px 0 10px}
  article p{margin:0 0 18px;font-size:16.5px}
  article b{font-weight:600;color:var(--navy)}
  article ul{margin:0 0 18px;padding-left:20px}
  article li{margin:8px 0;font-size:16.5px}
  blockquote{border-left:3px solid var(--gold);margin:20px 0;padding:6px 0 6px 18px;color:var(--muted)}
  blockquote p{margin:0 0 6px;font-size:16px}
  pre{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;
      font-family:ui-monospace,Menlo,Consolas,monospace;font-size:14px;line-height:1.9;
      white-space:pre-wrap;margin:0 0 18px;overflow-x:auto}
  table{border-collapse:collapse;width:100%;margin:0 0 18px;font-size:15.5px;background:var(--card)}
  th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
  th{background:#f2f1ea;font-weight:600;color:var(--navy)}
  hr{border:0;border-top:1px solid var(--line);margin:0}
  .foot{padding:28px 0 8px;font-size:15.5px;color:var(--muted)}
  .foot a{color:var(--navy);font-weight:600;text-decoration:none}
  .foot a:hover{color:var(--gold)}
  .list{padding:40px 0}
  .list h1{font-size:26px;font-weight:700;color:var(--navy);margin-bottom:24px}
  .list ol{list-style:none}
  .list li{border-bottom:1px solid var(--line);padding:18px 0}
  .list a{display:block;text-decoration:none;color:var(--navy);font-size:18px;font-weight:600}
  .list a:hover{color:var(--gold)}
  .list .d{display:block;margin-top:4px;font-size:13.5px;color:var(--muted);font-weight:400}
  footer{padding:30px 0 52px;font-size:13.5px;color:var(--muted);line-height:2}
  footer strong{color:var(--ink);font-weight:600}
  @media (max-width:560px){article h1{font-size:24px}article p,article li{font-size:16px}}
</style>"""

TOP = """<div class="top"><a href="/"><img src="/logo.png" alt="루위즈"><span>주식회사 루위즈</span></a></div>"""
FOOTER = """<hr>
  <footer><strong>주식회사 루위즈</strong><br>사업자등록번호 333-87-04299</footer>"""


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
        date = (re.search(r"^쓴 날:\s*(\S+)", md, flags=re.M) or [None, ""])[1]
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


if __name__ == "__main__":
    main()
