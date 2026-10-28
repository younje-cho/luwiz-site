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
from matplotlib.lines import Line2D
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
    ax.set_xlim(min(0, min(vals)) - span * (.35 if min(vals) < 0 else .02), max(0, max(vals)) + span * .35)
    ax.text(0, 1.035, note, transform=ax.transAxes, fontsize=10, color="#64748b",
            va="bottom", ha="left")


def center_head(ax):
    """제목 · 한 줄 설명을 그래프 가운데로 - 나란히 놓은 그래프에서 어느 제목이 어느 그래프 것인지 바로 읽히게."""
    title = ax.get_title(loc="left")
    ax.set_title("", loc="left")
    ax.set_title(title, fontsize=13, color=INK, pad=30, loc="center", fontweight="bold")
    note = [t for t in ax.texts if t.get_transform() == ax.transAxes]   # 값 글자는 데이터 좌표라 안 걸린다
    for t in note:
        t.set_x(.5)
        t.set_ha("center")


def funnel_gap():
    """09편 - 같은 표를 두 가지로 보면 손댈 칸이 바뀐다."""
    names = ["상품 상세 열람", "장바구니 담기", "결제 시작", "결제 완료"]
    gap = [0.4, -3.5, -0.5, -8.0]            # 기준 대비 %p
    lift = [0, 468, 29, 384]                 # 되돌렸을 때 늘어나는 주문(건)
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 3.5), dpi=150)
    bars(a, names, gap, lambda v: "%+.1f%%p" % v,
         "기준 대비 차이", "가장 많이 떨어진 칸은 결제 완료")
    bars(b, names, lift, lambda v: "—" if v == 0 else "+%s건" % format(int(v), ","),
         "되돌리면 늘어나는 주문", "가장 큰 칸은 장바구니")
    b.tick_params(labelleft=False)           # 줄 이름은 왼쪽 그래프와 같다 - 두 번 쓰지 않는다
    center_head(a)
    center_head(b)
    fig.tight_layout(pad=1.4, w_pad=4)
    # 사이에 점선 - 왼쪽 +0.4%p 가 오른쪽 그래프의 값처럼 읽혔다(2026-10-16 대표님, A안)
    x = (a.get_position().x1 + b.get_position().x0) / 2
    fig.add_artist(Line2D([x, x], [.04, .98], transform=fig.transFigure, color=GREY, lw=1, ls=(0, (4, 4))))
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


MONTHS = ["11월", "12월", "1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월"]


def conv_trend():
    """11편 - 열두 달 전체 전환율과 평소 범위(중위값 ±0.2%p). 이번 달 10월만 색을 준다."""
    conv = [3.45, 3.30, 2.75, 2.85, 3.05, 3.15, 3.20, 3.00, 2.95, 3.05, 3.25, 3.12]
    mid = 3.08                                          # 중위값(3.085)을 글과 같게 반올림
    fig, ax = plt.subplots(figsize=(10.4, 3.9), dpi=150)
    x = range(len(conv))
    ax.axhspan(mid - .2, mid + .2, color="#e2e8f0", zorder=1, lw=0)
    ax.text(len(conv) - .5, mid + .2, "평소 범위 %.2f~%.2f%%" % (mid - .2, mid + .2),
            ha="right", va="bottom", fontsize=10, color="#64748b")
    ax.plot(x, conv, color="#94a3b8", lw=2, marker="o", ms=5, zorder=3)
    ax.plot([len(conv) - 1], [conv[-1]], marker="o", ms=9, color=HOT, zorder=4)
    ax.text(len(conv) - 1, conv[-1] - .09, "이번 달 %.2f%%" % conv[-1], ha="center", va="top",
            fontsize=11, color=HOT, fontweight="bold")
    for i in (0, 1, 2, 3):                             # 범위 밖 네 달 - 연말 프로모션 · 연초
        ax.text(i, conv[i] + (.06 if conv[i] > mid else -.09), "%.2f%%" % conv[i], ha="center",
                va="bottom" if conv[i] > mid else "top", fontsize=10, color=INK)
    ax.set_xticks(list(x), MONTHS)
    ax.set_ylim(2.5, 3.65)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.tick_params(axis="x", length=0, labelsize=10.5, colors=INK)
    ax.set_title("열두 달 전체 전환율", fontsize=13, color=INK, pad=12, loc="left", fontweight="bold")
    fig.tight_layout(pad=1.2)
    p = os.path.join(OUT, "conv-trend.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def refund_lag():
    """12편 - 평소 대비 몇 배인가. 환불월로 센 환불율은 늦게 오르고 늦게 내려온다.
    결제월 환불율(5%)이 7 · 8월만 9%, 환불은 그달 40% · 다음 달 45% · 그다음 달 15%."""
    m = ["5월", "6월", "7월", "8월", "9월", "10월"]
    by_refund = [5.0, 5.0, 6.6, 8.4, 7.4, 5.6]          # 그달 환불 ÷ 그달 매출
    first = [2.0, 2.0, 3.6, 3.6, 2.0, 2.0]              # 그달 결제분의 첫 달 환불율
    a = [v / by_refund[0] for v in by_refund]
    b = [v / first[0] for v in first]
    fig, ax = plt.subplots(figsize=(10.4, 3.9), dpi=150)
    x = range(len(m))
    ax.axhline(1, color="#cbd5e1", lw=1, zorder=1)
    ax.plot(x, a, color="#94a3b8", lw=2.4, marker="o", ms=5, zorder=3)
    ax.plot(x, b, color=HOT, lw=2.4, marker="o", ms=5, zorder=4)
    ax.text(4.08, a[4] + .03, "그달 환불 ÷ 그달 매출\n8월에 꼭대기, 9월에도 높음", ha="left", va="bottom", fontsize=10.5,
            color="#64748b", linespacing=1.4)
    ax.text(2.5, b[2] + .05, "결제한 달의 첫 달 환불율  7월에 바로 뜀", ha="center", va="bottom", fontsize=10.5,
            color=HOT, fontweight="bold")
    ax.set_xticks(list(x), m)
    ax.set_ylim(.8, 2.05)
    ax.set_yticks([1], ["평소"])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#cbd5e1")
    ax.tick_params(length=0, labelsize=10.5, colors=INK)
    ax.set_title("환불율, 평소의 몇 배인가", fontsize=13, color=INK, pad=12, loc="left", fontweight="bold")
    fig.tight_layout(pad=1.2)
    p = os.path.join(OUT, "refund-lag.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


#: 12편 예시 - 결제월 환불율(평소 5%, 7 · 8월 9%), 환불은 그달 40% · 다음 달 45% · 그다음 달 15%. 10월 말 기준
COHORT_M = ["5월", "6월", "7월", "8월", "9월", "10월"]
COHORT_RATE = [5, 5, 9, 9, 5, 5]
COHORT_SPLIT = [.40, .45, .15]


def cohort_cells():
    """[결제월][환불월] 환불율(%) - 10월 뒤 칸은 None(아직 안 옴)."""
    n = len(COHORT_M)
    cells = [[None] * n for _ in range(n)]
    for i, r in enumerate(COHORT_RATE):
        for k, s in enumerate(COHORT_SPLIT):
            if i + k < n:
                cells[i][i + k] = round(r * s, 2)
    return cells


def refund_cohort():
    """12편 - 하이메디 대시보드 '환불 코호트 - 비율'과 같은 모양. 아래 결제월 · 오른쪽 환불월 · 끝에 지금까지 합계."""
    cells = cohort_cells()
    n = len(COHORT_M)
    fig, ax = plt.subplots(figsize=(10.4, 4.6), dpi=150)
    ax.set_xlim(-.5, n + .9)
    ax.set_ylim(n - .5, -1.1)
    for i in range(n):
        hot = COHORT_RATE[i] > 5
        for j in range(n + 1):
            if j == n:
                tot = sum(v for v in cells[i] if v)
                full = i + len(COHORT_SPLIT) <= n
                ax.add_patch(plt.Rectangle((j + .1, i - .45), .9, .9, color="#f1f5f9", zorder=1))
                ax.text(j + .55, i, ("%g%%" % round(tot, 2)) + ("" if full else "\n(덜 참)"), ha="center", va="center",
                        fontsize=10.5 if full else 9.5, color="#991b1b" if hot else INK, fontweight="bold")
                continue
            v = cells[i][j]
            if v is None:
                continue
            a = min(v / 4.2, 1)
            face = (1 - .85 * a * (37 / 255 * 0 + 1), 1 - .6 * a, 1 - .15 * a) if not hot else (1 - .1 * a, 1 - .55 * a, 1 - .55 * a)
            ax.add_patch(plt.Rectangle((j - .45, i - .45), .9, .9, color=face, zorder=1))
            if i == j:
                ax.add_patch(plt.Rectangle((j - .45, i - .45), .9, .9, fill=False, ec=INK, lw=1.6, zorder=2))
            ax.text(j, i, "%.1f" % v if v * 10 % 1 == 0 else "%.2f" % v, ha="center", va="center", fontsize=10.5,
                    color="#991b1b" if hot else INK, fontweight="bold" if i == j else "normal", zorder=3)
    for j, mname in enumerate(COHORT_M):
        ax.text(j, -.8, mname, ha="center", va="center", fontsize=10.5, color="#64748b")
    ax.text(n + .55, -.8, "합계", ha="center", va="center", fontsize=10.5, color="#64748b")
    ax.set_yticks(range(n), COHORT_M)
    ax.set_xticks([])
    ax.text(-.5, -1.45, "가로줄: 결제한 달   칸: 환불된 달   단위: 그 달 결제액 중 %   굵은 테두리: 첫 달",
            ha="left", va="center", fontsize=9.5, color="#64748b")
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0, labelsize=10.5, colors=INK)
    ax.set_title("환불 코호트 (10월 말 기준)", fontsize=13, color=INK, pad=34, loc="left", fontweight="bold")
    fig.tight_layout(pad=1.2)
    p = os.path.join(OUT, "refund-cohort.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


#: 13편 예시 - 5 · 6월 평균 한 달(만 원). 결제액 · 광고비 · 그 달 고객이 결국 환불한 비율(코호트 합계)
CHANNELS = {"인스타그램 광고": (8000, 2000, .12), "네이버 검색광고": (8000, 2150, .02),
            "자연 검색": (5000, 0, .016), "재방문": (4000, 0, .0125)}


def refund_channel():
    """16편 - 광고 두 곳의 ROAS 를 결제액 기준과 환불 뺀 기준으로. 순위가 뒤집힌다."""
    ads = [(k, p / c, p * (1 - r) / c) for k, (p, c, r) in CHANNELS.items() if c]
    fig, ax = plt.subplots(figsize=(8.6, 3.6), dpi=150)
    y = range(len(ads))
    h = .34
    ax.barh([i - h / 2 for i in y], [a[1] for a in ads], height=h, color=GREY, zorder=3, label="결제액 기준")
    ax.barh([i + h / 2 for i in y], [a[2] for a in ads], height=h, color=HOT, zorder=3, label="환불 뺀 기준")
    for i, (_, g, n) in enumerate(ads):
        ax.text(g + .04, i - h / 2, "%.2f" % g, va="center", fontsize=10.5, color="#64748b")
        ax.text(n + .04, i + h / 2, "%.2f" % n, va="center", fontsize=10.5, color=HOT, fontweight="bold")
    ax.set_yticks(list(y), [a[0] for a in ads])
    ax.invert_yaxis()
    ax.set_xlim(0, 4.6)
    ax.set_xticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=11.5, colors=INK)
    ax.legend(loc="lower right", bbox_to_anchor=(1, 1.0), ncol=2, frameon=False, fontsize=10)
    ax.set_title("광고비 1원당 매출(ROAS)", fontsize=13, color=INK, pad=12, loc="left", fontweight="bold")
    fig.tight_layout(pad=1.2)
    p = os.path.join(OUT, "refund-channel.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def funnel_split():
    """11편 - 유입 경로별 전환율 변화(지난달 → 이번 달, %p). 합계는 0 인데 광고는 빠지고 재방문은 올랐다."""
    names = ["광고", "검색", "재방문", "합계"]
    diff = [-0.70, 0.00, 2.03, 0.00]
    color = [HOT, GREY, "#f59e0b", "#94a3b8"]
    fig, ax = plt.subplots(figsize=(8.6, 3.4), dpi=150)
    ax.barh(names, diff, color=color, height=.58, zorder=3)
    ax.invert_yaxis()
    ax.axvline(0, color="#94a3b8", lw=.9, zorder=4)
    for i, v in enumerate(diff):
        ax.text(v + (.08 if v >= 0 else -.08), i, "%+.2f%%p" % v if v else "변화 없음", va="center",
                ha="left" if v >= 0 else "right", fontsize=11,
                color=INK if i == 3 else color[i] if v else "#64748b", fontweight="bold" if v else "normal")
    ax.set_xlim(-1.4, 2.8)
    ax.set_xticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=11.5, colors=INK)
    ax.set_title("유입 경로별 전환율, 지난달 대비", fontsize=13, color=INK, pad=12, loc="left", fontweight="bold")
    fig.tight_layout(pad=1.2)
    p = os.path.join(OUT, "funnel-split.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


#: 13편 - 한 달 결제액이 영업이익까지 내려가는 길. 글의 표와 같은 숫자(만 원)
METRIC_MAP = [("결제액", 25000), ("환불", -1250), ("원가, 배송, 수수료", -13250),
              ("광고비", -4150), ("고정비", -5000)]


def metric_map():
    """13편 - 결제액에서 영업이익까지 폭포. 지표마다 이 길의 한 칸을 맡는다."""
    rows, run = [], 0
    for k, v in METRIC_MAP:
        rows.append((k, run if v > 0 else run + v, abs(v), v))
        run += v
    assert run == 1350, run
    rows.append(("영업이익", 0, run, run))
    fig, ax = plt.subplots(figsize=(8.6, 3.8), dpi=150)
    for i, (k, b, h, v) in enumerate(rows):
        c = HOT if i in (0, len(rows) - 1) else GREY
        ax.bar(i, h, bottom=b, color=c, width=.6, zorder=3)
        ax.text(i, b + h + 350, "{:,}".format(v) if v > 0 else "({:,})".format(-v),
                ha="center", fontsize=10.5, color=HOT if c == HOT else "#64748b",
                fontweight="bold" if c == HOT else "normal")
    ax.set_xticks(range(len(rows)), [r[0] for r in rows])
    ax.set_ylim(0, 28000)
    ax.set_yticks([])
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GREY)
    ax.tick_params(axis="x", length=0, labelsize=10.5, colors=INK)
    ax.set_title("한 달 결제액이 영업이익이 되기까지 (만 원)", fontsize=13, color=INK, pad=12, loc="left", fontweight="bold")
    fig.tight_layout(pad=1.2)
    p = os.path.join(OUT, "metric-map.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def save(fig, name):
    fig.tight_layout(pad=1.2)
    p = os.path.join(OUT, name)
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def plain(ax, title):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GREY)
    ax.tick_params(length=0, labelsize=10.5, colors=INK)
    ax.set_title(title, fontsize=13, color=INK, pad=12, loc="left", fontweight="bold")


def waterfall(rows, title, name, top=None, fmt="{:,}"):
    """(이름, 값) - 첫 줄은 출발점, 끝에 합계 막대. 출발과 끝만 색을 준다."""
    bars_, run = [], 0
    for i, (k, v) in enumerate(rows):
        bars_.append((k, run if i == 0 or v > 0 else run + v, abs(v), v))
        run += v
    bars_.append((name[1], min(0, run), abs(run), run))
    fig, ax = plt.subplots(figsize=(8.6, 3.8), dpi=150)
    span = max(abs(b[1]) + b[2] for b in bars_)
    for i, (k, b, h, v) in enumerate(bars_):
        c = HOT if i in (0, len(bars_) - 1) else GREY
        ax.bar(i, h, bottom=b if i else 0, color=c, width=.6, zorder=3)
        y = (b + h if v >= 0 else b) + span * (.03 if v >= 0 else -.03)
        ax.text(i, y, fmt.format(round(v, 2)) if v >= 0 else "(" + fmt.format(round(-v, 2)) + ")", ha="center",
                va="bottom" if v >= 0 else "top", fontsize=10.5,
                color=HOT if c == HOT else "#64748b", fontweight="bold" if c == HOT else "normal")
    ax.axhline(0, color="#94a3b8", lw=.9, zorder=4)
    ax.set_xticks(range(len(bars_)), [b[0] for b in bars_])
    ax.set_yticks([])
    if top:
        ax.set_ylim(*top)
    plain(ax, title)
    ax.spines["bottom"].set_visible(False)
    return save(fig, name[0])


def aov_trade():
    """14편 - 묶음 할인 · 무료배송 문턱을 올린 달, 평소 대비. 객단가는 올랐는데 남는 돈은 줄었다."""
    fig, ax = plt.subplots(figsize=(8.6, 3.4), dpi=150)
    bars(ax, ["객단가", "주문 수", "결제액", "남는 돈(공헌이익)"], [10.3, -9.0, 0.4, -11.1],
         lambda v: "%+.1f%%" % v, "프로모션 달, 평소 대비", "객단가는 10% 올랐는데 남는 돈은 11% 줄었다")
    return save(fig, "aov-trade.png")


def product_margin():
    """15편 - 상품 셋. 주문 수로 줄 세우면 리필이 1등, 남긴 돈으로 세우면 리필은 거의 0."""
    names = ["세트", "세럼", "리필"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 3.3), dpi=150)
    bars(a, names, [800, 1376, 1500], lambda v: "%s건" % format(int(v), ","),
         "주문 수", "가장 많이 팔린 것은 리필")
    bars(b, names, [4447, 5884, 169], lambda v: "%s만 원" % format(int(v), ","),
         "남긴 돈(공헌이익)", "가장 많이 남긴 것은 세럼")
    b.tick_params(labelleft=False)
    center_head(a)
    center_head(b)
    fig.tight_layout(pad=1.4, w_pad=4)
    x = (a.get_position().x1 + b.get_position().x0) / 2
    fig.add_artist(Line2D([x, x], [.04, .98], transform=fig.transFigure, color=GREY, lw=1, ls=(0, (4, 4))))
    p = os.path.join(OUT, "product-margin.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return p


def cac_ceiling():
    """17편 - 광고비를 늘릴 때 마지막 구간의 신규 고객 한 명값(한계 CAC)과 두 상한선."""
    spend = ["3,000→4,150", "4,150→5,000", "5,000→6,000"]
    marg = [24468, 33333, 45455]
    fig, ax = plt.subplots(figsize=(8.6, 3.9), dpi=150)
    x = range(len(spend))
    ax.axhline(28560, color="#94a3b8", lw=1.2, ls=(0, (4, 3)), zorder=2)
    ax.axhline(39984, color="#f59e0b", lw=1.2, ls=(0, (4, 3)), zorder=2)
    ax.text(-.35, 28560 + 700, "첫 주문이 남기는 돈 28,560원", ha="left", va="bottom", fontsize=10, color="#64748b")
    ax.text(-.35, 39984 + 700, "첫해 LTV 40,000원", ha="left", va="bottom", fontsize=10, color="#b45309")
    ax.plot(x, marg, color=HOT, lw=2.4, marker="o", ms=7, zorder=3)
    for i, v in enumerate(marg):
        ax.text(i, v - 1800, "{:,}원".format(v), ha="center", va="top", fontsize=10.5, color=HOT, fontweight="bold")
    ax.set_xticks(list(x), ["광고비 %s만 원" % s for s in spend])
    ax.set_xlim(-.4, 2.4)
    ax.set_ylim(15000, 50000)
    ax.set_yticks([])
    plain(ax, "광고비를 늘린 구간마다 신규 고객 한 명값")
    return save(fig, "cac-ceiling.png")


def repeat_curve():
    """18편 - 첫 구매 뒤 몇 달 안에 다시 샀나(누적). 12달에 25%."""
    m = [1, 2, 3, 6, 9, 12]
    r = [6, 10, 13, 18, 22, 25]
    fig, ax = plt.subplots(figsize=(8.6, 3.6), dpi=150)
    ax.plot(m, r, color=HOT, lw=2.4, marker="o", ms=6, zorder=3)
    for a, b in zip(m, r):
        ax.text(a, b + 1.2, "%d%%" % b, ha="center", va="bottom", fontsize=10.5,
                color=HOT if a == 12 else INK, fontweight="bold" if a == 12 else "normal")
    ax.set_xticks(m, ["%d개월" % a for a in m])
    ax.set_ylim(0, 31)
    ax.set_yticks([])
    plain(ax, "첫 구매 고객 중 다시 산 사람 (누적)")
    return save(fig, "repeat-curve.png")


def fee_creep():
    """19편 - 결제 수수료율 3.30% → 4.00%. 요율은 그대로인데 결제 수단이 옮겨 갔다."""
    return waterfall([("1년 전", 3.30), ("간편결제로\n옮겨 감", .24), ("해외 카드\n늘어남", .10), ("무이자 할부\n부담", .36)],
                     "결제액 대비 수수료율 (%)", ("fee-creep.png", "지금"), top=(0, 4.6), fmt="{:.2f}")


def normal_range():
    """20편 - 이번 달 지표가 평소 범위(지난 열두 달) 안에 있나. 범위를 0~1 로 펴서 나란히.
    수수료율은 1년 동안 천천히 올라 범위 끝을 살짝 넘을 뿐이다 - 작년 같은 달(3.3%)과 대야 보인다."""
    rows = [("전환율", 3.12, 2.88, 3.28, "%.2f%%"), ("객단가", 6.8, 6.4, 7.1, "%.1f만 원"),
            ("첫 달 환불율", 2.0, 1.7, 2.3, "%.1f%%"), ("공헌이익률", 42, 40, 44, "%d%%"),
            ("CAC", 1.77, 1.6, 1.95, "%.2f만 원"), ("결제 수수료율", 4.0, 3.55, 3.9, "%.1f%%")]
    fig, ax = plt.subplots(figsize=(8.6, 3.9), dpi=150)
    for i, (k, v, lo, hi, f) in enumerate(rows):
        pos = min((v - lo) / (hi - lo), 1.9)
        out = not 0 <= pos <= 1
        ax.add_patch(plt.Rectangle((0, i - .22), 1, .44, color="#e2e8f0", zorder=1, lw=0))
        ax.plot([pos], [i], marker="o", ms=9, color=HOT if out else "#64748b", zorder=3)
        ax.text(pos + .07, i, f % v, va="center", fontsize=10.5, color=HOT if out else INK,
                fontweight="bold" if out else "normal")
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(-.3, 2.5)
    ax.set_xticks([0, 1], ["평소 아래 끝", "평소 위 끝"])
    plain(ax, "이번 달, 평소 범위 안에 있나")
    return save(fig, "normal-range.png")


def ebitda_capex():
    """21편 - 영업이익이 같은 두 회사(1년, 만 원). B 는 물류센터를 지어 물류비가 상각으로 바뀌었다."""
    keys = ["영업이익", "EBITDA", "EBITDA - 설비 투자"]
    a = [16200, 18000, 16200]
    b = [16200, 39600, -70200]
    fig, ax = plt.subplots(figsize=(8.6, 3.9), dpi=150)
    y = range(len(keys))
    h = .34
    ax.barh([i - h / 2 for i in y], a, height=h, color=GREY, zorder=3, label="A 위탁 물류")
    ax.barh([i + h / 2 for i in y], b, height=h, color=HOT, zorder=3, label="B 자체 물류센터")
    for i in y:
        for v, off, c in ((a[i], -h / 2, "#64748b"), (b[i], h / 2, HOT)):
            ax.text(v + (2500 if v >= 0 else -2500), i + off, "{:,}".format(v) if v >= 0 else "({:,})".format(-v),
                    va="center", ha="left" if v >= 0 else "right", fontsize=10.5, color=c)
    ax.axvline(0, color="#94a3b8", lw=.9, zorder=4)
    ax.set_yticks(list(y), keys)
    ax.invert_yaxis()
    ax.set_xlim(-100000, 60000)
    ax.set_xticks([])
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0, labelsize=11, colors=INK)
    ax.legend(loc="lower right", bbox_to_anchor=(1, 1.0), ncol=2, frameon=False, fontsize=10)
    ax.set_title("1년 숫자 (만 원)", fontsize=13, color=INK, pad=12, loc="left", fontweight="bold")
    return save(fig, "ebitda-capex.png")


def ebitda_cash():
    """22편 - 성수기 앞 한 달. EBITDA 1,500 이 영업현금흐름 (1,100) 이 되기까지."""
    return waterfall([("EBITDA", 1500), ("재고", -2400), ("오픈마켓\n정산 대기", -900), ("외상 매입", 600),
                      ("선수금", 300), ("법인세", -200)],
                     "EBITDA 에서 영업현금흐름까지 (만 원)", ("ebitda-cash.png", "영업\n현금흐름"), top=(-2600, 1900))


ALL = [funnel_basic, funnel_gap, conv_trend, refund_lag, refund_cohort, refund_channel, funnel_split, metric_map,
       aov_trade, product_margin, cac_ceiling, repeat_curve, fee_creep, normal_range, ebitda_capex, ebitda_cash]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in ALL:
        p = f()
        print("%s  %.0f KB" % (os.path.basename(p), os.path.getsize(p) / 1024))
    if "--check" in sys.argv:
        assert plt.rcParams["font.family"][0] != "sans-serif", "한글 폰트를 못 찾았어요"
        print("ok")
