#!/usr/bin/env python3
"""Pruefungen der festen Adressen von Dumpling Party (ST-484, ST-485).

    python3 scripts/dumpling_check.py repo [--vorher <commit>]
        Ablage im Repo: jede Datei in dumpling-party/levels/SHA256SUMS existiert
        mit genau ihrer Pruefsumme, zeit.json zeigt auf eine eingetragene
        Version, und gegenueber <commit> wurde keine Zeile von SHA256SUMS
        geaendert oder entfernt (eine veroeffentlichte Packversion ist
        unveraenderlich).

    python3 scripts/dumpling_check.py live
        Erreichbarkeitsprobe: Status, Inhalt und Kopfzeilen aller festen
        Adressen unter https://sfr-services.de/dumpling-party/.

Exitcode 0 = in Ordnung, 1 = Fehler (jeder Fehler steht als eigene Zeile).
Nur Standardbibliothek, Python 3.9.
"""
import argparse
import email.utils
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
APP = ROOT / "dumpling-party"
SUMS = APP / "levels" / "SHA256SUMS"
BASE = "https://sfr-services.de/dumpling-party/"
PATH_RE = re.compile(r"^levels/levels-v([0-9]+)\.json$")
HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_sums(text):
    rows = []
    for line in text.splitlines():
        if line.strip():
            digest, name = line.split(None, 1)
            rows.append((digest, name.strip()))
    return rows


def check_level_pack_block(zeit, sums, errors, where):
    lp = zeit.get("levelPack")
    if lp is None:
        return
    for key, kind in (("version", int), ("path", str), ("sha256", str), ("rules", str), ("minBuild", int)):
        if not isinstance(lp.get(key), kind):
            errors.append(f"{where}: levelPack.{key} fehlt oder hat den falschen Typ")
            return
    m = PATH_RE.match(lp["path"])
    if not m or int(m.group(1)) != lp["version"]:
        errors.append(f"{where}: levelPack.path {lp['path']!r} passt nicht zu version {lp['version']}")
    if not HEX_RE.match(lp["sha256"]):
        errors.append(f"{where}: levelPack.sha256 ist kein 64-stelliges Hex")
    name = lp["path"].split("/", 1)[-1]
    if (lp["sha256"], name) not in sums:
        errors.append(f"{where}: levelPack zeigt auf {name} mit einer Pruefsumme, die nicht in SHA256SUMS steht")


def check_repo(before):
    errors = []
    sums = parse_sums(SUMS.read_text(encoding="utf-8")) if SUMS.exists() else []
    names = [n for _, n in sums]
    if len(names) != len(set(names)):
        errors.append("SHA256SUMS: eine Version steht doppelt")
    for digest, name in sums:
        f = APP / "levels" / name
        if not f.exists():
            errors.append(f"{name}: in SHA256SUMS, aber nicht im Repo")
        elif hashlib.sha256(f.read_bytes()).hexdigest() != digest:
            errors.append(f"{name}: Inhalt weicht von der eingetragenen Pruefsumme ab (ueberschrieben?)")
    for f in sorted((APP / "levels").glob("levels-v*.json")) if (APP / "levels").exists() else []:
        if f.name not in names:
            errors.append(f"{f.name}: liegt im Repo, fehlt aber in SHA256SUMS")
    zeit = json.loads((APP / "zeit.json").read_text(encoding="utf-8"))
    if zeit.get("schemaVersion") != 1:
        errors.append("zeit.json: schemaVersion ist nicht 1")
    check_level_pack_block(zeit, sums, errors, "zeit.json")
    if before and not re.fullmatch(r"0+", before):
        old = subprocess.run(["git", "show", f"{before}:dumpling-party/levels/SHA256SUMS"], cwd=ROOT,
                             capture_output=True, text=True)
        if old.returncode == 0:
            old_rows = parse_sums(old.stdout)
            if sums[:len(old_rows)] != old_rows:
                errors.append("SHA256SUMS: eine bereits veroeffentlichte Zeile wurde geaendert oder entfernt")
    return errors


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "dumpling-check/1", "Cache-Control": "no-cache"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, b""
    except (urllib.error.URLError, OSError) as e:
        return 0, {}, str(e).encode()


def check_live(extra=()):
    errors = []
    stamp = int(time.time())

    url = f"{BASE}zeit.json?probe={stamp}"
    status, head, body = fetch(url)
    zeit = None
    if status != 200:
        errors.append(f"zeit.json: Status {status} {body[:120]!r}")
    else:
        if not head.get("content-type", "").startswith("application/json"):
            errors.append(f"zeit.json: content-type {head.get('content-type')!r}")
        if "cache-control" not in head:
            errors.append("zeit.json: Kopfzeile cache-control fehlt")
        date = head.get("date")
        if not date:
            errors.append("zeit.json: Kopfzeile Date fehlt (die App liest daraus die Zeit)")
        else:
            skew = abs(email.utils.parsedate_to_datetime(date).timestamp() - time.time())
            if skew > 300:
                errors.append(f"zeit.json: Date weicht {skew:.0f} s von der Probenuhr ab")
        try:
            zeit = json.loads(body.decode("utf-8"))
            if zeit.get("schemaVersion") != 1:
                errors.append("zeit.json: schemaVersion ist nicht 1")
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            errors.append(f"zeit.json: kein gueltiges JSON ({e})")

    sums = parse_sums(SUMS.read_text(encoding="utf-8")) if SUMS.exists() else []
    if zeit is not None:
        check_level_pack_block(zeit, sums, errors, "zeit.json live")
    for digest, name in sums:
        status, head, body = fetch(f"{BASE}levels/{name}")
        if status != 200:
            errors.append(f"levels/{name}: Status {status}")
            continue
        if not head.get("content-type", "").startswith("application/json"):
            errors.append(f"levels/{name}: content-type {head.get('content-type')!r}")
        if hashlib.sha256(body).hexdigest() != digest:
            errors.append(f"levels/{name}: ausgelieferter Inhalt weicht von der Pruefsumme ab")

    status, head, body = fetch(f"{BASE}datenschutz.html")
    if status != 200:
        errors.append(f"datenschutz.html: Status {status}")
    else:
        if not head.get("content-type", "").startswith("text/html"):
            errors.append(f"datenschutz.html: content-type {head.get('content-type')!r}")
        if b"Dumpling Party" not in body:
            errors.append("datenschutz.html: Inhalt nennt Dumpling Party nicht")

    for path in extra:
        status, _, _ = fetch(f"{BASE}{path}")
        if status != 200:
            errors.append(f"{path}: Status {status}")

    checked = 2 + len(sums) + len(extra)
    return errors, checked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modus", choices=("repo", "live"))
    ap.add_argument("--vorher", default="")
    ap.add_argument("--zusatz", action="append", default=[],
                    help="weitere Pflichtadresse relativ zur Basis (Probe der Fehlermeldung)")
    a = ap.parse_args()
    if a.modus == "repo":
        errors, checked = check_repo(a.vorher), None
    else:
        errors, checked = check_live(a.zusatz)
    for e in errors:
        print(f"FEHLER {e}")
    if errors:
        sys.exit(1)
    print(f"OK {a.modus}" + (f" ({checked} Adressen)" if checked else ""))


if __name__ == "__main__":
    main()
