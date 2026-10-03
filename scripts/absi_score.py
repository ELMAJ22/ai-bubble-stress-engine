"""Recompute the ABSI v0.1 score from the data files. Python 3, no extra packages.

Usage:  python scripts/absi_score.py
"""
import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
ORDER = ["V", "M", "S", "P", "E", "F", "I"]
NAMES = {"V": "Valuation", "M": "Capex / monetization", "S": "Supply vs demand",
         "P": "Profitability / cash flow", "E": "Market exuberance",
         "F": "Capital flow / financing", "I": "Physical infrastructure"}


def stress(r):
    """0-100 stress for one indicator: fixed judgment, or position between anchors."""
    if r["fixed"] is not None:
        return r["fixed"]
    return max(0.0, min(100.0, (r["raw"] - r["lo"]) / (r["hi"] - r["lo"]) * 100))


def component(rows, planned):
    """Group-average overlapping indicators, weight by confidence."""
    counts = {}
    for r in rows:
        counts[r["group"]] = counts.get(r["group"], 0) + 1
    num = den = conf_sum = 0.0
    for r in rows:
        w = (1 / counts[r["group"]]) * r["conf"]
        num += stress(r) * w
        den += w
        conf_sum += r["conf"]
    coverage = min(1.0, len(rows) / planned)
    return {"s": num / den, "conf": conf_sum / len(rows) * coverage, "n": len(rows)}


def composite(indicators, weights, planned):
    comps = {c: component([r for r in indicators if r["comp"] == c], planned[c])
             for c in ORDER if any(r["comp"] == c for r in indicators)}
    score = sum(comps[c]["s"] * weights[c] for c in comps) / sum(weights[c] for c in comps)
    conf = sum(comps[c]["conf"] * weights[c] for c in comps) / sum(weights.values())
    return score, conf, comps


def schemes(base):
    equal = {c: 100 / 7 for c in ORDER}
    half = dict(base)
    cut = base["V"] / 2
    half["V"] -= cut
    half["F"] += cut / 2
    half["I"] += cut / 2
    return {"Protocol weights": base, "Equal weights": equal, "Valuation halved": half}


def robustness(indicators, planned, n=1000, seed=42, judgment_jitter=0.0):
    """Re-score under n random weightings (flat Dirichlet, so every split of the
    100 weight points is equally likely). If judgment_jitter > 0, each judgment
    score is also shifted by a uniform random amount of up to +/- that many points.
    Returns sorted composite scores. Deterministic for a given seed."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        g = [rng.gammavariate(1.0, 1.0) for _ in ORDER]
        w = {c: 100 * x / sum(g) for c, x in zip(ORDER, g)}
        rows = []
        for r in indicators:
            r = dict(r)
            if judgment_jitter and r["fixed"] is not None:
                r["fixed"] = max(0.0, min(100.0, r["fixed"] + rng.uniform(-judgment_jitter, judgment_jitter)))
            rows.append(r)
        out.append(composite(rows, w, planned)[0])
    return sorted(out)


def pct(sorted_vals, q):
    return sorted_vals[int(round(q * (len(sorted_vals) - 1)))]


if __name__ == "__main__":
    ind = json.loads((DATA / "indicators_2026-10-02.json").read_text())
    cfg = json.loads((DATA / "config_v0.1.json").read_text())
    print(f"{cfg['version']}  data as of {cfg['asOf']}\n")
    for name, w in schemes(cfg["weights"]).items():
        score, conf, comps = composite(ind, w, cfg["planned"])
        print(f"{name:18s} stress {score:5.1f} / 100   confidence {conf*100:4.0f} / 100")
        if name == "Protocol weights":
            for c in ORDER:
                print(f"    {NAMES[c]:26s} {comps[c]['s']:5.1f}   (indicators: {comps[c]['n']})")
    print("\nRobustness: 1,000 random weightings of the seven components")
    for label, jit in (("weights only", 0.0), ("weights + judgment rows shifted up to +/-10 points", 10.0)):
        v = robustness(ind, cfg["planned"], judgment_jitter=jit)
        print(f"    {label}: 5th-95th percentile {pct(v, .05):.0f} to {pct(v, .95):.0f}, median {pct(v, .5):.0f}, min {v[0]:.0f}, max {v[-1]:.0f}")
    print("\nThis is a stress score, not a probability of a crash.")
