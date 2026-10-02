# -*- coding: utf-8 -*-
"""IndexNow — 새 글을 네이버와 빙에 바로 알린다.

    py indexnow.py                 사이트맵에 있는 주소를 전부 알린다
    py indexnow.py /blog/x.html    고른 주소만
    py indexnow.py --check         스스로 검사

네이버 서치어드바이저가 2023-07 부터 IndexNow 를 지원한다. 한 번 쏘면 참여 검색엔진
(네이버 · 빙 · Yandex · Seznam …)에 같이 퍼진다. **구글은 참여하지 않는다** -
구글은 서치 콘솔 화면에서 손으로 색인 요청한다.

열쇠는 `<열쇠>.txt` 파일을 사이트 뿌리에 올려 두는 것으로 증명한다. 그 파일이
배포돼 있어야 받아 준다.

네이버 안내 - "사용자가 직접 수집 요청하더라도 검색로봇이 실시간으로 방문하지 않는다.
최소 1일에서 몇 주가 걸릴 수 있다." 그래도 안 알리는 것보다는 빠르다.
"""
import glob
import json
import os
import re
import sys
import urllib.error
import urllib.request

HOST = "luwiz.co.kr"
HERE = os.path.dirname(os.path.abspath(__file__))
ENDPOINT = "https://api.indexnow.org/indexnow"      # 참여 엔진에 함께 퍼진다
CHUNK = 10000                                        # 한 번에 보낼 수 있는 주소 수


def key():
    """사이트 뿌리의 `<열쇠>.txt` 에서 읽는다. 파일 이름이 곧 열쇠다."""
    for p in glob.glob(os.path.join(HERE, "*.txt")):
        name = os.path.basename(p)[:-4]
        if re.fullmatch(r"[0-9a-f]{8,128}", name):
            return name
    raise FileNotFoundError("열쇠 파일이 없어요 - 사이트 뿌리에 <16진수>.txt 를 두세요")


def urls_from_sitemap():
    xml = open(os.path.join(HERE, "sitemap.xml"), encoding="utf-8").read()
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def tell(urls):
    k = key()
    body = {"host": HOST, "key": k,
            "keyLocation": f"https://{HOST}/{k}.txt",
            "urlList": urls[:CHUNK]}
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status


def demo():
    assert re.fullmatch(r"[0-9a-f]{8,128}", key())
    u = urls_from_sitemap()
    assert u and all(x.startswith("https://" + HOST) for x in u), u[:3]
    b = {"host": HOST, "key": key(), "urlList": u}
    assert json.loads(json.dumps(b))["host"] == HOST        # 직렬화가 되나
    print("ok — 주소 %d개 · 열쇠 %s…" % (len(u), key()[:8]))


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--check" in sys.argv:
        demo()
        sys.exit()
    urls = [f"https://{HOST}{a}" if a.startswith("/") else a for a in args] or urls_from_sitemap()
    try:
        code = tell(urls)
        print("알렸어요 — 주소 %d개 · 응답 %s" % (len(urls), code))
        for u in urls:
            print("   ", u.replace("https://" + HOST, ""))
    except urllib.error.HTTPError as e:
        print("막힘 %s — %s" % (e.code, e.read().decode()[:200]))
