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
            # Gentle warning for the user to hunt for Udatta/Svarita followed by half r/n
            if i + 2 < len(text) and text[i+1:i+3] in {"\u0cb0\u0ccd", "\u0ca8\u0ccd"}:
                print(f"👀 EYE-CHECK: Upper tick '॑' followed by half '{text[i+1:i+3]}' detected -> ...{text[max(0, i-6):min(len(text), i+8)]}...")
                
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

def extract_kannada_number(pada2: str):
    # match something like "೧೦.೦೯೦.೦೧" at the end (allowing some dots before)
    # Kannada digits are \u0ce6-\u0cef
    match = re.search(r'([\u0ce6-\u0cef\.]+)$', pada2.strip())
    if match:
        kannada_num_str = match.group(1).strip('.')
        # strip it from the pada
        pada_stripped = pada2[:match.start()].strip()
        pada_stripped = re.sub(r"[\.\u3002]+$", "", pada_stripped).strip()
        
        # translate to eng
        eng_num_str = kannada_num_str.translate(str.maketrans("\u0ce6\u0ce7\u0ce8\u0ce9\u0cea\u0ceb\u0cec\u0ced\u0cee\u0cef", "0123456789"))
        # split by . and strip leading zeros
        parts = []
        for p in eng_num_str.split('.'):
            if p:
                parts.append(str(int(p)))
        rv = ".".join(parts)
        return rv, pada_stripped
    return "", pada2

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
            
    base_id = fields.get("id", "rk")
    base_label = fields.get("label", base_id)
    
    # Strictly validate that the body contains only standard Unicode ranges and no English letters
    invalid_match = re.search(r'[^\u0C80-\u0CFF\u1CD0-\u1CFF\u0951\u0952\u0964\u0965\u0300-\u036F\u200C\u200D\s\.\,\-\!\?0-9\(\)\[\]\{\}\:\;\'\"]', body)
    if invalid_match:
        char = invalid_match.group(0)
        raise SystemExit(f"Error: Found illegal non-Unicode character in mantras: {repr(char)}. Please ensure input uses standard Kannada Unicode, not legacy ASCII fonts.")
    
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    
    riks = []
    seq = 1
    
    for i in range(0, len(lines), 2):
        if i + 1 >= len(lines):
            break
        pada1 = lines[i]
        pada2 = lines[i+1]
        
        rv, stripped_pada2 = extract_kannada_number(pada2)
        
        riks.append({
            "id": f"{base_id}_{seq:02d}",
            "label": f"{base_label} {seq}".translate(str.maketrans("0123456789", "\u0ce6\u0ce7\u0ce8\u0ce9\u0cea\u0ceb\u0cec\u0ced\u0cee\u0cef")),
            "rv": rv,
            "pada1": pada1,
            "pada2": stripped_pada2,
            "original_pada2": pada2,
            "number": seq
        })
        seq += 1
        
    return riks

def main():
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--json", type=Path, default=root / "data/kn/section-01/01-07-prayascitta.json")
    args = ap.parse_args()
    
    riks = parse_input(args.input.read_text(encoding="utf-8"))
    
    if args.json.exists():
        data = json.loads(args.json.read_text(encoding="utf-8"))
    else:
        # Auto-initialize an empty JSON structure if the output file doesn't exist yet
        data = {"mantras": []}
    
    existing = {m.get("id"): i for i, m in enumerate(data.get("mantras", []))}
    
    for spec in riks:
        u1, a1 = apply_dvisvarita(spec["pada1"])
        u2, a2 = apply_dvisvarita(spec["pada2"])
        unicode_out = normalize_danda(u1, u2, None)
        
        mantra = {
            "id": spec["id"], 
            "label": spec["label"], 
            "rv": spec["rv"],
            "accent_status": "converter_pass1",
            "two_mark_input": spec["pada1"] + "\n" + spec["original_pada2"],
            "dvisvarita_applied": a1 + a2,
            "unicode": unicode_out,
        }
        
        if spec["id"] in existing:
            data["mantras"][existing[spec["id"]]] = mantra
        else:
            data.setdefault("mantras", []).append(mantra)
            existing[spec["id"]] = len(data["mantras"]) - 1
            
        print(f"[{spec['id']}] {unicode_out.replace(chr(10), ' ')}")
        if a1 or a2:
            print(f"  applied: {', '.join(a1 + a2)}")
        
    args.json.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(riks)} riks to {args.json}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
