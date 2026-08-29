# Antigravity / local converter

## 01-07 mantras

1. Copy the rks from Sanskrit Documents **Kannada 2-mark**.
2. Put them in `tools/input/<id>.txt`. A single file can contain multiple rks.
3. Run:

```
python3 tools/apply_dvisvarita.py tools/input/ps.txt
```

4. Eyeball `unicode` and `dvisvarita_applied` in
   `data/kn/section-01/01-07-prayascitta.json`.
5. Acknowledge, commit, push. Grok then checks **dvisvarita placement only**
   against the household prayoga PDF.

## Rules

### Accent Rules
- svarita on a dirgha → dvisvarita
- svarita on a syllable with anusvara or closed n / r → dvisvarita
- short open svarita stays svarita

### Pada and Numbering Rules
- 2 padas make one rk.
- First pada ends with single danda.
- Second pada ends with double danda only. No serial after the danda.
- Sequence lives in `label` and `id`.
- Input may end the second pada with a citation like 10.90.1 in Kannada digits. That becomes `rv` only. It is stripped from `unicode`.
