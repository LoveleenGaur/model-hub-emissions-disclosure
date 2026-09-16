import json, re, pathlib, difflib
from collections import Counter
import pandas as pd, numpy as np
from scipy import stats

import os
# Point at the unzipped data/hf_gov_cache_export.zip, or set HF_GOV_CACHE.
CACHE = pathlib.Path(os.environ.get("HF_GOV_CACHE", "cache"))
if not (CACHE / "models.jsonl").exists():
    raise SystemExit(f"No models.jsonl under {CACHE.resolve()}. "
                     "Unzip data/hf_gov_cache_export.zip there, or set HF_GOV_CACHE.")
models = {json.loads(l)["id"]: json.loads(l) for l in open(CACHE/"models.jsonl", encoding="utf-8")}
rd = {json.loads(l)["id"]: json.loads(l) for l in open(CACHE/"readmes.jsonl", encoding="utf-8")}
FRONT = re.compile(r"^---\s*\r?\n.*?\r?\n---\s*\r?\n", re.DOTALL)
NUM = r"[0-9][0-9,.]*\s*"

QUANT = {
 "co2":     rf"{NUM}(kg|g|t|tonnes?|tons?|lbs?)\s*(of\s+)?(co2|co\u2082|carbon)",
 "energy":  rf"{NUM}(kwh|kw\u00b7h|mwh|gwh|kilowatt[- ]hours?|joules?)\b",
 "power":   rf"(?:tdp|power (?:draw|consumption)|rated)[^.\n]{{0,40}}?{NUM}k?W\b|{NUM}k?W\b[^.\n]{{0,25}}?(?:tdp|power draw)",
 "compute": rf"{NUM}(?:m\s*)?(gpu|tpu|a100|h100|v100)[- ]?hours?|{NUM}hours?\s+of\s+(?:training|compute)",
}
MENTION = {
 "co2_nonum":   r"\b(carbon footprint|carbon emission|co2|co\u2082|greenhouse)\b",
 "perf_watt":   r"\btokens?\s*/\s*watt\b|\btokens? per watt\b|\bperf(ormance)?\s*/\s*watt\b",
 "eff_claim":   r"\b(more efficient|energy[- ]efficient|lower memory|less vram|runs on (a )?(cpu|laptop|phone)|smaller footprint)\b",
}
EFF_TAGS = {"gguf","onnx","awq","gptq","quantized","4-bit","8-bit","bitsandbytes","mlx",
            "openvino","tensorrt","exl2","quantization"}

rows = []
for mid, m in models.items():
    r = rd.get(mid)
    if not r or not r.get("readme"): continue
    body = FRONT.sub("", r["readme"], count=1)
    rec = {"id": mid, "org": mid.split("/")[0], "downloads": m.get("downloads") or 0,
           "compression": bool({t.lower() for t in (m.get("tags") or [])} & EFF_TAGS),
           "body": body}
    for k, p in {**QUANT, **MENTION}.items():
        rec[k] = bool(re.search(p, body, re.I))
    rows.append(rec)
d = pd.DataFrame(rows); N = len(d)
d["any_quantity"] = d[list(QUANT)].any(axis=1)

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    ph=k/n; dd=1+z*z/n; c=(ph+z*z/(2*n))/dd
    h=z*np.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/dd
    return round(max(0,c-h)*100,2), round((c+h)*100,2)

def families(sub, thresh=0.85):
    ids=list(sub.id)
    if len(ids)<2: return len(ids)
    txt=dict(zip(sub.id, sub.body.str[:4000]))
    par={i:i for i in ids}
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for a in range(len(ids)):
        for b in range(a+1,len(ids)):
            i,j=ids[a],ids[b]
            if difflib.SequenceMatcher(None,txt[i],txt[j]).ratio()>thresh: par[f(i)]=f(j)
    return len({f(i) for i in ids})

print("="*76); print(f"TABLE 2 (final)  quantitative environmental reporting, n = {N} cards"); print("="*76)
print(f"{'measure':34s} {'cards':>5s} {'%':>5s} {'95% CI':>12s} {'orgs':>5s} {'tmpl':>5s}")
for col,label in [("co2","CO2 mass reported"),("energy","energy in kWh or joules"),
                  ("power","hardware power draw (TDP)"),("compute","GPU or TPU hours"),
                  ("any_quantity","ANY quantity reported"),
                  ("co2_nonum","carbon mentioned, no number"),
                  ("perf_watt","tokens-per-watt claim"),
                  ("eff_claim","efficiency claim, no number")]:
    s=d[d[col]]; k=len(s); lo,hi=wilson(k,N)
    print(f"  {label:32s} {k:5d} {k/N*100:5.2f} {f'{lo}-{hi}':>12s} {s.org.nunique():5d} {families(s):5d}")

q=d[d.any_quantity]
print(f"\nWHO reports: {len(q)} cards, {q.org.nunique()} organizations, {families(q)} template families")
for o,n in Counter(q.org).most_common(): print(f"    {o:24s} {n}")

print("\n" + "="*76); print("TABLE 3 (final)  compression artifacts versus other models"); print("="*76)
A=d[d.compression]; B=d[~d.compression]
print(f"  compression artifacts n={len(A)} ({A.org.nunique()} orgs) | other n={len(B)} ({B.org.nunique()} orgs)")
def orci(a,b,c,dd,z=1.96):
    if 0 in (a,b,c,dd): a,b,c,dd=a+.5,b+.5,c+.5,dd+.5
    o=(a*dd)/(b*c); se=np.sqrt(1/a+1/b+1/c+1/dd)
    return o,np.exp(np.log(o)-z*se),np.exp(np.log(o)+z*se)
for col,label in [("any_quantity","reports any quantity"),
                  ("eff_claim","asserts efficiency, no number"),
                  ("perf_watt","tokens-per-watt claim")]:
    ay,an=int(A[col].sum()),int((~A[col]).sum()); by,bn=int(B[col].sum()),int((~B[col]).sum())
    o,lo,hi=orci(ay,an,by,bn); _,p=stats.fisher_exact([[ay,an],[by,bn]])
    print(f"\n  {label}")
    print(f"    compression {ay:3d}/{len(A)} ({ay/len(A)*100:4.1f}%, {A[A[col]].org.nunique()} orgs, {families(A[A[col]])} tmpl)")
    print(f"    other       {by:3d}/{len(B)} ({by/len(B)*100:4.1f}%, {B[B[col]].org.nunique()} orgs, {families(B[B[col]])} tmpl)")
    print(f"    OR={o:.2f} [{lo:.2f}, {hi:.2f}]  Fisher p={p:.4f}")

d.drop(columns=["body"]).to_csv("results_v3_cards.csv", index=False)
print("\nwrote results_v3_cards.csv")
