#!/usr/bin/env python3
"""NepDate राशिफल भिडियो render.
  python render.py content.json              # पूरा भिडियो: इन्ट्रो → मेष … मीन → लोगो आउट्रो (एउटै MP4)
  python render.py content.json --only 1 2    # केही राशि मात्र (१=मेष, २=वृष ...)
  python render.py content.json --test        # छिटो टेस्ट: मुख्य क्षणका फोटो मात्र (२-३ सेकेन्ड)
  python render.py content.json --fps 24 --out videos
"""
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).parent.resolve()
sys.path.insert(0, str(HERE))

# Playwright check
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit(
        "त्रुटि: Playwright इन्स्टल गरिएको छैन।\n"
        "कृपया तलका कमान्ड चलाउनुहोस्:\n"
        "  pip install playwright numpy scipy\n"
        "  playwright install chromium\n"
    )

# ffmpeg check
if not shutil.which("ffmpeg"):
    sys.exit("त्रुटि: 'ffmpeg' सिस्टममा भेटिएन। कृपया ffmpeg इन्स्टल गर्नुहोस् (e.g. sudo apt install ffmpeg)।")

import audio

ap = argparse.ArgumentParser(description="NepDate राशिफल भिडियो रेन्डरर")
ap.add_argument("content", help="JSON सामग्री फाइलको बाटो (e.g. content.today.json)")
ap.add_argument("--only", nargs="*", type=int, help="राशि नम्बर (१=मेष … १२=मीन); पहिलो=१ भए इन्ट्रो, अन्तिम=१२ भए आउट्रो आउँछ")
ap.add_argument("--fps", type=int, default=20, help="फ्रेम रेट (default: 20)")
ap.add_argument("--out", default="videos", help="आउटपुट फोल्डर (default: videos)")
ap.add_argument("--test", action="store_true", help="छिटो टेस्ट: मुख्य फ्रेमका फोटो मात्र")
ap.add_argument("--crf", type=int, default=20, help="x264 भिडियो गुणस्तर (default: 20)")
ap.add_argument("--no-intro", action="store_true", help="इन्ट्रो स्क्रिन नराख्ने")
ap.add_argument("--no-outro", action="store_true", help="आउट्रो लोगो स्क्रिन नराख्ने")
ap.add_argument("--intro", action="store_true", help="इन्ट्रो स्क्रिन राख्ने")
ap.add_argument("--outro", action="store_true", help="आउट्रो स्क्रिन राख्ने")

a = ap.parse_args()

content_path = Path(a.content)
if not content_path.exists():
    sys.exit(f"त्रुटि: सामग्री फाइल भेटिएन: {a.content}")

content = json.load(open(content_path, encoding="utf-8"))
js = (HERE / "rashifal_video.js").read_text(encoding="utf-8")

assets = {
    "logo": "assets/logo.png",
    "badge": "assets/badge.png",
    "imgs": [f"assets/signs/{i:02d}.webp" for i in range(1, 13)]
}

out = Path(a.out)
out.mkdir(exist_ok=True, parents=True)

sub = [i - 1 for i in a.only] if a.only else list(range(12))

print(f"Playwright ब्राउजर खोल्दै... (राशि संख्या: {len(sub)})")
with sync_playwright() as p:
    try:
        b = p.chromium.launch(args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"])
    except Exception as e:
        sys.exit(f"त्रुटि: Chromium खोल्न सकिएन:\n{e}\n\nकृपया चलाउनुहोस्: playwright install chromium")

    pg = b.new_page(viewport={"width": 1080, "height": 1080})
    pg.set_content("<html></html>")
    pg.add_script_tag(content=js)

    opts = {"subset": sub}
    if a.no_intro: opts["intro"] = False
    elif a.intro: opts["intro"] = True
    if a.no_outro: opts["outro"] = False
    elif a.outro: opts["outro"] = True

    res = pg.evaluate(
        "([c,a,o])=>{const r=RV.build(c,a,o);return {doc:RV.doc(r),T:r.T,ev:r.ev,sec:r.sections}}",
        [content, assets, opts]
    )

    T = res["T"]
    ev = res["ev"]
    sec = res["sec"]

    hp = HERE / "_tmp.html"
    hp.write_text(res["doc"], encoding="utf-8")
    pg.goto("file://" + str(hp))
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(1000)
    pg.evaluate("document.getAnimations().forEach(x=>x.pause())")

    def shot(t, path):
        pg.evaluate("t=>document.getAnimations().forEach(x=>x.currentTime=t)", t * 1000)
        pg.screenshot(path=str(path), type="jpeg", quality=90)

    tag = "all" if not a.only else "_".join(str(x) for x in a.only)
    print(f"कुल भिडियो लम्बाइ: {T} सेकेन्ड ({T/60:.1f} मिनेट)", flush=True)

    if a.test:
        ts = []
        if sec["intro"] is not None:
            ts += [2.8, 6.2, 12.4]
        if sec["signs"]:
            s0 = sec["signs"][0]
            ts += [s0["S"] + 2.2, s0["S"] + 5.8, s0["c0"] + 3.2]
            if len(sec["signs"]) > 1:
                s1 = sec["signs"][1]
                ts += [s1["S"] + 2.2]
        if sec["out"] is not None:
            ts += [sec["out"] + 2.6]
        for t in ts:
            img_path = out / f"test_{tag}_t{t:06.1f}.jpg"
            shot(t, img_path)
        print(f"सफल: टेस्ट फोटोहरू यहाँ सुरक्षित भए: {out}", flush=True)
    else:
        fr = HERE / "_fr"
        shutil.rmtree(fr, ignore_errors=True)
        fr.mkdir(exist_ok=True)
        N = int(T * a.fps)
        t0 = time.time()
        print(f"फ्रेम रेन्डर सुरु भयो: जम्मा {N} फ्रेम ({a.fps} FPS)...")
        for f in range(N):
            shot(f / a.fps, fr / f"{f:06d}.jpg")
            if f % 150 == 0 or f == N - 1:
                elapsed = int(time.time() - t0)
                pct = (f + 1) / N * 100
                print(f"  फ्रेम {f+1}/{N} ({pct:.1f}%) — {elapsed}s", flush=True)

        silent = out / "_silent.mp4"
        wav = out / "_audio.wav"
        final = out / f"NepDate_Rashifal_{tag}.mp4"

        print("भिडियो स्ट्रिम इन्कोड गर्दै (x264)...")
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps),
             "-i", str(fr / "%06d.jpg"), "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-crf", str(a.crf), str(silent)],
            check=True
        )

        print("सङ्गीत अडियो तयार गर्दै...")
        audio.write(str(wav), T, ev, 7)

        print("भिडियो र अडियो जोड्दै (AAC)...")
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav),
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(final)],
            check=True
        )

        # सफाइ
        if silent.exists():
            silent.unlink()
        if wav.exists():
            wav.unlink()
        shutil.rmtree(fr, ignore_errors=True)
        print(f"सफल: अन्तिम भिडियो तयार भयो -> {final}", flush=True)

    if hp.exists():
        hp.unlink()
    b.close()
