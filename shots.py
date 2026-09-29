# -*- coding: utf-8 -*-
"""**제품 페이지에 들어갈 화면 캡처를 찍는다.**  py shots.py

홈페이지 `product/*.html` 의 점선 네모 자리를 채운다. 화면이 바뀌면 다시 돌리면 된다.

**실 고객이 찍히면 안 된다.** 그래서 캡처용 DB(`api/demo_shot.db` · 「가나전자」만 담김)를
보는 API 를 8301 에 따로 띄우고, 그것만 보는 web 을 3010 에 띄운 뒤 찍는다.
작업 탭이 쓰는 8300 · 3300 은 건드리지 않는다.

    cd api  && DATABASE_URL="sqlite:///.../api/demo_shot.db" py -m uvicorn main:app --port 8301
    cd web-shot && NEXT_PUBLIC_API=http://127.0.0.1:8301 npx next dev -p 3010
    cd luwiz-site && py shots.py

계정은 `~/.secrets/luwiz_demo_login.txt` 한 줄씩. 소스에 안 적는다.
"""
import io
import pathlib
import re
import sys

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WEB = "http://127.0.0.1:3010"
OUT = pathlib.Path(__file__).parent / "shot"
SECRET = pathlib.Path.home() / ".secrets" / "luwiz_demo_login.txt"

#: (파일 이름, 주소, 무엇을 보이려는 것인가[, 먼저 누를 탭]) - product/*.html 의 점선 네모와 짝이다
SHOTS = [
    ("consol-inv",     "/c/2/consol/inv",            "투자자본상계 — 취득내역 · 자본변동 · PPA", "취득내역 및 자본변동"),
    ("consol-ic",      "/c/2/consol/ic",             "내부거래제거 — 짝이 안 맞는 금액"),
    ("consol-books",   "/c/2/workspace?tab=books",   "결산 파일 — 시트 한 벌"),
    # 네 번째 칸은 찍기 전에 할 일 - 탭 이름이거나, 페이지를 만지는 함수다
    ("cash-daily",     "/c/2/cash",                  "자금일보 — 나날의 입출금과 잔액", "bank"),
    ("alloc",          "/c/2/alloc",                 "사업부별 손익 — 직접비와 배부"),
    ("scenario",       "/c/2/scenario",              "시나리오 분석 — 민감도"),
    ("cf",             "/c/2/reporting/cf",          "현금흐름표 — 명세와 검산"),
]


def login(page):
    """로그인. 비밀번호는 파일에서만 읽고 찍지 않는다."""
    d = dict(l.split("=", 1) for l in SECRET.read_text(encoding="utf-8").splitlines()
             if "=" in l and not l.startswith("#"))
    page.goto(WEB + "/login", wait_until="networkidle")
    # **JS 가 붙기 전에 누르면 폼이 그냥 GET 으로 넘어간다** - dev 서버는 첫 컴파일이 느리다
    page.wait_for_timeout(4000)
    page.fill('input[type="email"], input[name="email"]', d["email"])
    page.fill('input[type="password"]', d["password"])
    page.click('button[type="submit"]')
    # 로그인 뒤 회사를 고르는 화면이 한 번 더 설 수 있다
    for _ in range(12):
        page.wait_for_timeout(1000)
        if "/login" not in page.url:
            break
    if "/login" in page.url:
        print("  화면이 말하는 것:", " ".join(page.inner_text("body").split())[:200])
        return False
    page.wait_for_timeout(2000)
    return True


def trim(f, pad=24):
    """아래·오른쪽의 흰 여백을 잘라낸다. 화면마다 내용 높이가 달라서 그냥 찍으면 밑이 텅 빈다."""
    from PIL import Image, ImageChops
    im = Image.open(f).convert("RGB")
    bg = Image.new("RGB", im.size, im.getpixel((im.width - 2, im.height - 2)))
    box = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 8 else 0).getbbox()
    if box:
        im.crop((0, 0, min(im.width, box[2] + pad), min(im.height, box[3] + pad))).save(f)


def main():
    OUT.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=2)
        if not login(page):
            print("로그인이 안 됐어요 —", page.url)
            b.close()
            return 1
        # **연결 화면은 로그인 직후 첫 방문에서 터진다**(React #310) - 한 번 들렀다 간다
        page.goto(WEB + "/c/2/consol", wait_until="domcontentloaded")
        page.wait_for_timeout(4000)
        only = [a for a in sys.argv[1:] if not a.startswith("--")]
        for row in SHOTS:
            if only and row[0] not in only:
                continue
            name, path, what = row[:3]
            tab = row[3] if len(row) > 3 else None
            ok = False
            for _ in range(3):          # 간헐적으로 터지므로 다시 불러 본다
                page.goto(WEB + path, wait_until="domcontentloaded")
                page.wait_for_timeout(4500)
                if page.locator("main").count():
                    ok = True
                    break
            if ok and tab == "bank":
                # **통장 원천으로 보인다** - 활동별로 거래처가 펴져 서고, 계정 축이 아니라
                # 통장 줄 그대로다. 기본 기간은 최근 두 주뿐이라 6월을 통째로 잡는다.
                page.locator("main select").first.select_option("bank")
                page.wait_for_timeout(3500)
                for i, v in enumerate(("2026-06-01", "2026-06-16")):
                    page.locator('input[type="date"]').nth(i).fill(v)
                    page.wait_for_timeout(600)
                # 포커스가 남으면 날짜 칸에 파란 테두리가 찍힌다
                page.evaluate("document.activeElement && document.activeElement.blur()")
                page.wait_for_timeout(4500)
                # 접힌 묶음은 편 채로 보인다 - 무엇이 묶였는지가 보여야 한다
                for _ in range(6):
                    before = page.locator("main tbody tr").count()
                    hit = False
                    for tr in page.locator("main tbody tr").all():
                        head = tr.locator("td").first.inner_text()
                        if head.strip().startswith(("›", ">", "▸", "▶")):
                            tr.locator("td").first.click()
                            page.wait_for_timeout(1200)
                            hit = True
                            break
                    if not hit or page.locator("main tbody tr").count() == before:
                        break
            elif ok and tab:
                try:
                    page.get_by_text(tab, exact=True).first.click(timeout=4000)
                    page.wait_for_timeout(3500)
                except Exception:
                    pass
            f = OUT / (name + ".png")
            # **왼쪽 메뉴는 뺀다** - 제품 페이지에서는 표가 주인공이다
            box = page.locator("main")
            (box if ok else page).screenshot(path=str(f))
            trim(f)
            print("%-14s %s %-26s %s" % (name, "○" if ok else "X", path, what))
        b.close()
    print("\n%d 장 · %s" % (len(SHOTS), OUT))
    return 0


def put():
    """찍은 것을 product/*.html 의 점선 네모 자리에 끼운다.  py shots.py --put

    `<div class="shot">` 를 `<img>` 로 바꾼다. 설명은 alt 로 남긴다 -
    캡처가 안 뜨는 자리에서도 무엇이 있어야 하는지 읽힌다.
    """
    pair = {  # 파일 이름 → (어느 페이지, 그 페이지 안 몇 번째 자리)
        "product/consolidation.html":        ["consol-inv", "consol-ic", "consol-books"],
        "product/daily-cash-report.html":    ["cash-daily"],
        "product/management-accounting.html": ["alloc", "scenario"],
        "product/cash-flow-statement.html":  ["cf"],
    }
    root = pathlib.Path(__file__).parent
    for p, names in pair.items():
        s = io.open(root / p, encoding="utf-8").read()
        it = iter(names)

        def swap(m):
            name = next(it)
            what = " ".join(m.group(1).split())
            return ('<img class="shot" src="/shot/%s.png" alt="%s" loading="lazy">' % (name, what))

        s2 = re.sub(r'<div class="shot">\s*<b>\[ 화면 \]</b>\s*(.+?)\s*</div>', swap, s, flags=re.S)
        io.open(root / p, "w", encoding="utf-8", newline="\n").write(s2)
        print("%-38s %d 자리" % (p, len(names)))


if __name__ == "__main__":
    sys.exit(put() if "--put" in sys.argv else main())
