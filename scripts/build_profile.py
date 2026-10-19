"""Regenerate the SVG widgets used by README.md from live GitHub data.

Stdlib only. Token: GITHUB_TOKEN / GH_TOKEN, falling back to `gh auth token`.
Run from anywhere: python scripts/build_profile.py
"""
import json
import os
import subprocess
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

LOGIN = "k0te1ch"
FEATURED = ["PodBoxBot", "Timetable-bot", "powerpeek", "DialogEngine"]
FALLBACK_DESC = {
    "PodBoxBot": "Telegram bot in Python.",
    "Timetable-bot": "Class schedule and notifications for Voronezh State University.",
    "powerpeek": "Device battery in the Windows tray. One 4 MB exe, no installer, no telemetry.",
    "DialogEngine": "Lightweight dialog engine for form-driven Telegram bots.",
}
LANG_COLORS = {
    "Python": "#3572A5", "Java": "#b07219", "C++": "#f34b7d", "Dart": "#00B4AB",
    "JavaScript": "#f1e05a",
}
ACCENT = "#6366F1"
FONT = "JetBrains Mono, Consolas, monospace"
OUT = Path(__file__).resolve().parent.parent / "assets"

THEMES = {
    "dark": dict(bg="#0d0d16", card="#11111b", bar="#181826", line="#2a2a44", dot="#3a3a55",
                 text="#d4d4e0", muted="#8b8ba3", soft="#a8a8bd", head="#f4f4fb",
                 head2="#a5b4fc", accent=ACCENT, grid_op="0.07", glow_op="0.35",
                 cells=["#1a1a2b", "#2c2d6b", "#4547b8", "#6366F1", "#a5b4fc"]),
    "light": dict(bg="#f6f6fb", card="#ffffff", bar="#ececf6", line="#d4d4e6", dot="#c3c3d9",
                  text="#2a2a3c", muted="#6b6b85", soft="#50506a", head="#14142b",
                  head2="#4f46e5", accent="#4f46e5", grid_op="0.08", glow_op="0.18",
                  cells=["#ececf6", "#c7c9f7", "#9a9df0", "#6366F1", "#3730a3"]),
}

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection { contributionCalendar {
      totalContributions weeks { contributionDays { contributionCount date } } } }
    repositories(first: 100, privacy: PUBLIC, ownerAffiliations: OWNER,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes { name description pushedAt isFork isArchived primaryLanguage { name }
              releases(first: 1, orderBy: {field: CREATED_AT, direction: DESC}) {
                totalCount nodes { tagName publishedAt } }
              defaultBranchRef { target { ... on Commit { history { totalCount } } } } }
    }
  }
}
"""


def token():
    t = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    return t or subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def fetch():
    body = json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", body,
        {"Authorization": f"bearer {token()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def commits(repo):
    ref = repo["defaultBranchRef"]
    return ref["target"]["history"]["totalCount"] if ref else 0


def ago(iso):
    days = (datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    if days < 1:
        return "today"
    if days < 31:
        return f"{days}d ago"
    return f"{days // 30}mo ago" if days < 365 else f"{days // 365}y ago"


def text(x, y, s, fill, size=14, weight=400):
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{FONT}" font-size="{size}" '
            f'font-weight="{weight}">{escape(s)}</text>')


def banner(t):
    def line(begin, body):
        return (f'<g opacity="0"><animate attributeName="opacity" to="1" begin="{begin}s" '
                f'dur="0.3s" fill="freeze"/>{body}</g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="880" height="320" viewBox="0 0 880 320" role="img" aria-label="k0te1ch: Backend Engineer and System Designer">
<defs>
<radialGradient id="glow" cx="85%" cy="0%" r="70%"><stop offset="0" stop-color="{t['accent']}" stop-opacity="{t['glow_op']}"/><stop offset="1" stop-color="{t['accent']}" stop-opacity="0"/></radialGradient>
<linearGradient id="title" x1="0" x2="1"><stop offset="0" stop-color="{t['head']}"/><stop offset="1" stop-color="{t['head2']}"/></linearGradient>
<pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="{t['accent']}" stroke-opacity="{t['grid_op']}"/></pattern>
<clipPath id="card"><rect width="880" height="320" rx="12"/></clipPath>
</defs>
<g clip-path="url(#card)"><rect width="880" height="320" fill="{t['bg']}"/><rect width="880" height="320" fill="url(#grid)"/><rect width="880" height="320" fill="url(#glow)"/><rect width="880" height="40" fill="{t['bar']}"/><line x1="0" y1="40" x2="880" y2="40" stroke="{t['line']}"/></g>
<rect x="0.5" y="0.5" width="879" height="319" rx="12" fill="none" stroke="{t['line']}"/>
<circle cx="24" cy="20" r="6" fill="{t['dot']}"/><circle cx="44" cy="20" r="6" fill="{t['dot']}"/><circle cx="64" cy="20" r="6" fill="{t['accent']}"/>
{text(88, 25, "k0te1ch@github: ~", t['muted'], 12)}
{line(0.3, text(32, 86, "$", t['accent'], 16) + text(52, 86, "whoami", t['text'], 16))}
{line(0.9, text(32, 140, "Backend Engineer", "url(#title)", 38, 700) + text(32, 184, "& System Designer", "url(#title)", 38, 700))}
{line(1.6, text(32, 218, "Backend systems built for scalability and real-world impact.", t['soft'], 16))}
{line(2.2, text(32, 268, "$", t['accent'], 16) + text(52, 268, "echo $FOCUS", t['text'], 16) + text(32, 294, "architecture · performance · monetization", t['muted'], 16))}
</svg>
"""


def projects(t, repos):
    by_name = {r["name"]: r for r in repos}
    cards = []
    for i, name in enumerate(FEATURED):
        r = by_name.get(name)
        if not r:
            continue
        x, y = (i % 2) * 445, (i // 2) * 175
        lang = (r["primaryLanguage"] or {}).get("name", "")
        meta = f"{commits(r)} commits"
        if r["releases"]["totalCount"]:
            meta += f" · {r['releases']['totalCount']} releases"
        desc = (r["description"] or "").strip() or FALLBACK_DESC.get(name, "")
        words, rows = desc.split(), [""]
        for w in words:
            if len(rows[-1]) + len(w) + 1 > 38 and rows[-1]:
                rows.append("")
            rows[-1] = f"{rows[-1]} {w}".strip()
        if len(rows) > 2:
            rows = [rows[0], rows[1].rstrip(" .,") + "…"]
        body = "".join(text(24, 72 + 22 * j, row, t["soft"], 14) for j, row in enumerate(rows))
        cards.append(
            f'<g transform="translate({x} {y})">'
            f'<rect x="0.5" y="0.5" width="434" height="154" rx="10" fill="{t["card"]}" stroke="{t["line"]}"/>'
            f'<rect x="1" y="1" width="433" height="3" rx="1.5" fill="url(#edge)"/>'
            f'{text(24, 44, name, t["head"], 19, 700)}{body}'
            f'<circle cx="28" cy="128" r="5" fill="{LANG_COLORS.get(lang, t["muted"])}"/>'
            f'{text(42, 132, lang, t["head2"], 12, 600)}'
            f'{text(42 + 10 * len(lang) + 14, 132, meta, t["muted"], 12)}</g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="880" height="330" viewBox="0 0 880 330" role="img" aria-label="Featured projects">'
            f'<defs><linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{t["accent"]}"/>'
            f'<stop offset="1" stop-color="{t["accent"]}" stop-opacity="0"/></linearGradient></defs>'
            + "".join(cards) + "</svg>\n")


def languages(t, repos):
    own = [r for r in repos if not r["isFork"] and r["primaryLanguage"]]
    counts = Counter(r["primaryLanguage"]["name"] for r in own).most_common()
    total = sum(n for _, n in counts)
    bars, legend, x, lx = [], [], 0.0, 0
    for name, n in counts:
        w = 880 * n / total
        color = LANG_COLORS.get(name, t["muted"])
        bars.append(f'<rect x="{x:.1f}" y="26" width="{w:.1f}" height="14" fill="{color}"/>')
        label = f"{name} {round(100 * n / total)}%"
        legend.append(f'<circle cx="{lx + 6}" cy="68" r="5" fill="{color}"/>{text(lx + 18, 72, label, t["soft"], 12)}')
        x += w
        lx += 18 + 8 * len(label) + 24
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="880" height="96" viewBox="0 0 880 96" role="img" aria-label="Languages across public repositories">'
            f'{text(0, 14, "languages / public repos", t["accent"], 13, 600)}'
            f'<clipPath id="bar"><rect x="0" y="26" width="880" height="14" rx="7"/></clipPath>'
            f'<g clip-path="url(#bar)">{"".join(bars)}</g>{"".join(legend)}</svg>\n')


def activity(t, user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    peak = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=1) or 1
    cell, gap = 13, 3
    width = len(weeks) * (cell + gap) - gap
    rects = []
    for wi, w in enumerate(weeks):
        for di, d in enumerate(w["contributionDays"]):
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / peak))
            rects.append(f'<rect x="{wi * (cell + gap)}" y="{di * (cell + gap)}" width="{cell}" height="{cell}" rx="3" fill="{t["cells"][lvl]}"/>')
    sx = 880 / width if width > 880 else 1
    h = 7 * (cell + gap) - gap
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{int(h * sx) + 48}" viewBox="0 0 880 {int(h * sx) + 48}" role="img" aria-label="Contributions over the last year">'
            f'{text(0, 14, f"activity / {cal['totalContributions']} contributions in the last year", t["accent"], 13, 600)}'
            f'<g transform="translate(0 32) scale({sx:.4f})">{"".join(rects)}</g></svg>\n')


def now(t, repos):
    mine = [r for r in repos if not r["isFork"] and r["name"] != LOGIN][:3]
    rel = [(r["name"], r["releases"]["nodes"][0]) for r in repos if r["releases"]["nodes"]]
    rel.sort(key=lambda x: x[1]["publishedAt"], reverse=True)
    rows = [("$", "git log --recent", t["text"])]
    rows += [("→", f"{r['name']:<18} pushed {ago(r['pushedAt'])}", t["soft"]) for r in mine]
    if rel:
        n, rr = rel[0]
        rows += [("$", "gh release list --latest", t["text"]),
                 ("→", f"{n} {rr['tagName']}  {ago(rr['publishedAt'])}", t["soft"])]
    h = 56 + 26 * len(rows)
    body = "".join(
        text(24, 66 + 26 * i, sym, t["accent"], 14) + text(46, 66 + 26 * i, s, c, 14)
        for i, (sym, s, c) in enumerate(rows))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{h}" viewBox="0 0 880 {h}" role="img" aria-label="Recent activity">'
            f'<rect x="0.5" y="0.5" width="879" height="{h - 1}" rx="10" fill="{t["card"]}" stroke="{t["line"]}"/>'
            f'<rect x="0.5" y="0.5" width="879" height="34" rx="10" fill="{t["bar"]}"/>'
            f'{text(24, 22, "now.log", t["muted"], 12)}{body}</svg>\n')


def main():
    user = fetch()
    repos = user["repositories"]["nodes"]
    OUT.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        for stem, svg in (("banner", banner(t)), ("projects", projects(t, repos)),
                          ("languages", languages(t, repos)), ("activity", activity(t, user)),
                          ("now", now(t, repos))):
            (OUT / f"{stem}-{name}.svg").write_text(svg, encoding="utf-8", newline="\n")
    print("generated", len(THEMES) * 5, "files in", OUT)


if __name__ == "__main__":
    main()
