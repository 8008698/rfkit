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
ap.add_argument("--voice", action="store_true", help="XTTS-v2 मार्फत तपाईंकै आवाजमा भ्वाइसओभर जोड्ने")
ap.add_argument("--voice-sample", default="assets/voice_sample.wav",
                help="Voice reference WAV (default: assets/voice_sample.wav)")
ap.add_argument("--voice-prebuilt", action="store_true",
                help="voice_tts.py ले --out फोल्डरमा पहिले नै बनाइसकेका _voice_NN.wav files उठाउने")

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

        # ── Voice Mixing ─────────────────────────────────────────────────
        # --voice-prebuilt: voice_tts.py ले पहिले नै बनाइसकेको WAV उठाउने
        # --voice:          यहीँ voice_tts.py चलाएर WAV बनाउने
        use_voice = getattr(a, "voice_prebuilt", False) or getattr(a, "voice", False)
        if use_voice:
            voice_full = out / "_voice_full.wav"

            # pre-built WAV files छैनन् भने voice_tts.py चलाउने
            prebuilt_parts = sorted(out.glob("_voice_*.wav"))
            if not prebuilt_parts and getattr(a, "voice", False):
                voice_sample = HERE / getattr(a, "voice_sample", "assets/voice_sample.wav")
                if not voice_sample.exists():
                    print(f"⚠️  Voice sample भेटिएन ({voice_sample}) — म्युजिक मात्र राखिनेछ।", flush=True)
                    use_voice = False
                else:
                    print("🎙️  Voice TTS सुरु गर्दै (XTTS-v2)...", flush=True)
                    tts_cmd = [
                        sys.executable, str(HERE / "voice_tts.py"),
                        str(content_path), "--out", str(out),
                        "--voice", str(voice_sample),
                    ]
                    if a.only:
                        tts_cmd.extend(["--only"] + [str(x) for x in a.only])
                    env = dict(os.environ, COQUI_TOS_AGREED="1")
                    result = subprocess.run(tts_cmd, env=env)
                    if result.returncode != 0:
                        print(f"⚠️  Voice TTS फेल (exit {result.returncode}) — म्युजिक मात्र राखिनेछ।", flush=True)
                        use_voice = False
                    else:
                        prebuilt_parts = sorted(out.glob("_voice_*.wav"))

            if use_voice:
                voice_parts = prebuilt_parts if prebuilt_parts else sorted(out.glob("_voice_*.wav"))
                if not voice_parts:
                    print("⚠️  _voice_*.wav फाइलहरू भेटिएनन् — म्युजिक मात्र राखिनेछ।", flush=True)
                    use_voice = False
                else:
                    print(f"⏱️  {len(voice_parts)} वटा voice WAV भेटिए — timeline sync सुरु...", flush=True)

                    # Timeline sync: प्रत्येक राशिको voice लाई सही समयमा राख्ने
                    synced = False
                    try:
                        import numpy as np
                        from scipy.io import wavfile
                        from scipy.signal import resample as sig_resample

                        SR = 44100
                        total_s = int(T * SR)
                        timeline = np.zeros(total_s, dtype=np.float32)

                        for s_info in sec.get("signs", []):
                            si = s_info.get("si", 0)
                            p = out / f"_voice_{si+1:02d}.wav"
                            if not p.exists():
                                print(f"  ⚠️  {p.name} भेटिएन, skip.", flush=True)
                                continue
                            sr, data = wavfile.read(str(p))
                            if data.dtype == np.int16:
                                data = data.astype(np.float32) / 32768.0
                            elif data.dtype == np.int32:
                                data = data.astype(np.float32) / 2147483648.0
                            elif data.dtype == np.uint8:
                                data = (data.astype(np.float32) - 128.0) / 128.0
                            if data.ndim > 1:
                                data = data.mean(axis=1)
                            if sr != SR:
                                data = sig_resample(data, int(len(data) * SR / sr))

                            # राशि slide सुरु भएको 2 sec पछि बोल्ने
                            start_idx = int((s_info.get("S", 0.0) + 2.0) * SR)
                            end_idx = min(total_s, start_idx + len(data))
                            if 0 <= start_idx < total_s:
                                chunk = data[:end_idx - start_idx]
                                timeline[start_idx:end_idx] += chunk
                                synced = True
                                print(f"  ✓ राशि {si+1:02d}: t={s_info.get('S',0):.1f}s + 2.0s = start {start_idx/SR:.1f}s, dur={len(chunk)/SR:.1f}s", flush=True)

                        if synced:
                            peak = np.max(np.abs(timeline))
                            if peak > 0.0:
                                timeline = timeline * (0.92 / peak)
                            wavfile.write(str(voice_full), SR, (timeline * 32767).astype(np.int16))
                            print(f"✅  Timeline sync सम्पन्न → {voice_full.name}", flush=True)
                        else:
                            print("⚠️  कुनै पनि voice WAV timeline मा राख्न सकिएन।", flush=True)

                    except Exception as sync_err:
                        import traceback
                        print(f"⚠️  Timeline sync error: {sync_err}", flush=True)
                        traceback.print_exc()

                    # Fallback: sync fail भए concat गर्ने
                    if not voice_full.exists():
                        print("🔄  Fallback: voice WAV files concat गर्दै...", flush=True)
                        list_file = out / "_voice_list.txt"
                        list_file.write_text(
                            "\n".join(f"file '{p.name}'" for p in voice_parts),
                            encoding="utf-8"
                        )
                        subprocess.run([
                            "ffmpeg", "-y", "-loglevel", "error",
                            "-f", "concat", "-safe", "0",
                            "-i", str(list_file),
                            "-ar", "44100", "-ac", "1",
                            str(voice_full)
                        ], check=True)
                        list_file.unlink(missing_ok=True)

                    if voice_full.exists():
                        # Voice (100%) + Background music (15%) mix
                        mixed_wav = out / "_mixed_audio.wav"
                        subprocess.run([
                            "ffmpeg", "-y", "-loglevel", "error",
                            "-i", str(voice_full),
                            "-i", str(wav),
                            "-filter_complex",
                            "[0:a]volume=1.0[v];[1:a]volume=0.15[bg];[v][bg]amix=inputs=2:duration=longest:dropout_transition=3[out]",
                            "-map", "[out]",
                            "-ar", "44100",
                            str(mixed_wav)
                        ], check=True)
                        wav = mixed_wav
                        voice_full.unlink(missing_ok=True)
                        print("✅  तपाईंकै आवाज + ब्याकग्राउन्ड म्युजिक — मिक्स सम्पन्न!", flush=True)
                    else:
                        print("⚠️  voice_full.wav बनेन — म्युजिक मात्र राखिनेछ।", flush=True)

                    # अस्थायी voice part files सफा गर्ने
                    for p in voice_parts:
                        p.unlink(missing_ok=True)

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
