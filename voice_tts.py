#!/usr/bin/env python3
"""NepDate राशिफल Voice TTS — XTTS-v2 मार्फत तपाईंकै आवाजमा भ्वाइसओभर।

प्रयोग (GitHub Actions / लोकल):
  python voice_tts.py content.today.json --out videos
  python voice_tts.py content.today.json --out videos --voice assets/voice_sample.wav
  python voice_tts.py --test    # सानो टेस्ट (मेष मात्र)
"""
import argparse, json, os, shutil, subprocess, sys, wave
from pathlib import Path

HERE = Path(__file__).parent.resolve()
VOICE_SAMPLE = HERE / "assets" / "voice_sample.wav"   # तपाईंको प्रोसेस्ड आवाज
RASHI_NAMES = [
    "मेष", "वृष", "मिथुन", "कर्कट", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"
]

# ───────────────────────────────────────────────────────────
# १. टेक्स्ट बनाउने (राशिफलको सामग्रीबाट)
# ───────────────────────────────────────────────────────────
def build_script(sign: dict) -> str:
    """एक राशिको TTS स्क्रिप्ट बनाउँछ — भाव-पूर्ण विराम सहित।"""
    name = sign.get("name", "")
    sentences = [s["text"] for s in sign.get("sentences", []) if s.get("text")]

    # अगाडि राशि नाम, पछाडि वाक्यहरू प्राकृतिक विरामसहित
    parts = [f"{name} राशि।"]
    for i, s in enumerate(sentences):
        # वाक्य बीचमा सानो विराम थप्न "... " जोड्ने
        parts.append(s.strip())
    return "  ".join(parts)


# ───────────────────────────────────────────────────────────
# २. XTTS-v2 मार्फत TTS (GPU छैन भने CPU मा पनि चल्छ)
# ───────────────────────────────────────────────────────────
def run_xtts(text: str, voice_wav: Path, out_wav: Path, language: str = "hi"):
    """Coqui XTTS-v2 ले voice_wav को आवाजमा text बोल्छ → out_wav।
    
    नोट: नेपाली (ne) पूर्ण रूपमा XTTS-v2 ले support गर्दैन,
    'hi' (हिन्दी) ले देवनागरी उच्चारण सबैभन्दा राम्रो गर्छ।
    """
    try:
        from TTS.api import TTS  # pip install TTS
    except ImportError:
        sys.exit(
            "त्रुटि: TTS इन्स्टल छैन।\n"
            "कृपया चलाउनुहोस्: pip install TTS\n"
            "(GitHub Actions मा daily.yml मा थपिनेछ।)"
        )

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  TTS device: {device}", flush=True)

    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    tts.tts_to_file(
        text=text,
        speaker_wav=str(voice_wav),
        language=language,
        file_path=str(out_wav),
        speed=0.90,          # अलि ढिलो → स्पष्ट उच्चारण
        split_sentences=True,
    )
    print(f"  → {out_wav.name} तयार", flush=True)


# ───────────────────────────────────────────────────────────
# ३. Music + Voice मिक्स (ffmpeg amix)
# ───────────────────────────────────────────────────────────
def mix_voice_music(voice_wav: Path, music_wav: Path, out_wav: Path, music_vol: float = 0.18):
    """तपाईंको आवाज (100%) + ब्याकग्राउन्ड धुन (18%) = अन्तिम अडियो।"""
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-i", str(voice_wav),
        "-i", str(music_wav),
        "-filter_complex",
        f"[1:a]volume={music_vol}[bg];[0:a][bg]amix=inputs=2:duration=longest:dropout_transition=2[out]",
        "-map", "[out]",
        "-c:a", "aac", "-b:a", "192k",
        str(out_wav)
    ], check=True)


# ───────────────────────────────────────────────────────────
# ४. Main — content.today.json पढेर सबै राशिको अडियो बनाउने
# ───────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="NepDate Voice TTS")
    ap.add_argument("content", nargs="?", default="content.today.json",
                    help="JSON सामग्री फाइल (default: content.today.json)")
    ap.add_argument("--out", default="videos", help="आउटपुट फोल्डर")
    ap.add_argument("--voice", default=str(VOICE_SAMPLE),
                    help="Voice reference WAV फाइल")
    ap.add_argument("--lang", default="hi",
                    help="TTS भाषा कोड: hi (default) वा ne")
    ap.add_argument("--only", nargs="*", type=int,
                    help="छानिएका राशि नम्बरहरू (१=मेष ... १२=मीन)")
    ap.add_argument("--test", action="store_true",
                    help="टेस्ट मोड: पहिलो राशि मात्र")
    a = ap.parse_args()

    voice_path = Path(a.voice)
    if not voice_path.exists():
        sys.exit(f"त्रुटि: Voice sample भेटिएन: {voice_path}\n"
                 f"कृपया assets/voice_sample.wav राख्नुहोस्।")

    content_path = Path(a.content)
    if not content_path.exists():
        sys.exit(f"त्रुटि: Content फाइल भेटिएन: {content_path}")

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

    print(f"\n🎙️  Voice TTS सुरु — {len(indices)} राशि | Voice: {voice_path.name}\n")

    for idx in indices:
        if idx >= len(signs):
            continue
        sign = signs[idx]
        name = sign.get("name", f"rashi_{idx+1}")
        script = build_script(sign)

        print(f"[{idx+1:02d}/12] {name}: {script[:60]}...")

        raw_wav = out_dir / f"_voice_{idx+1:02d}.wav"
        run_xtts(script, voice_path, raw_wav, language=a.lang)

    print("\n✅  सबै Voice WAV फाइलहरू तयार भए!")
    print(f"   फोल्डर: {out_dir.resolve()}\n")


if __name__ == "__main__":
    main()

