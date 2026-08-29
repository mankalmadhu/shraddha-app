# Antigravity / local converter

## 01-07 mantras

1. Copy the ṛk from Sanskrit Documents **Kannada 2-mark** (॒ and ॑ only).
2. Put it in `tools/input/<id>.kn.txt` using the template in that folder.
3. Run:

```
python3 tools/apply_dvisvarita.py tools/input/ps_01.kn.txt
```

4. Eyeball `unicode` and `dvisvarita_applied` in
   `data/kn/section-01/01-07-prayascitta.json`.
5. Acknowledge, commit, push. Grok then checks **᳚ placement only**
   against the household prayoga PDF.

## Rule

- `॑` on a dīrgha (ಾ ೀ ೂ ೇ ೈ ೋ ೌ / ಆ ಈ ಊ ಏ ಐ ಓ ಔ) → `᳚`
- `॑` on a syllable with `ಂ` or closed `ನ್` / `ರ್` → `᳚`
- short open `॑` stays `॑`
- first pāda ends `।` ; second ends `॥` + Kannada number
