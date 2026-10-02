# -*- coding: utf-8 -*-
"""구글 서치 콘솔 — 사이트맵 다시 읽히기 · 색인 상태 보기.

    py gsc.py --ping     사이트맵을 다시 제출한다 (배포한 뒤에 돌린다)
    py gsc.py            색인 상태와 검색 성과를 본다

`build.py` 는 의존성 없이 도는 파일이라 여기를 따로 뒀다.

서비스 계정 `claude-docs@luwiz-docs...` 가 서치 콘솔 사용자로 들어 있어야 한다
(설정 → 사용자 및 권한). Search Console API 도 켜져 있어야 한다.

색인 생성 요청(Request Indexing)은 API 가 없다 - 서치 콘솔 화면에서 손으로 한다.
사이트맵만 다시 읽히면 구글이 따라오니 급할 때만 손으로 당긴다.
"""
import datetime as dt
import glob
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

from google.oauth2 import service_account
import google.auth.transport.requests as gat

SITE = "https://luwiz.co.kr/"
MAP = "https://luwiz.co.kr/sitemap.xml"
BASE = "https://searchconsole.googleapis.com"
LOOK = ["/", "/blog/", "/product/", "/notice/"]      # 색인 상태를 늘 보는 쪽


def token(write=False):
    key = glob.glob("C:/Users/Lenovo/.secrets/luwiz-docs-*.json")[0]
    scope = "webmasters" if write else "webmasters.readonly"
    c = service_account.Credentials.from_service_account_file(
        key, scopes=["https://www.googleapis.com/auth/" + scope])
    c.refresh(gat.Request())
    return c.token


def call(url, tok, body=None, method=None):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": "Bearer " + tok, "Content-Type": "application/json"},
        method=method)
    with urllib.request.urlopen(req, timeout=40) as r:
        txt = r.read().decode()
    return json.loads(txt) if txt.strip() else {}


def ping():
    """사이트맵을 다시 제출한다. 같은 주소를 다시 넣어도 쌓이지 않는다."""
    tok = token(write=True)
    s, m = urllib.parse.quote(SITE, safe=""), urllib.parse.quote(MAP, safe="")
    call(f"{BASE}/webmasters/v3/sites/{s}/sitemaps/{m}", tok, method="PUT")
    got = call(f"{BASE}/webmasters/v3/sites/{s}/sitemaps/{m}", tok)
    print("사이트맵 다시 제출함 — 마지막으로 읽은 날 %s · 발견된 쪽 %s" % (
        (got.get("lastDownloaded") or "아직")[:10],
        (got.get("contents") or [{}])[0].get("submitted", "?")))


def look():
    tok = token()
    s = urllib.parse.quote(SITE, safe="")
    print("== 색인 상태 ==")
    for p in LOOK:
        r = call(f"{BASE}/v1/urlInspection/index:inspect", tok,
                 {"inspectionUrl": SITE.rstrip("/") + p, "siteUrl": SITE, "languageCode": "ko"})
        st = r["inspectionResult"]["indexStatusResult"]
        print("  %-28s %s" % (p, st.get("coverageState", "?")))

    print("\n== 검색 성과 (최근 28일) ==")
    q = call(f"{BASE}/webmasters/v3/sites/{s}/searchAnalytics/query", tok,
             {"startDate": str(dt.date.today() - dt.timedelta(days=28)),
              "endDate": str(dt.date.today()),
              "dimensions": ["query"], "rowLimit": 15})
    rows = q.get("rows", [])
    if not rows:
        print("  노출 0 — 아직 검색 결과에 안 떠요")
    for x in rows:
        print("  %-30s 노출 %s · 클릭 %s · 순위 %.1f" % (
            x["keys"][0][:30], x["impressions"], x["clicks"], x.get("position", 0)))


if __name__ == "__main__":
    try:
        ping() if "--ping" in sys.argv else look()
    except urllib.error.HTTPError as e:
        print("막힘 %s — %s" % (e.code, e.read().decode()[:300]))
