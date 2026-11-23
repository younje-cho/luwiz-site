# -*- coding: utf-8 -*-
"""옵시디언 원고 → 홈페이지 블로그 (`blog/`).

    py build.py

원고 한 벌만 둔다 - 옵시디언에 쓰고 여기서 뽑는다. 빌드 도구도 의존성도 없다.
`slug` 에 없는 파일은 안 뽑는다(초안이 홈페이지에 새지 않게).

네이버에 붙여 넣을 판은 다른 곳에서 만든다 - 거기는 서식이 살아야 해서 모양이 다르다.
"""
import html
import io
import json
import os
import re
import shutil

SRC = "C:/Users/Lenovo/Documents/Obsidian/Younje/1. Project/루위즈/마케팅/글/"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "blog")
SITE = "https://luwiz.co.kr"

#: 파일 이름 → 주소. 새 글을 내려면 여기에 한 줄 더한다.
SLUG = {
    "01 재무는 침묵의 장기이자 근력이다": "finance-is-silent",
    "02 연결회계, 이론보다 작성이 어렵다": "consolidation-is-hard",
    "03 사업계획 세우기 전에 봐야 할 과거 숫자 세 가지": "future-starts-from-past",
    "04 AI는 정리된 숫자에서 시작한다": "ai-starts-from-clean-numbers",
    "05 연결재무제표는 누가 만들어야 하나": "who-makes-consolidated-statements",
    "06 현금흐름표는 왜 따로 있나": "why-cash-flow-statement",
    "07 현금흐름표, 직접법과 간접법": "direct-vs-indirect-cash-flow",
    "08 현금흐름표 간접법, 어디서 안 맞나": "where-indirect-cash-flow-breaks",
    "09 우리 퍼널은 어디서 새고 있나": "where-is-the-funnel-leaking",
    "10 퍼널에서 어디부터 고쳐야 하나": "where-to-fix-the-funnel-first",
    "11 퍼널을 갈라 보면 보이는 것": "split-the-funnel",
    "12 환불율이 오르는 걸 늦게 아는 이유": "refund-rate-by-cohort",
    "13 마케팅 지표는 이익 하나로 이어진다": "marketing-metrics-map",
    "14 객단가가 오른 달에 남는 돈은 줄었다": "higher-aov-less-profit",
    "15 많이 팔린 상품이 많이 남긴 상품은 아니다": "best-seller-not-best-earner",
    "16 환불을 빼고 보면 광고 순위가 바뀐다": "refunds-change-ad-ranking",
    "17 고객 한 명을 데려오는 데 얼마까지 써도 되나": "how-much-to-spend-per-customer",
    "18 광고비 없이 돌아오는 고객은 매출의 몇 할인가": "repeat-customers-share",
    "19 결제 수수료는 왜 조용히 오르나": "why-payment-fees-creep-up",
    "20 숫자를 보고 무엇을 바꿀 수 있나": "what-to-change-from-numbers",
    "21 EBITDA가 좋아 보일 때 의심할 자리": "when-ebitda-looks-too-good",
    "22 EBITDA와 영업현금흐름은 왜 벌어지나": "ebitda-vs-operating-cash-flow",
    "23 친구에게 빌려준 1만원은 어디에 적을까": "double-entry-bookkeeping-basics",
}

# 글 목록의 갈래 - 네이버 블로그 카테고리와 같은 이름 · 같은 차례
CATS = ["회계 이야기", "숫자로 보는 사업"]

GA = """<script async src="https://www.googletagmanager.com/gtag/js?id=G-KMZVP6S2VE"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  // 대표님 기기는 안 센다(2026-10-08) - 주소 끝 ?me=1 로 한 번 열면 그 브라우저는 꺼지고, ?me=0 이면 다시 켜진다
  try { var q = location.search; if (q.indexOf('me=1') >= 0) localStorage.setItem('luwiz_me', '1'); if (q.indexOf('me=0') >= 0) localStorage.removeItem('luwiz_me'); if (localStorage.getItem('luwiz_me')) window['ga-disable-G-KMZVP6S2VE'] = true; } catch (e) {}
  gtag('js', new Date());
  gtag('config', 'G-KMZVP6S2VE');
</script>"""

CSS = """<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="/style.css">
<script src="/inquiry.js" defer></script>"""

TOP = """<div class="top"><a class="brand" href="/"><img src="/logo.png" alt="주식회사 루위즈 로고"><span>주식회사 루위즈</span></a><nav><span class="menu"><a href="/product/">제품</a><span class="sub"><a href="/product/#flow">이어지는 흐름</a><a href="/product/#close">결산</a><a href="/product/#consol">연결</a><a href="/product/#tax">세금</a><a href="/product/#fpa">관리회계</a><a href="/product/#cash">자금</a><a href="/product/#contract">계약</a><a href="/product/#hr">인사</a><a href="/product/#ir">IR</a><a href="/product/#ai">AI</a></span></span><span class="menu"><a href="/#doors">솔루션</a><span class="sub"><a href="/solution/self-bookkeeping.html">자체 기장</a><a href="/solution/consolidation-build.html">연결재무제표 구축</a></span></span><a href="/blog/">글</a><a class="btn" href="mailto:contact@luwiz.co.kr">문의하기</a></nav></div>"""
FOOTER = """<hr>
  <footer><strong>주식회사 루위즈</strong><br>사업자등록번호 333-87-04299<br><a href="/about/">회사 소개</a><br><a href="/notice/">공고</a><br><a href="/privacy/">개인정보 처리방침</a></footer>"""


def inline(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    # [글 제목](https://luwiz.co.kr/blog/…) - 앞 글 링크는 사이트 안 주소로(2026-11-14 글 20)
    return re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                  lambda m: f'<a href="{m.group(2).replace(SITE, "")}">{m.group(1)}</a>', t)


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
            src = m.group(2)
            if not src.startswith(("/", "http")):      # 원고는 옵시디언 상대 경로
                src = "/blog/img/" + os.path.basename(src)
            out.append(f'<figure><img src="{src}" alt="{inline(m.group(1))}">'
                       f'<figcaption>{inline(m.group(1))}</figcaption></figure>')
        elif ln.startswith("|") and ln.rstrip().endswith("|"):
            rows, right = [], set()
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    right = {k for k, c in enumerate(cells) if c.endswith(":")}   # `---:` 는 오른쪽 맞춤(숫자 열)
                else:
                    rows.append(cells)
                i += 1
            i -= 1
            tag, buf = "th", []
            for r in rows:
                buf.append("<tr>" + "".join(f'<{tag}{" style=\"text-align:right\"" if k in right else ""}>{inline(c)}</{tag}>'
                                            for k, c in enumerate(r)) + "</tr>")
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
    pics = os.path.join(SRC, "img")           # 그림은 원고 옆이 원본이다
    if os.path.isdir(pics):
        os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
        for f in os.listdir(pics):
            shutil.copy2(os.path.join(pics, f), os.path.join(OUT, "img", f))
    posts = []
    for name, slug in SLUG.items():
        p = SRC + name + ".md"
        if not os.path.exists(p):              # 발행한 원고는 과거/ 로 옮겨 둔다
            p = SRC + "과거/" + name + ".md"
        md = io.open(p, encoding="utf-8").read()
        title = re.search(r"^# (.+)$", md, flags=re.M).group(1).strip()
        # **발행일이 있으면 그것을 쓴다** - 독자는 이 날짜를 발행일로 읽는다.
        # 앞머리에 `발행: 2026-09-29` 를 적는다. 없으면 쓴 날로 떨어진다.
        m = re.search(r"^발행:\s*(\S+)", md, flags=re.M) or re.search(r"^쓴 날:\s*(\S+)", md, flags=re.M)
        date = m.group(1) if m else ""
        # **분류는 네이버 카테고리와 같게** - 앞머리 `분류: 숫자로 보는 사업`. 없으면 회계 이야기(2026-10-13)
        c = re.search(r"^분류:\s*(.+)$", md, flags=re.M)
        cat = c.group(1).strip() if c else CATS[0]
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
<meta name="author" content="{AUTHOR['name']}">
<link rel="alternate" type="application/rss+xml" title="루위즈 글" href="/blog/feed.xml">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": title, "description": desc, "datePublished": date, "dateModified": date, "inLanguage": "ko", "mainEntityOfPage": f"{SITE}/blog/{slug}.html", "articleSection": cat, "author": AUTHOR, "publisher": ORG}, ensure_ascii=False)}</script>
{ld(ORG)}
{ld(WEBSITE)}
{CSS}
</head>
<body>
<div class="wrap">
  {TOP}
  <article>
    <h1>{html.escape(title)}</h1>
    <p class="date">{html.escape(cat)} · <time datetime="{date}">{date}</time></p>
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
        posts.append((title, slug, date, cat))

    items = ""
    for k in CATS + sorted({p[3] for p in posts} - set(CATS)):
        rows = "\n".join(
            f'      <li><a href="/blog/{s}.html">{html.escape(t)}<span class="d">{d}</span></a></li>'
            for t, s, d, c in reversed(posts) if c == k)
        if rows:
            items += f'    <h2>{html.escape(k)}</h2>\n    <ol>\n{rows}\n    </ol>\n'
    idx = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
{GA}
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>회계 이야기, 숫자로 보는 사업 — 주식회사 루위즈</title>
<meta name="description" content="연결결산, 월 마감, 현금흐름표, 관리회계, 마케팅 숫자를 실무 예시로 풀어 쓴 루위즈의 글입니다. 회계 이야기와 숫자로 보는 사업 두 갈래로 나눴습니다.">
<meta property="og:title" content="회계 이야기, 숫자로 보는 사업 — 주식회사 루위즈">
<meta property="og:description" content="연결결산, 월 마감, 현금흐름표, 관리회계, 마케팅 숫자를 실무 예시로 풀어 쓴 루위즈의 글입니다. 회계 이야기와 숫자로 보는 사업 두 갈래로 나눴습니다.">
<link rel="canonical" href="{SITE}/blog/">
<link rel="icon" href="/logo.png">
<link rel="alternate" type="application/rss+xml" title="루위즈 글" href="/blog/feed.xml">
{ld(ORG)}
{ld(WEBSITE)}
{CSS}
</head>
<body>
<div class="wrap">
  {TOP}
  <div class="list">
    <h1>글</h1>
{items}  </div>
  {FOOTER}
</div>
</body>
</html>
"""
    io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8", newline="\n").write(idx)
    home(posts)
    print(f"ok  글 {len(posts)}장 + 목록")
    for t, s, d, c in posts:
        print(f"    /blog/{s}.html   {c} · {t}")
    sitemap()
    feed(posts)
    pages = static_pages()
    llms(posts, pages)
    ai_files(pages)


# **AI 가 읽는 자리**(2026-11-23 GEO 점검 - GEO Optimizer 평균 52.7점). 화면에는 안 보인다.
# 작성자는 검색엔진용 정보에만 넣는다 - 대표님: 「ai 만 읽게 하고 사람은 안 읽히도록」(홈페이지에 대표 소개를 안 넣기로 한 것과 같은 결)
ORG = {"@type": "Organization", "name": "주식회사 루위즈", "alternateName": ["루위즈", "Luwiz"], "url": SITE,
       "logo": {"@type": "ImageObject", "url": f"{SITE}/logo.png"}, "email": "contact@luwiz.co.kr",
       # 주소 · 전화번호는 넣지 않는다(대표님 2026-11-23 - 주소는 지도에 핀이 박힌다, 09-29) - 연락 창구는 메일 하나
       "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "email": "contact@luwiz.co.kr", "availableLanguage": ["ko"]},
       "sameAs": ["https://www.linkedin.com/company/luwiz-kr/", "https://blog.naver.com/luwiz"]}
WEBSITE = {"@type": "WebSite", "name": "주식회사 루위즈", "url": SITE + "/", "inLanguage": "ko", "publisher": {"@type": "Organization", "name": "주식회사 루위즈"}}


def ld(obj):
    return f'<script type="application/ld+json">{json.dumps(dict(obj, **{"@context": "https://schema.org"}), ensure_ascii=False)}</script>'


def faq_ld(t):
    """화면에 있는 자주 묻는 질문(<details><summary>질문</summary><p>답</p>)을 FAQPage 로. 없으면 빈 글."""
    qa = [(html.unescape(re.sub(r"<[^>]+>", "", q)).strip(), html.unescape(re.sub(r"<[^>]+>", "", a)).strip())
          for q, a in re.findall(r"(?s)<summary>(.*?)</summary>\s*<p>(.*?)</p>", t)]
    if not qa:
        return ""
    return ld({"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]})
AUTHOR = {"@type": "Person", "name": "조윤제", "jobTitle": "대표, 공인회계사", "hasCredential": {"@type": "EducationalOccupationalCredential", "credentialCategory": "공인회계사"}, "worksFor": {"@type": "Organization", "name": "주식회사 루위즈", "url": SITE},
          "sameAs": ["https://www.linkedin.com/in/younjecho"]}
FEED_LINK = '<link rel="alternate" type="application/rss+xml" title="루위즈 글" href="/blog/feed.xml">'


def feed(posts):
    """blog/feed.xml - 새 글 알림(RSS). AI 검색과 구독기가 새 글을 찾는 길."""
    import datetime
    items = []
    for t, s, d, c in sorted(posts, key=lambda p: p[2], reverse=True):
        try:
            when = datetime.datetime.strptime(d, "%Y-%m-%d").strftime("%a, %d %b %Y 09:00:00 +0900")
        except ValueError:
            when = ""
        items.append(f"  <item><title>{html.escape(t)}</title><link>{SITE}/blog/{s}.html</link>"
                     f"<guid>{SITE}/blog/{s}.html</guid><category>{html.escape(c)}</category><pubDate>{when}</pubDate></item>")
    io.open(os.path.join(OUT, "feed.xml"), "w", encoding="utf-8", newline="\n").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>\n'
        f"  <title>루위즈 글</title><link>{SITE}/blog/</link><description>연결결산, 월 마감, FP&amp;A에 대해 쓴 글</description><language>ko</language>\n"
        + "\n".join(items) + "\n</channel></rss>\n")


def static_pages():
    """손으로 만든 화면(첫 화면 · 제품 · 솔루션 · 공고 · 개인정보)에 회사 정보와 RSS 연결을 붙인다. 이미 있으면 그대로.
    그 화면들의 제목 · 설명을 돌려준다(llms.txt 재료)."""
    out = []
    for rel in ["index.html"] + sorted(f"{d}/{f}" for d in ("about", "product", "solution", "notice", "privacy")
                                       for f in os.listdir(os.path.join(HERE, d)) if f.endswith(".html")):
        p = os.path.join(HERE, *rel.split("/"))
        t = io.open(p, encoding="utf-8").read()
        add = ""
        if FEED_LINK not in t:
            add += FEED_LINK + "\n"
        # 회사 정보는 늘 최신 ORG 로 갈아 끼운다(한 줄짜리 ld 만 - 첫 화면의 손으로 쓴 여러 줄 회사 정보는 그대로 두고 연락 창구만 더한다)
        t = re.sub(r'<script type="application/ld\+json">\{"@type": "Organization".*?</script>\n', "", t)
        if '\n  "@type": "Organization"' not in t:          # 첫 화면의 손으로 쓴 여러 줄 회사 정보가 없으면
            add += ld(ORG) + "\n"
        elif '"contactPoint"' not in t:
            t = t.replace('"email": "contact@luwiz.co.kr",\n', '"email": "contact@luwiz.co.kr",\n  "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "email": "contact@luwiz.co.kr", "availableLanguage": ["ko"]},\n', 1)
        if '"@type": "WebSite"' not in t:
            add += ld(WEBSITE) + "\n"
        if '"FAQPage"' not in t:
            add += (faq_ld(t) + "\n") if faq_ld(t) else ""
        t = t.replace('alt="루위즈"', 'alt="주식회사 루위즈 로고"')
        if add:
            t = t.replace("</head>", add + "</head>", 1)
        io.open(p, "w", encoding="utf-8", newline="\n").write(t)
        title = html.unescape((re.search(r"<title>(.*?)</title>", t, re.S) or [None, ""])[1]).strip()
        desc = html.unescape((re.search(r'<meta name="description" content="([^"]*)"', t) or [None, ""])[1])
        url = SITE + "/" + (rel[:-len("index.html")] if rel.endswith("index.html") else rel)
        out.append((rel, title, desc, url))
    return out


def llms(posts, pages):
    """/llms.txt - AI 에게 주는 사이트 안내(제목 · 한 줄 설명 · 주소). 화면 제목 · 설명과 글 목록에서 만든다."""
    def sec(name, rows):
        return f"## {name}\n" + "\n".join(f"- [{t}]({u}): {d}" if d else f"- [{t}]({u})" for t, u, d in rows) + "\n"
    home_ = next(p for p in pages if p[0] == "index.html")
    body = f"# 주식회사 루위즈\n\n> {home_[2]}\n\n"
    body += sec("솔루션", [(t, u, d) for r, t, d, u in pages if r.startswith("solution/")]) + "\n"
    body += sec("제품", [(t, u, d) for r, t, d, u in pages if r.startswith("product/")]) + "\n"
    body += sec("글", [(t, f"{SITE}/blog/{s}.html", "") for t, s, d, c in sorted(posts, key=lambda p: p[2], reverse=True)]) + "\n"
    body += "## 연락\n- contact@luwiz.co.kr\n"
    io.open(os.path.join(HERE, "llms.txt"), "w", encoding="utf-8", newline="\n").write(body)
    print("    llms.txt · blog/feed.xml")


# AI 검색이 사이트를 읽는 길(GEO). 허락 범위는 그대로 - 전에도 모두 허용(User-agent: *)이었고, 이름을 적어 분명히 할 뿐이다
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User",
           "Googlebot", "Google-Extended", "Bingbot", "Applebot", "Applebot-Extended", "DuckAssistBot", "meta-externalagent", "Amazonbot",
           "CCBot", "cohere-ai"]


def robots_txt():
    return "".join(f"User-agent: {b}\nAllow: /\n\n" for b in AI_BOTS) + "User-agent: *\nAllow: /\n\nSitemap: " + SITE + "/sitemap.xml\n"


def ai_files(pages):
    """/.well-known/ai.txt · /ai/summary.json · /ai/faq.json · /ai/service.json - AI 에게 주는 회사 요약. 화면에 있는 말로만 만든다."""
    home_ = next(p for p in pages if p[0] == "index.html")
    t = io.open(os.path.join(HERE, "index.html"), encoding="utf-8").read()
    qa = [{"question": html.unescape(re.sub(r"<[^>]+>", "", q)).strip(), "answer": html.unescape(re.sub(r"<[^>]+>", "", a)).strip()}
          for q, a in re.findall(r"(?s)<summary>(.*?)</summary>\s*<p>(.*?)</p>", t)]
    os.makedirs(os.path.join(HERE, ".well-known"), exist_ok=True)
    os.makedirs(os.path.join(HERE, "ai"), exist_ok=True)

    def w(rel, body):
        io.open(os.path.join(HERE, *rel.split("/")), "w", encoding="utf-8", newline="\n").write(body)

    def j(o):
        return json.dumps(o, ensure_ascii=False, indent=2) + "\n"

    w(".well-known/ai.txt", f"# 주식회사 루위즈 ({SITE})\n# AI 크롤러는 모든 공개 화면을 읽고 인용해도 됩니다.\nUser-Agent: *\nAllow: /\n\n"
                            f"Summary: {SITE}/ai/summary.json\nFAQ: {SITE}/ai/faq.json\nService: {SITE}/ai/service.json\n"
                            f"LLMs: {SITE}/llms.txt\nContact: contact@luwiz.co.kr\n")
    w("ai/summary.json", j({"name": "주식회사 루위즈", "alternateName": ["루위즈", "Luwiz"], "url": SITE, "description": home_[2],
                           "language": "ko", "email": "contact@luwiz.co.kr", "about": f"{SITE}/about/", "blog": f"{SITE}/blog/"}))
    w("ai/faq.json", j({"name": "주식회사 루위즈 자주 묻는 질문", "url": f"{SITE}/", "faq": qa}))
    w("ai/service.json", j({"name": "주식회사 루위즈", "description": home_[2], "url": SITE,
                           "services": [{"name": tt.split(" — ")[0], "description": d, "url": u} for r, tt, d, u in pages
                                        if r.startswith(("solution/", "product/")) and not r.endswith("index.html")]}))
    print("    .well-known/ai.txt · ai/summary.json · ai/faq.json · ai/service.json")


def home(posts, n=4):
    """**첫 화면 글 목록** - 갈래마다 최신 n편(2026-11-13 대표님: 「카테고리 2개로 나눠서」).
    전에는 손으로 적어 10-02 의 4편에 멈춰 있었다. 표시 사이만 갈아 끼운다."""
    cols = ""
    for k in CATS:
        # 같은 날이면 번호가 뒤인 글(SLUG 아래쪽)이 먼저 - 발행일 없는 글은 쓴 날로 떨어져 날이 겹친다
        got = [p for _, p in sorted(((i, p) for i, p in enumerate(posts) if p[3] == k),
                                    key=lambda x: (x[1][2], x[0]), reverse=True)][:n]
        if not got:
            continue
        rows = "\n".join(f'          <li><a href="/blog/{s}.html"><span>{html.escape(t)}</span><time>{d}</time></a></li>'
                         for t, s, d, c in got)
        cols += f'      <div>\n        <h3>{html.escape(k)}</h3>\n        <ul class="posts2">\n{rows}\n        </ul>\n      </div>\n'
    p = os.path.join(HERE, "index.html")
    t = io.open(p, encoding="utf-8").read()
    t, hit = re.subn(r"(<!-- 글 목록:[^\n]*-->\n).*?(<!-- /글 목록 -->)",
                     lambda m: m.group(1) + '    <div class="posts3">\n' + cols + "    </div>\n    " + m.group(2),
                     t, flags=re.S)
    assert hit == 1, "index.html 에 글 목록 표시가 없어요"
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)


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
        robots_txt())
    print("    sitemap.xml  주소 %d개 · robots.txt" % len(rows))


if __name__ == "__main__":
    main()

