from __future__ import annotations

import csv, hashlib, json, math, os, platform, shutil, statistics, subprocess, sys, time
from pathlib import Path
from io import BytesIO
from PIL import Image, features

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "build/full-map-atlas/tiles"
OUT = ROOT / "build/otbm-codec-benchmark"
N = 240

def pct(xs, p):
    ys=sorted(xs); x=(len(ys)-1)*p/100; a=math.floor(x); b=math.ceil(x)
    return ys[a] if a==b else ys[a]*(b-x)+ys[b]*(x-a)

def even(seq, n):
    if n >= len(seq): return list(seq)
    return [seq[round(i*(len(seq)-1)/(n-1))] for i in range(n)]

def sha(b): return hashlib.sha256(b).hexdigest()

files=sorted(CORPUS.glob("z*/*.png"), key=lambda p:p.relative_to(CORPUS).as_posix())
if not files: raise SystemExit("BLOCKED: no detailed chunks")
sizes={p:p.stat().st_size for p in files}
by_floor={}
for p in files: by_floor.setdefault(int(p.parent.name[1:]),[]).append(p)
selected=set()
for group in by_floor.values(): selected.update(even(group, min(6,len(group))))
ranked=sorted(files,key=lambda p:(sizes[p],p.as_posix()))
quartiles=[ranked[i*len(ranked)//4:(i+1)*len(ranked)//4] for i in range(4)]
for q in quartiles: selected.update(even(q,16))
for p in even(files, N):
    if len(selected)>=N: break
    selected.add(p)
for p in files:
    if len(selected)>=N: break
    selected.add(p)
selected=sorted(selected,key=lambda p:p.relative_to(CORPUS).as_posix())

OUT.mkdir(parents=True,exist_ok=True); (OUT/"samples").mkdir(exist_ok=True)
rows=[]
for idx,p in enumerate(selected,1):
    raw=p.read_bytes(); floor=int(p.parent.name[1:])
    with Image.open(BytesIO(raw)) as im:
        rgba=im.convert("RGBA"); original=rgba.tobytes(); w,h=rgba.size
        thumb=rgba.resize((min(64,w),min(64,h)),Image.Resampling.NEAREST).convert("RGB")
        hist=thumb.histogram(); total=sum(hist); probs=[v/total for v in hist if v]
        entropy=-sum(v*math.log2(v) for v in probs)
        t0=time.perf_counter_ns(); bio=BytesIO(); rgba.save(bio,"WEBP",lossless=True,method=6,exact=True); webp=bio.getvalue(); enc=time.perf_counter_ns()-t0
    with Image.open(BytesIO(webp)) as wi:
        wrgba=wi.convert("RGBA"); equal=wrgba.size==(w,h) and wrgba.tobytes()==original
    png_times=[]; webp_times=[]
    for _ in range(3):
        t=time.perf_counter_ns()
        with Image.open(BytesIO(raw)) as x: x.convert("RGBA").load()
        png_times.append(time.perf_counter_ns()-t)
        t=time.perf_counter_ns()
        with Image.open(BytesIO(webp)) as x: x.convert("RGBA").load()
        webp_times.append(time.perf_counter_ns()-t)
    rows.append({"path":p.relative_to(ROOT).as_posix(),"floor":floor,"width":w,"height":h,"pixels":w*h,"png_bytes":len(raw),"webp_bytes":len(webp),"saving_bytes":len(raw)-len(webp),"saving_percent":100*(len(raw)-len(webp))/len(raw),"encode_ms":enc/1e6,"png_decode_ms":statistics.median(png_times)/1e6,"webp_decode_ms":statistics.median(webp_times)/1e6,"entropy":entropy,"rgba_equal":equal,"png_sha256":sha(raw),"webp_sha256":sha(webp),"_webp":webp})
    print(f"{idx}/{len(selected)} {p.name} {len(raw)} -> {len(webp)}",flush=True)

if not all(r["rgba_equal"] for r in rows): raise SystemExit("UNSAFE: RGBA mismatch")
png_total=sum(r["png_bytes"] for r in rows); webp_total=sum(r["webp_bytes"] for r in rows)
all_png=sum(sizes.values()); estimate=round(all_png*webp_total/png_total)

def pick_unique(groups):
    out=[]
    for group in groups:
        added=0
        for r in group:
            if r not in out:
                out.append(r); added+=1
            if added==4: break
    return out[:24]

by_size=sorted(rows,key=lambda r:(r["png_bytes"],r["path"])); by_entropy=sorted(rows,key=lambda r:(r["entropy"],r["path"]))
median_order=sorted(rows,key=lambda r:(abs(r["png_bytes"]-statistics.median(x["png_bytes"] for x in rows)),r["path"]))
floor_dist=[]
for f in sorted(by_floor):
    candidates=[r for r in rows if r["floor"]==f]
    if candidates: floor_dist.append(candidates[len(candidates)//2])
visual=pick_unique([list(reversed(by_size))[:12],by_size[:12],median_order[:12],list(reversed(by_entropy))[:12],by_entropy[:12],even(floor_dist, min(12,len(floor_dist)))])

for i,r in enumerate(visual,1):
    d=OUT/"samples"/f"{i:02d}"; d.mkdir(exist_ok=True)
    src=ROOT/r["path"]; shutil.copyfile(src,d/"original.png"); (d/"lossless.webp").write_bytes(r["_webp"])
    meta={k:v for k,v in r.items() if not k.startswith("_")}; meta["original_atlas_path"]=r["path"]
    (d/"metadata.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")

fields=[k for k in rows[0] if not k.startswith("_")]
with (OUT/"results.csv").open("w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows({k:r[k] for k in fields} for r in rows)

savings=[r["saving_percent"] for r in rows]; enc=[r["encode_ms"] for r in rows]; pd=[r["png_decode_ms"] for r in rows]; wd=[r["webp_decode_ms"] for r in rows]
head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
summary={"verdict":"WEBP_LOSSLESS_WIN" if 100*(png_total-webp_total)/png_total>=10 else "NO_MATERIAL_GAIN","repo_head":head,"environment":{"os":platform.platform(),"cpu":platform.processor(),"python":sys.version,"pillow":Image.__version__,"libwebp":features.version("webp"),"encoder":{"format":"WEBP","lossless":True,"method":6,"exact":True}},"corpus":{"detail_chunks":len(files),"detail_png_bytes":all_png,"benchmarked":len(rows),"floors":sorted({r['floor'] for r in rows}),"selection":"deterministic union of 6 evenly distributed paths per floor, 16 per size quartile, then evenly distributed sorted paths; filled to exactly 240"},"storage":{"png_bytes":png_total,"webp_bytes":webp_total,"saving_bytes":png_total-webp_total,"saving_percent":100*(png_total-webp_total)/png_total,"ratio":webp_total/png_total,"percentiles":{f"p{p}":pct(savings,p) for p in (10,25,50,75,90,95)},"mean":statistics.mean(savings),"median":statistics.median(savings),"best":max(savings),"worst":min(savings)},"timing_ms":{"encode":{"total":sum(enc),"mean":statistics.mean(enc),"median":statistics.median(enc),"p95":pct(enc,95)},"png_decode":{"mean":statistics.mean(pd),"median":statistics.median(pd),"p95":pct(pd,95)},"webp_decode":{"mean":statistics.mean(wd),"median":statistics.median(wd),"p95":pct(wd,95),"delta_percent":100*(statistics.median(wd)/statistics.median(pd)-1)}},"rgba_exact":all(r['rgba_equal'] for r in rows),"full_atlas":{"kind":"ESTIMATED","webp_bytes":estimate,"saving_bytes":all_png-estimate,"saving_percent":100*(all_png-estimate)/all_png},"visual_samples":[r['path'] for r in visual]}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")

per_floor=[]
for f in sorted({r['floor'] for r in rows}):
    q=[r for r in rows if r['floor']==f]; a=sum(x['png_bytes'] for x in q); b=sum(x['webp_bytes'] for x in q); per_floor.append(f"| {f} | {len(q)} | {a} | {b} | {100*(a-b)/a:.2f}% |")
report=f"""VERDICT: {summary['verdict']}

## Environment

- Repository head: `{head}`
- OS: {platform.platform()}
- CPU: {platform.processor()}
- Python: {platform.python_version()}; Pillow: {Image.__version__}; libwebp: {features.version('webp')}
- WebP parameters: `lossless=True, method=6, exact=True`

## Corpus

- Discovered: {len(files)} canonical detail PNG chunks, {all_png} bytes.
- Benchmarked: {len(rows)} chunks; floors {sorted({r['floor'] for r in rows})}.
- Selection: {summary['corpus']['selection']} Exact paths are in `results.csv`.

## Results

| Format | Total bytes | Saving vs PNG | Encode median/p95 | Decode median/p95 | RGBA exact |
|---|---:|---:|---:|---:|---|
| Existing PNG | {png_total} | baseline | n/a | {statistics.median(pd):.3f}/{pct(pd,95):.3f} ms | source |
| WebP lossless | {webp_total} | {100*(png_total-webp_total)/png_total:.2f}% | {statistics.median(enc):.3f}/{pct(enc,95):.3f} ms | {statistics.median(wd):.3f}/{pct(wd,95):.3f} ms | PASS ({len(rows)}/{len(rows)}) |

Saving distribution: mean {statistics.mean(savings):.2f}%, median {statistics.median(savings):.2f}%, p10 {pct(savings,10):.2f}%, p25 {pct(savings,25):.2f}%, p50 {pct(savings,50):.2f}%, p75 {pct(savings,75):.2f}%, p90 {pct(savings,90):.2f}%, p95 {pct(savings,95):.2f}%, best {max(savings):.2f}%, worst {min(savings):.2f}%.

## Per floor

| Floor | n | PNG bytes | WebP bytes | Saving |
|---:|---:|---:|---:|---:|
{chr(10).join(per_floor)}

## Visual samples

Open `build/otbm-codec-benchmark/comparison.html`. Samples: {', '.join(r['path'] for r in visual)}.

## Full-atlas impact

ESTIMATED from the measured aggregate ratio: {estimate} WebP bytes, saving {all_png-estimate} bytes ({100*(all_png-estimate)/all_png:.2f}%) from the exact current {all_png} PNG bytes. This is not a full conversion measurement.

## Risks / caveats

This measures codec/storage and local Pillow/libwebp timings only, not browser performance. Implementation complexity was not assessed. Overview and creature/environment assets were excluded. The existing PNG files were used byte-for-byte; only representative copies were written.
"""
(OUT/"report.md").write_text(report,encoding="utf-8")

cards=[]
for i,r in enumerate(visual,1):
    cards.append(f'<section><h2>{i:02d} — {r["path"]}</h2><p>floor {r["floor"]} · PNG {r["png_bytes"]:,} B · WebP {r["webp_bytes"]:,} B · saving {r["saving_percent"]:.2f}% · RGBA exact: {r["rgba_equal"]}</p><div><figure><img src="samples/{i:02d}/original.png"><figcaption>Original PNG</figcaption></figure><figure><img src="samples/{i:02d}/lossless.webp"><figcaption>Lossless WebP</figcaption></figure></div></section>')
html='<!doctype html><meta charset="utf-8"><title>OTBM codec comparison</title><style>body{font:14px system-ui;background:#111;color:#eee;margin:24px}section{border-top:1px solid #555;padding:16px 0}section div{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0;overflow:auto;background:#222;padding:8px}img{max-width:none;image-rendering:pixelated}h2{font-size:16px}@media(max-width:800px){section div{grid-template-columns:1fr}}</style><h1>OTBM Atlas: PNG vs WebP lossless</h1>'+''.join(cards)
(OUT/"comparison.html").write_text(html,encoding="utf-8")
print(json.dumps(summary,indent=2))
