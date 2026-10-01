#!/usr/bin/env python3
"""Veroeffentlicht ein Levelpack fuer Dumpling Party (ST-484, ENT-722).

Legt ein vom Spiel-Repo gebautes Pack (tools/levelpack) unveraenderlich unter
dumpling-party/levels/levels-v<N>.json ab, traegt seine Pruefsumme in
dumpling-party/levels/SHA256SUMS ein (nur anhaengen) und setzt den Block
levelPack in dumpling-party/zeit.json. Eine vorhandene Version wird nie
ueberschrieben; die Nummer muss streng steigen.

    python3 scripts/levelpack_publish.py --pack <datei> --min-build <n> [--push]

Ohne --push wird nur lokal geschrieben und committet; mit --push auch
veroeffentlicht (GitHub Pages, etwa eine Minute).
"""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP = ROOT / "dumpling-party"
LEVELS = APP / "levels"
SUMS = LEVELS / "SHA256SUMS"
ZEIT = APP / "zeit.json"
NAME_RE = re.compile(r"^levels-v([0-9]+)\.json$")


def fail(msg):
    sys.exit(f"levelpack_publish: {msg}")


def read_sums():
    if not SUMS.exists():
        return []
    rows = []
    for line in SUMS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, name = line.split(None, 1)
        rows.append((digest, name.strip()))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--min-build", type=int, required=True)
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    raw = pathlib.Path(a.pack).read_bytes()
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        fail(f"Pack ist kein gueltiges UTF-8-JSON: {e}")
    for key in ("schemaVersion", "packVersion", "rules", "levels"):
        if key not in doc:
            fail(f"Pack ohne Feld {key}")
    version = doc["packVersion"]
    if not isinstance(version, int) or version < 1:
        fail(f"packVersion {version!r} ist keine Zahl >= 1")
    if not doc["levels"]:
        fail("Pack ohne Level")

    name = f"levels-v{version}.json"
    target = LEVELS / name
    sums = read_sums()
    known = {n for _, n in sums}
    if target.exists() or name in known:
        fail(f"{name} ist bereits veroeffentlicht und unveraenderlich; neue Nummer vergeben")
    highest = max((int(NAME_RE.match(n).group(1)) for n in known if NAME_RE.match(n)), default=0)
    if version <= highest:
        fail(f"packVersion {version} ist nicht groesser als die hoechste veroeffentlichte ({highest})")

    digest = hashlib.sha256(raw).hexdigest()
    LEVELS.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    with SUMS.open("a", encoding="utf-8") as f:
        f.write(f"{digest}  {name}\n")

    zeit = json.loads(ZEIT.read_text(encoding="utf-8"))
    zeit["levelPack"] = {
        "version": version,
        "path": f"levels/{name}",
        "sha256": digest,
        "rules": doc["rules"],
        "minBuild": a.min_build,
    }
    ZEIT.write_text(json.dumps(zeit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    paths = [str(p.relative_to(ROOT)) for p in (target, SUMS, ZEIT)]
    subprocess.run(["git", "add", "--", *paths], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", f"Dumpling Party: Levelpack v{version} veroeffentlichen", "--", *paths],
                   cwd=ROOT, check=True)
    if a.push:
        subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT, check=True)
    print(f"levels/{name} sha256={digest} minBuild={a.min_build} push={'ja' if a.push else 'nein'}")


if __name__ == "__main__":
    main()
