"""Gộp 3 lần khởi chạy JVM (raw_fork1..3.csv): trung vị của 3 trung bình fork."""
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = sys.argv[1] if len(sys.argv) > 1 else "results"
FILES = [f"{OUT}/raw_fork{i}.csv" for i in (1, 2, 3)]


def fork_means(path):
    d = pd.read_csv(path)
    rows = []
    for (dist, n, c), g in d.groupby(["distribution", "N", "cutoff"]):
        x = g.time_ms.to_numpy()
        q1, q3 = np.percentile(x, [25, 75]); iqr = q3 - q1
        k = x[(x >= q1 - 1.5 * iqr) & (x <= q3 + 1.5 * iqr)]
        rows.append((dist, n, c, k.mean()))
    return pd.DataFrame(rows, columns=["distribution", "N", "cutoff", "mean_ms"])


frames = []
for i, f in enumerate(FILES, 1):
    m = fork_means(f); m["fork"] = i; frames.append(m)
A = pd.concat(frames)
P = A.pivot_table(index=["distribution", "N", "cutoff"], columns="fork",
                  values="mean_ms").reset_index()
P["robust_ms"] = P[[1, 2, 3]].median(axis=1)
P["fork_min"] = P[[1, 2, 3]].min(axis=1)
P["fork_max"] = P[[1, 2, 3]].max(axis=1)
b0 = P[P.cutoff == 0].set_index(["distribution", "N"])["robust_ms"]
P["gain_pct"] = [(b0[(d, n)] - t) / b0[(d, n)] * 100
                 for d, n, t in zip(P.distribution, P.N, P.robust_ms)]
P.columns = [str(c) for c in P.columns]
P.rename(columns={"1": "fork1_ms", "2": "fork2_ms", "3": "fork3_ms"}).to_csv(
    f"{OUT}/robust_summary.csv", index=False, float_format="%.6f")

rows = []
for (d, n), g in P.groupby(["distribution", "N"]):
    g = g.sort_values("cutoff")
    best = g.loc[g.robust_ms.idxmin()]
    plateau = g[g.robust_ms <= best.robust_ms * 1.02]

    def gain(c):
        return float(g[g.cutoff == c].gain_pct.iloc[0])

    per_fork = [int(A[(A.distribution == d) & (A.N == n) & (A.fork == f)]
                    .sort_values("mean_ms").cutoff.iloc[0]) for f in (1, 2, 3)]
    rows.append(dict(distribution=d, N=n, best_cutoff=int(best.cutoff),
                     best_ms=best.robust_ms, gain_best_pct=best.gain_pct,
                     plateau_min=int(plateau.cutoff.min()),
                     plateau_max=int(plateau.cutoff.max()),
                     gain_at_7_pct=gain(7), gain_at_10_pct=gain(10),
                     gain_at_16_pct=gain(16), gain_at_30_pct=gain(30),
                     ms_at_cutoff0=b0[(d, n)],
                     argmin_fork1=per_fork[0], argmin_fork2=per_fork[1],
                     argmin_fork3=per_fork[2]))
O = pd.DataFrame(rows)
O.to_csv(f"{OUT}/robust_optimal.csv", index=False, float_format="%.4f")
print(O.round(2).to_string(index=False))

DISTS = ["RANDOM", "ASCENDING", "DESCENDING", "DUPLICATES"]
LABEL = {"RANDOM": "Ngẫu nhiên", "ASCENDING": "Tăng dần",
         "DESCENDING": "Giảm dần", "DUPLICATES": "Trùng lặp"}
SIZES = sorted(P.N.unique())

fig, axs = plt.subplots(2, 2, figsize=(11, 7.5))
for ax, n in zip(axs.ravel(), SIZES):
    g = P[(P.distribution == "RANDOM") & (P.N == n)].sort_values("cutoff")
    ax.fill_between(g.cutoff, g.fork_min, g.fork_max, alpha=.25, label="min–max giữa 3 JVM")
    ax.plot(g.cutoff, g.robust_ms, "o-", ms=3.5, lw=1.4, label="trung vị 3 JVM")
    r = O[(O.distribution == "RANDOM") & (O.N == n)].iloc[0]
    ax.axvspan(r.plateau_min, r.plateau_max, color="green", alpha=.08)
    ax.axvline(r.best_cutoff, color="red", ls="--", lw=1)
    ax.set_title(f"N = {n:,}  (tốt nhất: {int(r.best_cutoff)}; "
                 f"trong 2%: {int(r.plateau_min)}–{int(r.plateau_max)})", fontsize=10)
    ax.set_xlabel("CUTOFF"); ax.set_ylabel("Thời gian (ms)"); ax.grid(alpha=.3)
axs[0, 0].legend(fontsize=8)
fig.suptitle("Phân bố ngẫu nhiên — ước lượng vững từ 3 lần khởi chạy JVM")
fig.tight_layout(); fig.savefig(f"{OUT}/fig4_random_robust.png", dpi=150); plt.close(fig)

fig, axs = plt.subplots(2, 2, figsize=(11, 7.5))
for ax, n in zip(axs.ravel(), SIZES):
    for d in DISTS:
        g = P[(P.distribution == d) & (P.N == n)].sort_values("cutoff")
        ax.plot(g.cutoff, g.robust_ms / b0[(d, n)], marker="o", ms=3, lw=1.2, label=LABEL[d])
    ax.axhline(1, color="gray", lw=.8)
    ax.set_title(f"N = {n:,}"); ax.set_xlabel("CUTOFF")
    ax.set_ylabel("Thời gian / thời gian (CUTOFF=0)"); ax.grid(alpha=.3)
axs[0, 0].legend(fontsize=8)
fig.suptitle("Bốn dạng phân bố (trung vị 3 JVM, chuẩn hoá theo CUTOFF = 0)")
fig.tight_layout(); fig.savefig(f"{OUT}/fig5_distributions_robust.png", dpi=150); plt.close(fig)
print("OK")