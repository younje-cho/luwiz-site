# -*- coding: utf-8 -*-
"""네이버 검색광고 - 말마다 월간 검색수를 잰다.

    py keywords.py          HINTS 를 고쳐 가며 쓴다. 결과는 keywords.txt

**우리 말과 고객 말이 다르다.** 페이지 제목이나 글감을 정하기 전에 여기서 먼저 잰다.
2026-09-29 에 처음 재고 알게 된 것:
  · 사업부별손익 · 공통비배부 = 0      → 「관리회계」(940)로 불러야 검색에 걸린다
  · 연결재무제표 330 · 연결회계 130     → 작지만 그 사람들이 전부 우리 고객이다
  · 현금흐름표 830                    → 연결의 두 배 반. 「간접법」 「양식」이 붙는다
  · 결산 1,720 · 전표 1,520            → 커 보이지만 남의 검색이 섞여 있다(결산소득세 · 전표 양식)

열쇠는 `.secrets` 에서 읽고 화면에 안 찍는다 - 소스 · 커밋에 평문으로 남기지 않는다.
  naver_ad_customer.txt · naver_ad_key.txt · naver_ad_secret.txt
키는 searchad.naver.com → 도구 → API 사용 관리 에서 받는다(ads.naver.com 이 아니다).
"""
import base64, hashlib, hmac, io, json, os, time, urllib.parse, urllib.request
S = os.path.expanduser("~") + "/.secrets/"
def secret(n): return io.open(S + n, encoding="utf-8-sig").read().strip()
CUST, KEY, SEC = secret("naver_ad_customer.txt"), secret("naver_ad_key.txt"), secret("naver_ad_secret.txt")

def call(uri, params):
    ts = str(int(time.time() * 1000))
    sign = base64.b64encode(hmac.new(SEC.encode(), f"{ts}.GET.{uri}".encode(), hashlib.sha256).digest()).decode()
    r = urllib.request.Request("https://api.searchad.naver.com" + uri + "?" + urllib.parse.urlencode(params),
        headers={"X-Timestamp": ts, "X-API-KEY": KEY, "X-Customer": CUST, "X-Signature": sign})
    return json.load(urllib.request.urlopen(r, timeout=20))

HINTS = ["연결재무제표", "연결결산", "연결회계", "현금흐름표", "월마감", "결산",
         "재무제표작성", "자금일보", "관리회계", "사업부별손익", "공통비배부",
         "연결정산표", "내부거래", "원가계산", "예산관리", "전표"]
CORE = ("연결", "현금흐름", "마감", "결산", "재무제표", "자금", "관리회계",
        "손익", "배부", "정산표", "내부거래", "원가", "예산", "전표", "분개", "장부")
def num(v): return 0 if v in ("< 10", "<10", None) else int(str(v).replace(",", ""))

rows, seen = [], {}
for i in range(0, len(HINTS), 5):
    for k in call("/keywordstool", {"hintKeywords": ",".join(HINTS[i:i+5]), "showDetail": 1}).get("keywordList", []):
        n = k["relKeyword"]
        if n in seen or not any(c in n for c in CORE):
            continue
        seen[n] = 1
        rows.append((n, num(k.get("monthlyPcQcCnt")), num(k.get("monthlyMobileQcCnt")), k.get("compIdx", "")))
    time.sleep(0.4)

rows.sort(key=lambda r: -(r[1] + r[2]))
out = io.open("keywords.txt", "w", encoding="utf-8")
out.write(f"{'키워드':<22}{'합계':>8}{'PC':>8}{'모바일':>9}  경쟁\n" + "-" * 58 + "\n")
for n, pc, mo, c in rows[:60]:
    out.write(f"{n:<22}{pc+mo:>8,}{pc:>8,}{mo:>9,}  {c}\n")
out.close()
print(len(rows))
