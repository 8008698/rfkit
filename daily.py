#!/usr/bin/env python3
"""दैनिक स्वचालित भिडियो: आजको नेपाली मिति + NepDate राशिफल → render।

प्रयोगका उदाहरणहरू:
  python daily.py --file ../data/nepdate/nepdate_2026-09-15.json --dry   # स्थानीय फाइलबाट सामग्री जाँच्ने (अफ्लाइन)
  python daily.py --date 2026-09-15 --dry                                 # मितिअनुसार सामग्री जाँच्ने
  python daily.py --date 2026-09-15 --test --only 1                       # पहिलो राशिको टेस्ट फोटो
  python daily.py --date 2026-09-15 --only 1 2                            # छानिएका राशि मात्र भिडियो
  python daily.py                                                         # आजको मितिमा पूरा भिडियो
"""
import argparse, datetime as dt, json, os, subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))
import fetch_content as fc

MONTHS = ["बैशाख", "जेठ", "असार", "श्रावण", "भाद्र", "आश्विन", "कार्तिक", "मंसिर", "पौष", "माघ", "फाल्गुन", "चैत्र"]
WEEK = ["सोमवार", "मंगलवार", "बुधवार", "बिहीवार", "शुक्रवार", "शनिवार", "आइतवार"]
DEV_MAP = str.maketrans("0123456789", "०१२३४५६७८९")
dev = lambda n: str(n).translate(DEV_MAP)

ap = argparse.ArgumentParser(description="NepDate दैनिक राशिफल भिडियो स्वचालन किट")
ap.add_argument("--config", default="config.json", help="कन्फिग फाइल (default: config.json)")
ap.add_argument("--base", default="content.json", help="आधारभूत टेम्प्लेट (default: content.json)")
ap.add_argument("--file", help="सिधा स्थानीय NepDate JSON फाइलको बाटो (e.g. ../data/nepdate/nepdate_2026-09-15.json)")
ap.add_argument("--local-dir", default="../data/nepdate", help="स्थानीय nepdate फोल्डर (default: ../data/nepdate)")
ap.add_argument("--date", help="AD मिति YYYY-MM-DD (खाली भए आजको मिति, नेपाल समय)")
ap.add_argument("--out", default="videos", help="भिडियो आउटपुट फोल्डर (default: videos)")
ap.add_argument("--dry", action="store_true", help="सामग्री मात्र content.today.json मा तयार गर्ने (रेन्डर नगर्ने)")
ap.add_argument("--test", action="store_true", help="रेन्डर टेस्ट: मुख्य क्षणका फोटो मात्र खिच्ने")
ap.add_argument("--only", nargs="*", type=int, help="छानिएका राशि नम्बरहरू (१=मेष … १२=मीन)")
ap.add_argument("--fps", type=int, default=20, help="भिडियो फ्रेम रेट (default: 20)")
ap.add_argument("--crf", type=int, default=20, help="x264 भिडियो गुणस्तर (default: 20)")
ap.add_argument("--probe", action="store_true", help="API/फाइलको कच्चा उत्तर देखाउँछ")
ap.add_argument("--allow-stale", action="store_true", help="डाटा नभेटिए पुरानै टेम्प्लेट प्रयोग गर्ने")
ap.add_argument("--free-api", action="store_true", help="निःशुल्क /api/ai/today endpoint प्रयोग गर्ने")
ap.add_argument("--no-intro", action="store_true", help="इन्ट्रो स्क्रिन नराख्ने")
ap.add_argument("--no-outro", action="store_true", help="आउट्रो लोगो स्क्रिन नराख्ने")
ap.add_argument("--intro", action="store_true", help="इन्ट्रो स्क्रिन राख्ने")
ap.add_argument("--outro", action="store_true", help="आउट्रो लोगो स्क्रिन राख्ने")

a = ap.parse_args()

cfg_path = HERE / a.config
cfg = json.load(open(cfg_path, encoding="utf-8")) if cfg_path.exists() else {}
content_path = HERE / a.base
content = json.load(open(content_path, encoding="utf-8")) if content_path.exists() else {"signs": []}

# १. AD मिति निर्धारण (नेपाल समय Asia/Kathmandu)
try:
    from zoneinfo import ZoneInfo
    ad = dt.datetime.now(ZoneInfo("Asia/Kathmandu")).date()
except Exception:
    ad = dt.date.today()

if a.date:
    ad = dt.date.fromisoformat(a.date)

ad_iso = ad.isoformat()

# २. स्रोत निर्धारण: स्थानीय फाइल पहिलो प्राथमिकता (LOCAL FIRST)
api_cfg = cfg.get("api", {})
target_url = None

if a.file and os.path.exists(a.file):
    target_url = "file://" + os.path.abspath(a.file)
    print(f"स्थानीय फाइल प्रयोग गर्दै: {a.file}")
else:
    # Check local directory (e.g. ../data/nepdate/nepdate_YYYY-MM-DD.json or ./data/nepdate/)
    local_candidates = [
        Path(a.local_dir) / f"nepdate_{ad_iso}.json",
        HERE / "data" / "nepdate" / f"nepdate_{ad_iso}.json",
        HERE.parent / "data" / "nepdate" / f"nepdate_{ad_iso}.json"
    ]
    for cand in local_candidates:
        if cand.exists():
            target_url = "file://" + str(cand.resolve())
            print(f"स्थानीय NepDate डेटा भेटियो: {cand}")
            break

# If not local, set remote API URL
if not target_url:
    api_key = os.environ.get("NEPDATE_API_KEY", "")
    if a.free_api or not api_key:
        target_url = f"https://nepdate-api.khumnath.com.np/api/ai/today?rashifal=true&date={ad_iso}"
        print(f"निःशुल्क NepDate AI API प्रयोग गर्दै (API Key आवश्यक छैन): {ad_iso}")
    else:
        target_url = api_cfg.get("url") or f"https://nepdate-api.khumnath.com.np/rashifal?date={ad_iso}&lang=ne&apiKey=${{NEPDATE_API_KEY}}"
        print(f"NepDate Enterprise API प्रयोग गर्दै")

if os.environ.get("NEPDATE_API_URL"):
    target_url = os.environ["NEPDATE_API_URL"]

api_dict = {
    "url": target_url,
    "headers": api_cfg.get("headers", {}),
    "signs_path": api_cfg.get("signs_path", ""),
    "match": api_cfg.get("match", ""),
    "fields": api_cfg.get("fields", {})
}

fmt = {"ad": ad_iso}

if a.probe:
    data = fc.raw(api_dict, fmt)
    items = fc.find_items(data)
    first = (list(items.items())[0] if isinstance(items, dict) else items[0]) if items else data
    print(json.dumps(first, ensure_ascii=False, indent=2)[:3500])
    sys.exit(0)

# ३. सामग्री लोड र रूपान्तरण
try:
    got, meta_date = fc.fetch(api_dict, fmt)
    if not got:
        raise RuntimeError("कुनै राशिफल डेटा प्राप्त भएन")
    if len(got) < 12:
        print(f"चेतावनी: १२ मध्ये {len(got)} राशि मात्र भेटियो")

    # मिति अद्यावधिक
    if meta_date and "year" in meta_date:
        bs_year = meta_date["year"]
        bs_month = meta_date["month"]
        bs_day = meta_date["day"]
        m_name = meta_date.get("monthName") or MONTHS[bs_month - 1]
        w_day = meta_date.get("dayOfWeek") or WEEK[ad.weekday()]
        content["date"] = {
            "year": dev(bs_year),
            "month": m_name,
            "day": dev(bs_day),
            "weekday": w_day
        }
        bs = (bs_year, bs_month, bs_day)
    else:
        # Fallback to nepali_datetime or /convert
        bs = None
        try:
            import nepali_datetime
            n = nepali_datetime.date.from_datetime_date(ad)
            bs = (n.year, n.month, n.day)
            content["date"] = {
                "year": dev(bs[0]),
                "month": MONTHS[bs[1] - 1],
                "day": dev(bs[2]),
                "weekday": WEEK[ad.weekday()]
            }
        except Exception:
            pass

    # १२ राशिको सामग्री content मा जोड्ने
    for i, r in got.items():
        if i >= len(content.get("signs", [])):
            continue
        if r.get("_fallback"):
            print("सूचना:", content["signs"][i]["name"], "को पाठ उपलब्ध नभएकाले श्रेणी-अंकबाट तयार गरियो")
        for k, v in r.items():
            if k != "_fallback":
                content["signs"][i][k] = v

    print(f"सफल: {len(got)} राशिको राशिफल सामग्री मिलाइयो।")
except Exception as e:
    print("डेटा लोडमा त्रुटि:", e)
    if not a.allow_stale:
        sys.exit("रोकियो: पुरानो/नमुना पाठले भिडियो नबनाउन (--allow-stale ले बाइपास हुन्छ)।")

# इन्ट्रो र ट्यागलाइन
for k in ("intro", "tagline"):
    if k in cfg:
        content[k] = cfg[k]

# content.today.json बचत
today_json_path = HERE / "content.today.json"
today_json_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"तयार भयो: {today_json_path.name} (मिति: {content.get('date')})")

if a.dry:
    print("Dry-run समाप्त भयो (रेन्डर नगरी रोकियो)।")
    sys.exit(0)

# ४. भिडियो रेन्डर आह्वान (render.py)
out_dir = Path(a.out)
if out_dir.exists() and not a.dry:
    date_label = (f"{bs[0]}-{bs[1]:02d}-{bs[2]:02d}" if 'bs' in locals() and bs else ad_iso)
    for old_vid in out_dir.glob("NepDate_Rashifal_*.mp4"):
        if date_label not in old_vid.name:
            print(f"पुरानो भिडियो हटाइयो: {old_vid.name}")
            try:
                old_vid.unlink()
            except Exception:
                pass

cmd = [
    sys.executable,
    str(HERE / "render.py"),
    str(today_json_path),
    "--out", a.out,
    "--fps", str(a.fps),
    "--crf", str(a.crf)
]
if a.test:
    cmd.append("--test")
if a.only:
    cmd.extend(["--only"] + [str(x) for x in a.only])
if a.no_intro:
    cmd.append("--no-intro")
if a.no_outro:
    cmd.append("--no-outro")
if a.intro:
    cmd.append("--intro")
if a.outro:
    cmd.append("--outro")

print("रेन्डर सुरु गर्दैछ:", " ".join(cmd))
subprocess.run(cmd, check=True)

if not a.test:
    date_label = (f"{bs[0]}-{bs[1]:02d}-{bs[2]:02d}" if 'bs' in locals() and bs else ad_iso)
    for f in Path(a.out).glob("NepDate_Rashifal_*.mp4"):
        if "_20" not in f.stem[-12:]:
            new_name = f.with_name(f"NepDate_Rashifal_{date_label}.mp4")
            f.rename(new_name)
            print(f"अन्तिम भिडियो फाइल: {new_name}")
