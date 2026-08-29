#!/usr/bin/env python3
"""Kannada 2-mark rk to vidwan dvisvarita + danda, write into section JSON."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
SVARITA = "\u0951"
ANUDATTA = "\u0952"
DVISVARITA = "\u1cda"
ANUSVARA = "\u0c82"
VIRAMA = "\u0ccd"
DIRGHA_SIGNS = set("\u0cbe\u0cc0\u0cc2\u0cc7\u0cc8\u0ccb\u0ccc")
VOWEL_SIGNS = set("\u0cbe\u0cbf\u0cc0\u0cc1\u0cc2\u0cc3\u0cc4\u0cc6\u0cc7\u0cc8\u0cca\u0ccb\u0ccc")
DIRGHA_INDEPENDENT = set("\u0c86\u0c88\u0c8a\u0c8f\u0c90\u0c93\u0c94")
CLOSED_FINAL = set("\u0ca8\u0cb0")

def _is_mark(ch: str) -> bool:
    return ch in {SVARITA, ANUDATTA, DVISVARITA} or ("\u0300" <= ch <= "\u036f")

def _cluster_before(text: str, mark_index: int) -> str:
    i = mark_index - 1
    while i >= 0 and _is_mark(text[i]):
        i -= 1
    if i < 0:
        return ""
    end = i + 1
    if text[i] in {ANUSVARA, "\u0c83"}:
        i -= 1
    if i >= 0 and text[i] in VOWEL_SIGNS:
        i -= 1
    while i >= 0:
        if text[i] == VIRAMA and i >= 1:
            i -= 2
            continue
        o = ord(text[i])
        if 0x0C85 <= o <= 0x0CB9:
            i -= 1
            if i >= 0 and text[i] == VIRAMA:
                i -= 1
                continue
            break
        break
    return text[i + 1 : end]

def _is_heavy(cluster: str) -> bool:
    if not cluster:
        return False
    if ANUSVARA in cluster:
        return True
    if cluster.endswith(VIRAMA) and len(cluster) >= 2 and cluster[-2] in CLOSED_FINAL:
        return True
    if any(ch in DIRGHA_SIGNS for ch in cluster):
        return True
    if cluster[0] in DIRGHA_INDEPENDENT:
        return True
    return False

def apply_dvisvarita(text: str):
    out, applied = [], []
    i = 0
    while i < len(text):
        if text[i] == SVARITA:
            cl = _cluster_before(text, i)
            if _is_heavy(cl):
                out.append(DVISVARITA)
                applied.append(cl + SVARITA)
            else:
                out.append(SVARITA)
            i += 1
        else:
            out.append(text[i]); i += 1
    return "".join(out), applied

def normalize_danda(pada1, pada2, number):
    def strip_end(s):
        s = s.strip()
        s = re.sub(r"[\.\u3002]+$", "", s)
        return s.rstrip("\u0964\u0965 ").rstrip()
    a, b = strip_end(pada1), strip_end(pada2)
    num = ""
    if number is not None:
        num = " " + str(number).translate(str.maketrans("0123456789", "\u0ce6\u0ce7\u0ce8\u0ce9\u0cea\u0ceb\u0cec\u0ced\u0cee\u0cef"))
    return f"{a}\u0964\n{b}\u0965{num}"

def parse_input(raw):
    raw = raw.strip()
    if not raw:
        raise SystemExit("empty input")
    meta, _, body = raw.partition("---")
    fields = {}
    for line in meta.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    if len(lines) < 2:
        raise SystemExit("need two padas after ---")
    return {
        "id": fields.get("id", "rk"),
        "rv": fields.get("rv", ""),
        "label": fields.get("label", fields.get("id", "rk")),
        "pada1": lines[0],
        "pada2": lines[1],
        "number": int(fields["n"]) if fields.get("n") else None,
    }

def main():
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--json", type=Path, default=root / "data/kn/section-01/01-07-prayascitta.json")
    args = ap.parse_args()
    spec = parse_input(args.input.read_text(encoding="utf-8"))
    n = spec["number"]
    if n is None and spec["rv"]:
        n = int(spec["rv"].rsplit(".", 1)[-1])
    u1, a1 = apply_dvisvarita(spec["pada1"])
    u2, a2 = apply_dvisvarita(spec["pada2"])
    unicode_out = normalize_danda(u1, u2, n)
    data = json.loads(args.json.read_text(encoding="utf-8"))
    mantra = {
        "id": spec["id"], "label": spec["label"], "rv": spec["rv"],
        "accent_status": "converter_pass1",
        "two_mark_input": spec["pada1"] + "\n" + spec["pada2"],
        "dvisvarita_applied": a1 + a2,
        "unicode": unicode_out,
    }
    existing = {m.get("id"): i for i, m in enumerate(data.get("mantras", []))}
    if spec["id"] in existing:
        data["mantras"][existing[spec["id"]]] = mantra
    else:
        data.setdefault("mantras", []).append(mantra)
    args.json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(unicode_out)
    print("applied:", ", ".join(a1 + a2) or "(none)")
    print("wrote", args.json)
    return 0

if __name__ == "__main__":
    sys.exit(main())
