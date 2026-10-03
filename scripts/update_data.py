"""Daily ABSI update: fetch fresh public data, re-score, append a snapshot.

Usage:  python scripts/update_data.py

Sources (all free, no account needed):
  - Shiller CAPE:   http://www.econ.yale.edu/~shiller/data/ie_data.xls   (monthly)
  - US IG spread:   https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLC0A0CM  (daily)

If a source fails, the last known value is kept, the failure is recorded, and the
indicator's confidence is halved once the value is older than its stale limit.
The formula itself lives in absi_score.py and is not changed here.
"""
import csv
import datetime as dt
import io
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import absi_score as A  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UA = "Mozilla/5.0 (ABSI open research project; github.com/ELMAJ22/ai-bubble-stress-engine)"
SHILLER_URL = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
FRED_IG_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=BAMLC0A0CM"
START, END = "<!-- ABSI:START -->", "<!-- ABSI:END -->"


# ---------- fetching and parsing (pure functions are unit-tested) ----------

def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as f:
                return f.read()
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"fetch failed for {url}: {last}")


def parse_fred_csv(text):
    """Return (date, value) of the last non-missing observation in a FRED CSV."""
    rows = list(csv.reader(io.StringIO(text)))
    best = None
    for r in rows[1:]:
        if len(r) < 2:
            continue
        try:
            best = (r[0].strip(), float(r[1]))
        except ValueError:
            continue  # FRED marks missing days with "."
    if best is None:
        raise ValueError("no numeric observations in FRED CSV")
    return best


def parse_shiller_rows(rows):
    """Return ('YYYY-MM', cape) for the latest row of Shiller's 'Data' sheet.

    The date column is a float like 2026.1 (October 2026) or 2026.09 (September).
    """
    col = hdr = None
    for i, r in enumerate(rows[:20]):
        for j, cell in enumerate(r):
            if isinstance(cell, str) and "cape" in cell.lower():
                col, hdr = j, i
                break
        if col is not None:
            break
    if col is None:
        raise ValueError("CAPE column not found in Shiller sheet")
    best = None
    for r in rows[hdr + 1:]:
        if len(r) <= col:
            continue
        d, v = r[0], r[col]
        if isinstance(d, (int, float)) and isinstance(v, (int, float)) and v > 0:
            year = int(d)
            month = int(round((d - year) * 100))
            if 1 <= month <= 12:
                best = (f"{year}-{month:02d}", float(v))
    if best is None:
        raise ValueError("no CAPE values found")
    return best


def read_shiller():
    import xlrd  # imported here so the tests do not need it
    book = xlrd.open_workbook(file_contents=fetch(SHILLER_URL))
    sheet = book.sheet_by_name("Data")
    rows = [[c.value for c in sheet.row(i)] for i in range(sheet.nrows)]
    return parse_shiller_rows(rows)


# ---------- scoring ----------

def band(s):
    return "Low stress" if s < 35 else "Moderate stress" if s < 55 else "Elevated to high stress" if s < 75 else "Extreme stress"


def regime(score, comps):
    g = lambda c: comps[c]["s"] if c in comps else 0.0  # noqa: E731
    market, fund = (g("V") + g("E")) / 2, (g("S") + g("P")) / 2
    if score < 35:
        return "Fundamental expansion"
    if score >= 75:
        return "Bubble stress"
    if market >= 70 and fund < 50:
        return "Speculative expansion"
    if market >= 70:
        return "Fragility"
    return "Fundamental to speculative expansion"


def build_indicators(base, state, cfg, today):
    """Launch values (v0.1) overlaid with the latest automatic values."""
    stale = cfg["auto"]["stale_days"]
    rows = [dict(r) for r in base]
    flags = {}

    def age(key):
        return (today - dt.date.fromisoformat(state[key]["fetched"])).days

    if "cape" in state:
        for r in rows:
            if r["id"] == "cape":
                r["raw"] = state["cape"]["value"]
                if age("cape") > stale["cape"]:
                    r["conf"] = round(r["conf"] / 2, 4)
                    flags["cape"] = "stale"
    if "ig_oas" in state:
        r = dict(cfg["auto"]["ig_oas"], raw=state["ig_oas"]["value"], fixed=None)
        if age("ig_oas") > stale["ig_oas"]:
            r["conf"] = round(r["conf"] / 2, 4)
            flags["ig_oas"] = "stale"
        rows.append(r)
    return rows, flags


def score_all(rows, cfg):
    out = {}
    for name, w in A.schemes(cfg["weights"]).items():
        out[name] = A.composite(rows, w, cfg["planned"])
    return out


# ---------- outputs ----------

def render_block(date, version, results, n_ind, planned_total, flags, errors):
    score, conf, comps = results["Protocol weights"]
    lo = min(v[0] for v in results.values())
    hi = max(v[0] for v in results.values())
    lines = [START,
             f"## Current reading ({version}, data as of {date})", "",
             "| | |", "|---|---|",
             f"| **Composite stress** | **{score:.0f} / 100** ({band(score)}; {lo:.0f} to {hi:.0f} across three weighting schemes) |",
             f"| **Confidence** | **about {conf * 100:.0f} / 100** ({n_ind} of about {planned_total} planned indicators have data) |",
             f"| **Provisional regime** | {regime(score, comps)} |", "",
             "| Component | Stress (0-100) |", "|---|---|"]
    for c in sorted(comps, key=lambda c: -comps[c]["s"]):
        lines.append(f"| {A.NAMES[c]} | {comps[c]['s']:.0f} |")
    note = ""
    if flags:
        note += " Stale inputs: " + ", ".join(sorted(flags)) + "."
    if errors:
        note += " Last update had fetch problems: " + "; ".join(errors)[:300] + "."
    lines += ["", "This is a **stress score, not a probability of a crash.** Low confidence means the number is a rough position, not a measurement." + note, END]
    return "\n".join(lines)


def replace_block(readme, block):
    if START in readme and END in readme:
        pre, rest = readme.split(START, 1)
        _, post = rest.split(END, 1)
        return pre + block + post
    return readme


def write_snapshot(path, date, version, results):
    head = "date,version,composite_protocol,composite_equal,composite_valuation_halved,confidence"
    rows = {}
    if path.exists():
        for line in path.read_text().splitlines()[1:]:
            if line.strip():
                rows[line.split(",")[0]] = line
    p, e, h = (results[k] for k in ("Protocol weights", "Equal weights", "Valuation halved"))
    rows[date] = f"{date},{version},{p[0]:.1f},{e[0]:.1f},{h[0]:.1f},{p[1]:.2f}"
    path.write_text(head + "\n" + "\n".join(rows[k] for k in sorted(rows)) + "\n")


def run(today=None, data=DATA, readme_path=None):
    today = today or dt.date.today()
    readme_path = readme_path or (ROOT / "README.md")
    cfg = json.loads((data / "config_v0.2.json").read_text())
    base = json.loads((data / "indicators_2026-10-02.json").read_text())
    state_path = data / "auto_state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    errors = []

    for key, getter, label in (("cape", read_shiller, "Shiller CAPE"),
                               ("ig_oas", lambda: parse_fred_csv(fetch(FRED_IG_URL).decode("utf-8", "replace")), "FRED IG spread")):
        try:
            obs, value = getter()
            state[key] = {"value": value, "obs": obs, "fetched": today.isoformat(), "source": label}
            print(f"ok    {label}: {value} (observation {obs})")
        except Exception as e:  # noqa: BLE001
            errors.append(f"{label}: {str(e)[:120]}")
            print(f"FAIL  {label}: {e}")
    state_path.write_text(json.dumps(state, indent=2))

    rows, flags = build_indicators(base, state, cfg, today)
    results = score_all(rows, cfg)
    planned_total = sum(cfg["planned"].values())
    date = today.isoformat()
    write_snapshot(data / "snapshots.csv", date, cfg["version"], results)
    p = results["Protocol weights"]
    (data / "latest.json").write_text(json.dumps({
        "date": date, "version": cfg["version"], "composite": round(p[0], 2), "confidence": round(p[1], 4),
        "schemes": {k: round(v[0], 2) for k, v in results.items()},
        "components": {c: round(v["s"], 2) for c, v in p[2].items()},
        "indicators_used": len(rows), "stale": flags, "errors": errors,
    }, indent=2))
    if readme_path.exists():
        readme_path.write_text(replace_block(readme_path.read_text(), render_block(date, cfg["version"], results, len(rows), planned_total, flags, errors)))
    return results, errors


if __name__ == "__main__":
    _, errs = run()
    print("Done." + (" Some sources failed; kept last known values." if errs else ""))
