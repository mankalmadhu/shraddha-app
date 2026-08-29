# Antigravity / local converter

## 01-07 mantras

1. Copy the ṛks from Sanskrit Documents **Kannada 2-mark** (॒ and ॑ only).
2. Put them in `tools/input/<id>.txt` using the template in that folder. A single file can contain multiple ṛks.
3. Run:

```
python3 tools/apply_dvisvarita.py tools/input/ps.txt
```

4. Eyeball `unicode` and `dvisvarita_applied` in
   `data/kn/section-01/01-07-prayascitta.json`.
5. Acknowledge, commit, push. Grok then checks **᳚ placement only**
   against the household prayoga PDF.

## Rules

### Accent Rules
- `॑` on a dīrgha (ಾ ೀ ೂ ೇ ೈ ೋ ೌ / ಆ ಈ ಊ ಏ ಐ ಓ ಔ) → `᳚`
- `॑` on a syllable with `ಂ` or closed `ನ್` / `ರ್` → `᳚`
- short open `॑` stays `॑`

### Pāda and Numbering Rules
- 2 pādas make one ṛk.
- First pāda ends with `।`
- Second pāda ends with `॥` + sequential Kannada number (e.g., `॥ ೧`, `॥ ೨`).
- The input text will contain the ṛk number at the end of the second pāda in Kannada numerals, enclosed in brackets or dots (e.g., `೧೦.೦೯೦.೦೧`). This is strictly for generating the `rv` property in the JSON output (e.g. `10.90.1`), and is *not* included in the `unicode` property.
- The `id` (e.g., `ps_01`) and `label` (e.g., `ಪುರುಷಸೂಕ್ತ ೧`) should be generated dynamically based on the sequential ṛk number being processed.
