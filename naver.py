# -*- coding: utf-8 -*-
"""옵시디언 원고 → 네이버 블로그에 붙여 넣을 HTML.

    py naver.py "04 AI는 정리된 숫자에서 시작한다"
    py naver.py --all

홈페이지는 `build.py` 가 뽑는다. 네이버는 모양이 달라서 따로 만든다 -
네이버 편집기가 빈 줄을 먹어서 `<p>&nbsp;</p>` 로 띄워야 간격이 산다.

브라우저로 열어 전체 선택 · 복사해서 네이버 글쓰기에 붙여 넣는다.
네이버는 완결된 글을 좋아하고 외부 링크가 많으면 노출이 떨어져서,
전문을 올리고 끝에 luwiz.co.kr 한 줄만 붙인다.
"""
import html
import os
import re
import sys

SRC = "C:/Users/Lenovo/Documents/Obsidian/Younje/1. Project/루위즈/마케팅/글/"
OUT = "C:/Users/Lenovo/Downloads/회사/Luwiz/08_영업 참고자료/블로그 붙여넣기/"

HEAD = ("<!doctype html><meta charset=utf-8><title>%s</title><style>"
        "body{font-family:'맑은 고딕',sans-serif;max-width:720px;margin:40px auto;"
        "line-height:1.9;font-size:16px;color:#222}"
        "h1{font-size:26px;margin:40px 0 20px}h2{font-size:20px;margin:36px 0 12px}"
        "h3{font-size:17px;margin:28px 0 10px}"
        "blockquote{border-left:3px solid #ccc;margin:16px 0;padding:4px 0 4px 16px;color:#555}"
        "pre{background:#f5f5f5;padding:14px 16px;font-family:'D2Coding',monospace;"
        "font-size:14px;line-height:1.7;white-space:pre-wrap}li{margin:6px 0}"
        "table{border-collapse:collapse;margin:16px 0}"
        "th,td{border:1px solid #ddd;padding:8px 12px;text-align:left}"
        "th{background:#f7f7f7}</style>\n")
FOOT = ('<hr style="border:0;border-top:1px solid #ddd;margin:44px 0 20px">'
        '<p style="color:#666">루위즈 — 연결결산 · FP&amp;A 도구를 만듭니다. '
        '<a href="https://luwiz.co.kr">luwiz.co.kr</a></p>\n')
GAP = "<p>&nbsp;</p>\n"


def inline(s):
    """줄 안의 서식. 이스케이프를 먼저 하고 마크업을 연다."""
    s = html.escape(s, quote=True)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def convert(md):
    body = md.split("---\n", 2)[2] if md.startswith("---\n") else md
    out, lines, i = [], body.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        t = ln.strip()
        if not t:
            i += 1
            continue
        if t.startswith("```"):                                   # 코드 블록
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(html.escape(lines[i]))
                i += 1
            out.append("<pre>%s</pre>" % "\n".join(buf))
        elif t.startswith("#"):                                   # 제목
            n = len(t) - len(t.lstrip("#"))
            out.append("<h%d>%s</h%d>" % (n, inline(t.lstrip("# ")), n))
        elif t.startswith("|"):                                   # 표
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            i -= 1
            cells = []
            for k, r in enumerate(rows):
                if k == 1 and all(set(c) <= set(" -:") for c in r):   # 구분선
                    continue
                tag = "th" if k == 0 else "td"
                cells.append("<tr>%s</tr>" % "".join(
                    "<%s>%s</%s>" % (tag, inline(c), tag) for c in r))
            out.append("<table>%s</table>" % "".join(cells))
        elif re.match(r"^[-*•]\s", t):                            # 목록
            items = []
            while i < len(lines) and re.match(r"^[-*•]\s", lines[i].strip()):
                items.append("<li>%s</li>" % inline(re.sub(r"^[-*•]\s+", "", lines[i].strip())))
                i += 1
            i -= 1
            out.append("<ul>%s</ul>" % "".join(items))
        elif t.startswith(">"):                                   # 인용
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(inline(lines[i].strip().lstrip("> ")))
                i += 1
            i -= 1
            out.append("<blockquote>%s</blockquote>" % "<br>".join(buf))
        else:                                                     # 문단
            out.append("<p>%s</p>" % inline(t))
        i += 1
    return out


def make(name):
    md = open(os.path.join(SRC, name + ".md"), encoding="utf-8").read()
    blocks = convert(md)
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".html")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(HEAD % html.escape(name))
        f.write(GAP.join(b + "\n" for b in blocks))
        f.write(FOOT)
    return path, len(blocks)


def demo():
    b = convert("---\nx: 1\n---\n# 제목\n**굵게** 와 `코드`\n\n- 하나\n- 둘\n")
    assert b[0] == "<h1>제목</h1>", b
    assert "<strong>굵게</strong>" in b[1] and "<code>코드</code>" in b[1], b
    assert b[2] == "<ul><li>하나</li><li>둘</li></ul>", b
    assert "&amp;" in convert("A & B\n")[0]          # 이스케이프가 먼저다
    print("ok")


if __name__ == "__main__":
    if "--check" in sys.argv:
        demo()
    elif "--all" in sys.argv:
        for f in sorted(os.listdir(SRC)):
            if f.endswith(".md"):
                print("%s  블록 %d" % make(f[:-3]))
    elif len(sys.argv) > 1:
        print("%s  블록 %d" % make(sys.argv[1]))
    else:
        print(__doc__)
