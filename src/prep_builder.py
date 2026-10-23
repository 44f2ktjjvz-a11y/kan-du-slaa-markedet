"""Saml data til porteføljebyggeren: månedlige afkast 2001-01 til seneste måned.

Aktier = MSCI ACWI Net TR i DKK, obligationer = Bloomberg Global Aggregate afdækket (fra returns.json),
sektorer = MSCI ACWI-sektorindeks Net TR i DKK (sectors_raw.json), vægte = nuværende markedsværdi pr. sektor.
Ejendomme (RL) har kun historik fra 2016 og holdes fast på benchmarkvægt, så den udelades her.
"""
import json, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
ret = json.loads((root / "data" / "returns.json").read_text(encoding="utf-8"))
raw = json.loads((root / "data" / "sectors_raw.json").read_text(encoding="utf-8"))
w = json.loads((root / "data" / "sector_weights.json").read_text(encoding="utf-8"))
NAMES = {"IT": "IT", "FN": "Finans", "IN": "Industri", "CD": "Cyklisk forbrug", "HC": "Sundhed",
         "TC": "Kommunikation", "EN": "Energi", "CS": "Stabilt forbrug", "MT": "Materialer", "UT": "Forsyning"}
codes = list(NAMES)
lvl = {c: {m: v for m, v in raw[c] if v is not None} for c in codes}
eqbd = {m: (e, b) for m, e, b in ret["monthly"]}
months = sorted(m for m in eqbd if m >= "2001-01")
rows = []
for i, m in enumerate(months):
    prev = f"{int(m[:4]) - (m[5:] == '01')}-{12 if m[5:] == '01' else int(m[5:]) - 1:02d}"
    e, b = eqbd[m]
    sec = [round(lvl[c][m] / lvl[c][prev] - 1, 5) for c in codes]
    rows.append([m, round(e, 5), round(b, 5), *sec])
out = {"months": rows, "sectors": [{"code": c, "name": NAMES[c], "w": w[c]} for c in codes],
       "w_other": w["RL"], "asof": months[-1],
       "source": "Bloomberg: MSCI ACWI og sektorindeks Net TR i DKK; Bloomberg Global Aggregate valutaafdækket"}
(root / "data" / "builder.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
# kontrol: vægtet sum af sektorer ≈ ACWI
import statistics as st
diff = [r[1] - (sum(s["w"] * x for s, x in zip(out["sectors"], r[3:])) + w["RL"] * r[1]) for r in rows]
print(len(rows), rows[0][0], rows[-1][0], "gns. |ACWI - vægtet sektor|:", round(st.mean(abs(x) for x in diff) * 100, 3), "% pr. md")
