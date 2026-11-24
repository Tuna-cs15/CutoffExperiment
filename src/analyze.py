import sys
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW = sys.argv[1] if len(sys.argv) > 1 else "results/raw_benchmark.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "results"

df = pd.read_csv(RAW)
rows = []
for (dist, n, c), g in df.groupby(["distribution", "N", "cutoff"]):
    x = g["time_ms"].to_numpy()
    q1, q3 = np.percentile(x, [25, 75]); iqr = q3 - q1
    k = x[(x >= q1 - 1.5 * iqr) & (x <= q3 + 1.5 * iqr)]
    m = len(k); mean = k.mean(); sd = k.std(ddof=1)
    half = stats.t.ppf(0.975, m - 1) * sd / np.sqrt(m)
    rows.append(dict(distribution=dist, N=n, cutoff=c, kept=m, mean_ms=mean,
                     median_ms=float(np.median(k)), std_ms=sd, ci95_half=half))
S = pd.DataFrame(rows).sort_values(["distribution", "N", "cutoff"]).reset_index(drop=True)
base = S[S.cutoff == 0].set_index(["distribution", "N"])["mean_ms"]
S["gain_vs_cutoff0_pct"] = [(base[(d, n)] - t) / base[(d, n)] * 100
                            for d, n, t in zip(S.distribution, S.N, S.mean_ms)]
S.to_csv(f"{OUT}/summary_statistics.csv", index=False)

opt = S.loc[S.groupby(["distribution", "N"]).mean_ms.idxmin(),
            ["distribution", "N", "cutoff", "mean_ms", "gain_vs_cutoff0_pct"]]
opt.to_csv(f"{OUT}/optimal_cutoff.csv", index=False)
print(opt.to_string(index=False))

for d in ["RANDOM", "ASCENDING", "DESCENDING", "DUPLICATES"]:
    fig, axs = plt.subplots(2, 2, figsize=(11, 7.5))
    for ax, n in zip(axs.ravel(), sorted(S.N.unique())):
        g = S[(S.distribution == d) & (S.N == n)]
        ax.errorbar(g.cutoff, g.mean_ms, yerr=g.ci95_half, fmt="o-", ms=3.5, capsize=2)
        ax.set_title(f"{d}, N = {n:,}")
        ax.set_xlabel("CUTOFF"); ax.set_ylabel("Thoi gian trung binh (ms)")
        ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(f"{OUT}/fig_{d.lower()}.png", dpi=150); plt.close(fig)