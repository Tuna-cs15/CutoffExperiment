"""Gộp các CUTOFF cho cùng cây đệ quy thành một nhóm, rồi so sánh theo nhóm.

Dùng: py src\analyze_groups.py <raw_csv> <thu_muc_ra>
"""
import sys
from collections import Counter
import numpy as np
import pandas as pd

RAW = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "."


def signature(n, c):
    cnt, level = Counter(), Counter({n: 1})
    while level:
        nxt = Counter()
        for s, k in level.items():
            if s <= 1 or s <= c:
                cnt[s] += k
            else:
                nxt[(s + 1) // 2] += k
                nxt[s // 2] += k
        level = nxt
    return tuple(sorted(cnt.items()))


df = pd.read_csv(RAW)
means = []
for (d, n, c), g in df.groupby(["distribution", "N", "cutoff"]):
    x = g.time_ms.to_numpy()
    q1, q3 = np.percentile(x, [25, 75]); iqr = q3 - q1
    k = x[(x >= q1 - 1.5 * iqr) & (x <= q3 + 1.5 * iqr)]
    means.append((d, n, c, k.mean()))
M = pd.DataFrame(means, columns=["distribution", "N", "cutoff", "mean_ms"])

rows = []
for (d, n), g in M.groupby(["distribution", "N"]):
    g = g.sort_values("cutoff")
    gid, prev, cur = {}, None, -1
    for c in g.cutoff:
        s = signature(int(n), int(c))
        if s != prev:
            cur += 1; prev = s
        gid[c] = cur
    g = g.assign(group=g.cutoff.map(gid))
    base = g[g.group == 0].mean_ms.median()
    for gr, h in g.groupby("group"):
        lo, hi = h.cutoff.min(), h.cutoff.max()
        rows.append(dict(distribution=d, N=n, group=f"{lo}-{hi}" if lo != hi else f"{lo}",
                         n_cutoffs=len(h), median_ms=h.mean_ms.median(),
                         min_ms=h.mean_ms.min(), max_ms=h.mean_ms.max(),
                         gain_pct=(base - h.mean_ms.median()) / base * 100))
G = pd.DataFrame(rows)
G.to_csv(f"{OUT}/group_summary.csv", index=False, float_format="%.4f")

pd.set_option("display.width", 200)
for (d, n), h in G.groupby(["distribution", "N"]):
    b = h.loc[h.median_ms.idxmin()]
    print(f"\n{d}  N={n}   nhom tot nhat: {b.group}  ({b.median_ms:.4f} ms, "
          f"cai thien {b.gain_pct:.1f}%)")
    print(h[["group", "n_cutoffs", "median_ms", "min_ms", "max_ms", "gain_pct"]]
          .round(4).to_string(index=False))