#!/usr/bin/env python3
"""NepDate राशिफल Voice TTS — XTTS-v2 मार्फत तपाईंकै आवाजमा भ्वाइसओभर।

प्रयोग (GitHub Actions / लोकल):
  python voice_tts.py content.today.json --out videos
  python voice_tts.py content.today.json --out videos --voice assets/voice_sample.wav
  python voice_tts.py --test    # सानो टेस्ट (मेष मात्र)
"""
import os
# Coqui TTS License TOS agreement non-interactive headless bypass
os.environ["COQUI_TOS_AGREED"] = "1"

import argparse, json, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).parent.resolve()
VOICE_SAMPLE = HERE / "assets" / "voice_sample.wav"


# ───────────────────────────────────────────────────────────
# १. टेक्स्ट बनाउने (राशिफलको सामग्रीबाट)
# ───────────────────────────────────────────────────────────
def build_script(sign: dict) -> str:
    """एक राशिको TTS स्क्रिप्ट बनाउँछ — प्राकृतिक विराम सहित।"""
    name = sign.get("name", "").strip()
    sentences = [s["text"].strip() for s in sign.get("sentences", []) if s.get("text")]

    # अगाडि राशि नाम, पछाडि वाक्यहरू
    parts = [f"{name} राशि।"]
    for s in sentences:
        s_clean = s.rstrip("। .")
        parts.append(f"{s_clean}।")
    return "  ".join(parts)


# ───────────────────────────────────────────────────────────
# २. Main TTS Pipeline
# ───────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="NepDate Voice TTS")
    ap.add_argument("content", nargs="?", default="content.today.json",
                    help="JSON सामग्री फाइल (default: content.today.json)")
    ap.add_argument("--out", default="videos", help="आउटपुट फोल्डर")
    ap.add_argument("--voice", default=str(VOICE_SAMPLE),
                    help="Voice reference WAV फाइल")
    ap.add_argument("--lang", default="hi",
                    help="TTS भाषा कोड (default: hi - सर्वश्रेष्ठ देवनागरी उच्चारण)")
    ap.add_argument("--only", nargs="*", type=int,
                    help="छानिएका राशि नम्बरहरू (१=मेष ... १२=मीन)")
    ap.add_argument("--test", action="store_true",
                    help="टेस्ट मोड: पहिलो राशि मात्र")
    ap.add_argument("--speed", type=float, default=0.92,
                    help="बोलीको गति (default: 0.92)")
    a = ap.parse_args()

    voice_path = Path(a.voice)
    if not voice_path.exists():
        sys.exit(f"त्रुटि: Voice sample भेटिएन: {voice_path}\n"
                 f"कृपया assets/voice_sample.wav राख्नुहोस्।")

    content_path = Path(a.content)
    if not content_path.exists():
        sys.exit(f"त्रुटि: Content फाइल भेटिएन: {content_path}")

    # TTS import check
    try:
        import torch
        from TTS.api import TTS
    except ImportError as e:
        sys.exit(
            f"त्रुटि: TTS वा PyTorch लोड गर्न सकिएन ({e})।\n"
            "कृपया चलाउनुहोस्: pip install TTS torch torchaudio"
        )

    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cpu":
        torch.set_num_threads(2)
    print(f"🎙️  TTS Device: {device} | Voice Sample: {voice_path.name}", flush=True)

    content = json.load(open(content_path, encoding="utf-8"))
    signs = content.get("signs", [])

    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # कुन राशि
    if a.test:
        indices = [0]
    elif a.only:
        indices = [i - 1 for i in a.only]
    else:
        indices = list(range(len(signs)))

    # १ पटक मात्र मोडल लोड गर्ने (12 पटक होइन!)
    print("⏳ XTTS-v2 मोडल मेमोरीमा लोड गर्दैछ (एक पटक मात्र)...", flush=True)
    t_load_start = time.time()
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    print(f"✅ मोडल लोड भयो ({time.time() - t_load_start:.1f}s)", flush=True)

    print(f"\n--- {len(indices)} राशिका लागि भ्वाइस क्लोनिङ सुरु ---\n", flush=True)
    for idx in indices:
        if idx >= len(signs):
            continue
        sign = signs[idx]
        name = sign.get("name", f"rashi_{idx+1}")
        script = build_script(sign)
        out_wav = out_dir / f"_voice_{idx+1:02d}.wav"

        print(f"[{idx+1:02d}/12] {name}: {script[:65]}...", flush=True)
        t_synth = time.time()
        tts.tts_to_file(
            text=script,
            speaker_wav=str(voice_path),
            language=a.lang,
            file_path=str(out_wav),
            speed=a.speed,
            split_sentences=True,
        )
        print(f"       ✓ {out_wav.name} तयार ({time.time() - t_synth:.1f}s)", flush=True)

    print(f"\n✅ सबै भ्वाइस फाइलहरू सफलतापूर्वक तयार भए: {out_dir}\n", flush=True)


if __name__ == "__main__":
    main()
