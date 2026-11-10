#!/usr/bin/env python3
"""NepDate राशिफल Voice TTS — OmniVoice (नेपाली) र XTTS-v2 इन्जिन।

Default Settings (OmniVoice Native Nepali):
  - Instruct: "male, young adult, moderate pitch"
  - Seed: 253
  - Speed: 0.95
  - Guidance: 1.4
  - Language: npi

प्रयोग:
  python voice_tts.py content.today.json --out videos
  python voice_tts.py --test                                  # पहिलो राशि टेस्ट (मेष)
  python voice_tts.py --engine xtts --voice assets/voice_sample.wav  # लिगेसी Coqui XTTS
"""
import os
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).parent.resolve()
VOICE_SAMPLE = HERE / "assets" / "voice_sample.wav"


def main():
    ap = argparse.ArgumentParser(description="NepDate Voice TTS Engine")
    ap.add_argument("content", nargs="?", default="content.today.json",
                    help="JSON सामग्री फाइल (default: content.today.json)")
    ap.add_argument("--out", default="videos", help="आउटपुट फोल्डर")
    ap.add_argument("--engine", default="omnivoice", choices=["omnivoice", "xtts"],
                    help="TTS इन्जिन: omnivoice (नेपाली) वा xtts (Coqui)")
    ap.add_argument("--voice", default=str(VOICE_SAMPLE),
                    help="Voice reference WAV फाइल (XTTS-v2 का लागि)")
    ap.add_argument("--instruct", default="male, young adult, moderate pitch",
                    help="OmniVoice भ्वाइस स्टाइल (default: 'male, young adult, moderate pitch')")
    ap.add_argument("--seed", type=int, default=253,
                    help="Random seed (default: 253)")
    ap.add_argument("--speed", type=float, default=None,
                    help="बोलीको गति (default: 0.95 for omnivoice, 0.92 for xtts)")
    ap.add_argument("--guidance", type=float, default=1.4,
                    help="OmniVoice guidance scale (default: 1.4)")
    ap.add_argument("--lang", default=None,
                    help="TTS भाषा कोड (default: npi for omnivoice, hi for xtts)")
    ap.add_argument("--only", nargs="*", type=int,
                    help="छानिएका राशि नम्बरहरू (१=मेष ... १२=मीन)")
    ap.add_argument("--test", action="store_true",
                    help="टेस्ट मोड: पहिलो राशि मात्र")
    ap.add_argument("--concat-full", action="store_true",
                    help="सबै राशिको एउटै अडियो फाइल (_voice_full.wav) बनाउने")
    a = ap.parse_args()

    if a.engine == "omnivoice":
        import voice_omnivoice
        speed = a.speed if a.speed is not None else 0.95
        lang = a.lang if a.lang is not None else "npi"

        # Re-pack arguments for voice_omnivoice
        sys.argv = [
            "voice_omnivoice.py",
            str(a.content),
            "--out", str(a.out),
            "--instruct", str(a.instruct),
            "--seed", str(a.seed),
            "--speed", str(speed),
            "--guidance", str(a.guidance),
            "--lang", str(lang),
        ]
        if a.test:
            sys.argv.append("--test")
        if a.only:
            sys.argv.extend(["--only"] + [str(x) for x in a.only])
        if a.concat_full:
            sys.argv.append("--concat-full")
        voice_omnivoice.main()
        return

    # ── Legacy Coqui XTTS-v2 Mode ──
    os.environ["COQUI_TOS_AGREED"] = "1"
    import json, time

    voice_path = Path(a.voice)
    if not voice_path.exists():
        sys.exit(f"त्रुटि: Voice sample भेटिएन: {voice_path}\n"
                 f"कृपया assets/voice_sample.wav राख्नुहोस्।")

    content_path = Path(a.content)
    if not content_path.exists():
        sys.exit(f"त्रुटि: Content फाइल भेटिएन: {content_path}")

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
    print(f"🎙️  XTTS Device: {device} | Voice Sample: {voice_path.name}", flush=True)

    content = json.load(open(content_path, encoding="utf-8"))
    signs = content.get("signs", [])
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if a.test:
        indices = [0]
    elif a.only:
        indices = [i - 1 for i in a.only]
    else:
        indices = list(range(len(signs)))

    speed = a.speed if a.speed is not None else 0.92
    lang = a.lang if a.lang is not None else "hi"

    import voice_omnivoice
    build_script = voice_omnivoice.build_script

    print("⏳ XTTS-v2 मोडल मेमोरीमा लोड गर्दैछ...", flush=True)
    t_load_start = time.time()
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    print(f"✅ मोडल लोड भयो ({time.time() - t_load_start:.1f}s)", flush=True)

    print(f"\n--- {len(indices)} राशिका लागि XTTS भ्वाइस क्लोनिङ सुरु ---\n", flush=True)
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
            language=lang,
            file_path=str(out_wav),
            speed=speed,
            split_sentences=True,
        )
        print(f"       ✓ {out_wav.name} तयार ({time.time() - t_synth:.1f}s)", flush=True)

    print(f"\n✅ सबै भ्वाइस फाइलहरू सफलतापूर्वक तयार भए: {out_dir}\n", flush=True)


if __name__ == "__main__":
    main()
