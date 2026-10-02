# -*- coding: utf-8 -*-
"""블로그 글에 넣는 그래프 → `blog/img/`.

    py charts.py          전부 다시 그린다
    py charts.py --check  스스로 검사

원고(옵시디언)와 숫자가 **두 곳에 있다.** 글의 표를 고치면 여기도 고친다 -
한쪽만 고치면 그래프와 표가 어긋난다. 글마다 함수 하나.
네이버에 올릴 때는 PNG 를 손으로 올린다(HTML 붙여넣기로는 안 들어간다).
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

#: 그림은 **원고 옆**에 둔다 - 옵시디언에서도 보여야 글을 쓰면서 확인한다.
#: 홈페이지 쪽 `blog/img/` 로는 `build.py` 가 옮긴다.
OUT = "C:/Users/Lenovo/Documents/Obsidian/Younje/1. Project/루위즈/마케팅/글/img"
INK, GREY, HOT = "#1f2937", "#cbd5e1", "#2563eb"

for f in ("Malgun Gothic", "맑은 고딕", "NanumGothic", "Gulim"):
    if any(f == x.name for x in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = f
        break
plt.rcParams["axes.unicode_minus"] = False


def bars(ax, names, vals, fmt, title, note):
    """가로 막대 하나. 제일 큰 칸만 색을 준다 - 그 칸이 이 그래프의 답이다."""
    top = max(range(len(vals)), key=lambda i: abs(vals[i]))
    ax.barh(names, vals, color=[HOT if i == top else GREY for i in range(len(vals))],
            height=.62, zorder=3)
    ax.set_title(title, fontsize=13, color=INK, pad=30, loc="left", fontweight="bold")
    ax.invert_yaxis()
    ax.axvline(0, color="#94a3b8", lw=.9, zorder=4)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.set_xticks([])
    ax.tick_params(axis="y", length=0, labelsize=11, colors=INK)
    span = max(abs(v) for v in vals) or 1
    for i, v in enumerate(vals):
        ax.text(v + span * (.03 if v >= 0 else -.03), i, fmt(v), va="center",
                ha="left" if v >= 0 else "right", fontsize=11,
                color=HOT if i == top else "#64748b",
                fontweight="bold" if i == top else "normal")
    ax.set_xlim(min(0, min(vals)) - span * .35, max(0, max(vals)) + span * .35)
    ax.text(0, 1.035, note, transform=ax.transAxes, fontsize=10, color="#64748b",
            va="bottom", ha="left")


def funnel_gap():
    """09편 - 같은 표를 두 가지로 보면 손댈 칸이 바뀐다."""
    names = ["상품 상세 열람", "장바구니 담기", "결제 시작", "결제 완료"]
    gap = [0.4, -3.5, -0.5, -8.0]            # 기준 대비 %p
    lift = [0, 468, 29, 384]                 # 되돌렸을 때 늘어나는 주문(건)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 3.5), dpi=150)
    bars(a, names, gap, lambda v: "%+.1f%%p" % v,
         "기준 대비 차이", "가장 벌어진 칸은 결제 완료")
    bars(b, names, lift, lambda v: "—" if v == 0 else "+%s건" % format(int(v), ","),
         "되돌리면 늘어나는 주문", "가장 큰 칸은 장바구니")
    fig.tight_layout(pad=1.4)
    p = os.path.join(OUT, "funnel-gap.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def funnel_basic():
    """09편 기본 - 12만이 들어와 3,748이 산다. 칸 사이에 전환율."""
    names = ["사이트 방문", "상품 상세 열람", "장바구니 담기", "결제 시작", "결제 완료"]
    cnt = [120000, 26400, 7392, 4805, 3748]
    fig, ax = plt.subplots(figsize=(8.6, 4.4), dpi=150)
    top = cnt[0]
    for i, (nm, c) in enumerate(zip(names, cnt)):
        w = c / top
        ax.barh(-i, w, left=(1 - w) / 2, height=.52,
                color=HOT if i == len(cnt) - 1 else "#93b4f5", zorder=3)
        ax.text(-0.04, -i, nm, ha="right", va="center", fontsize=11.5, color=INK)
        ax.text(1.04, -i, format(c, ","), ha="left", va="center", fontsize=11.5,
                color=INK, fontweight="bold" if i == len(cnt) - 1 else "normal")
        if i:
            ax.text(.5, -i + .5, "%.1f%%" % (c / cnt[i - 1] * 100), ha="center",
                    va="center", fontsize=10.5, color="#64748b")
    ax.set_xlim(-.42, 1.3)
    ax.set_ylim(-len(cnt) + .4, .6)
    ax.axis("off")
    ax.text(.5, .52, "전체 전환율 3.12%", ha="center", fontsize=11.5,
            color=HOT, fontweight="bold")
    fig.tight_layout(pad=.6)
    p = os.path.join(OUT, "funnel-basic.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


ALL = [funnel_basic, funnel_gap]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in ALL:
        p = f()
        print("%s  %.0f KB" % (os.path.basename(p), os.path.getsize(p) / 1024))
    if "--check" in sys.argv:
        assert plt.rcParams["font.family"][0] != "sans-serif", "한글 폰트를 못 찾았어요"
        print("ok")
