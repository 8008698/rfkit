#!/usr/bin/env python3
"""
NepDate दैनिक राशिफल Voice Generator — OmniVoice Native Nepali TTS.
नेपाली भाषा (npi) को लागि प्राकृतिक तथा स्क्रिन-सिङ्क्ड (On-Screen Synchronized) भ्वाइसओभर।

विशेषताहरू:
  - प्रत्येक वाक्य स्क्रिनमा देखा पर्ने बित्तिकै अडियो बोल्ने (Exact Text-to-Screen Sync)
  - इन्ट्रो (Intro) र आउट्रो (Outro) का लागि पनि प्राकृतिक भ्वाइसओभर
  - समानान्तर प्रोसेसिङ (Parallel Shards / Workers) मार्फत तीव्र गति
  - GitHub Actions Matrix को लागि --shard 1/4, 2/4, 3/4, 4/4 सपोर्ट

User Parameters:
  - Instruct: "male, young adult, moderate pitch"
  - Seed: 253
  - Speed: 0.95
  - Guidance scale: 1.4
  - Language: npi (Nepali)

प्रयोग:
  python voice_omnivoice.py content.today.json --out videos
  python voice_omnivoice.py --test                      # मेष राशि मात्र
  python voice_omnivoice.py --intro                     # इन्ट्रो मात्र
  python voice_omnivoice.py --outro                     # आउट्रो मात्र
  python voice_omnivoice.py --shard 1/4                 # Shard 1 (Intro + राशि 1-3)
  python voice_omnivoice.py --parallel --workers 4       # लोकल मल्टि-प्रोसेसिङ
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import soundfile as sf
import torch

HERE = Path(__file__).parent.resolve()
PARENT_DIR = HERE.parent

LOCAL_CANDIDATES = [
    HERE / "models" / "OmniVoice",
    PARENT_DIR / "models" / "OmniVoice",
    Path("/media/computebox/files/projects/voice/models/OmniVoice"),
]

# Timeline Constants from rashifal_video.js
SL_SECONDS = 4.4    # न्यूनतम कार्ड समय (Base duration)
C0_REL = 6.6        # राशि सुरु भएको कति सेकेन्डपछि कार्ड ० देखा पर्ने
INTRO_DURATION = 18.0 # इन्ट्रोको कुल लम्बाइ
OUTRO_DURATION = 10.0 # आउट्रोको कुल लम्बाइ


def calc_card_duration(text: str) -> float:
    """अक्षर संख्याको आधारमा कार्ड स्क्रिनमा रहने समय (सेकेन्ड) गणना गर्छ।"""
    length = len(text.strip())
    # 0.95x बोलीको गतिमा ~12.5 अक्षर प्रति सेकेन्ड + 0.3s सुरुआत
    est_speech = 0.3 + (length / 12.5)
    # वाचनपछि 1.2 सेकेन्ड शान्त विराम (न्यूनतम 4.4 सेकेन्ड)
    return max(4.4, round(est_speech + 1.2, 1))


def resolve_model_path(user_model_arg: Optional[str] = None) -> str:
    """Finds best model path: user arg -> env var -> local path -> huggingface repo id."""
    if user_model_arg:
        p = Path(user_model_arg)
        if p.exists():
            return str(p.resolve())
        return user_model_arg

    env_dir = os.environ.get("OMNIVOICE_MODEL_DIR")
    if env_dir and Path(env_dir).exists():
        return env_dir

    for cand in LOCAL_CANDIDATES:
        if cand.exists() and (cand / "model.safetensors").exists():
            return str(cand.resolve())

    return "k2-fsa/OmniVoice"


def load_model(model_source: str, device: str):
    """Loads OmniVoice model."""
    try:
        from omnivoice.models.omnivoice import OmniVoice
    except ImportError:
        alt_omnivoice = PARENT_DIR / "OmniVoice"
        if alt_omnivoice.exists() and (alt_omnivoice / "omnivoice").exists():
            sys.path.insert(0, str(alt_omnivoice))
            from omnivoice.models.omnivoice import OmniVoice
        else:
            sys.exit(
                "त्रुटि: 'omnivoice' प्याकेज लोड गर्न सकिएन।\n"
                "कृपया चलाउनुहोस्: pip install git+https://github.com/k2-fsa/OmniVoice.git"
            )

    dtype = torch.float16 if device == "cuda" else torch.float32
    print(f"⏳ मोडल लोड हुँदैछ ({model_source}) [{device.upper()}]...", flush=True)
    t0 = time.time()
    model = OmniVoice.from_pretrained(
        model_source,
        device_map=device,
        dtype=dtype,
        load_asr=False
    )
    print(f"✅ मोडल लोड सम्पन्न ({time.time() - t0:.1f}s)", flush=True)
    return model


DEV_TO_LATIN = str.maketrans("०१२३४५६७८९", "0123456789")

WORDS_0_99 = [
    "शून्य", "एक", "दुई", "तीन", "चार", "पाँच", "छ", "सात", "आठ", "नौ",
    "दश", "एघार", "बाह्र", "तेह्र", "चौध", "पन्ध्र", "सोह्र", "सत्र", "अठार", "उन्नाइस",
    "बीस", "एक्काइस", "बाइस", "तेइस", "चौबिस", "पच्चिस", "छब्बीस", "सत्ताइस", "अट्ठाइस", "उनन्तिस",
    "तीस", "एकत्तिस", "बत्तिस", "तेत्तिस", "चौँतिस", "पैँतिस", "छत्तीस", "सैँतिस", "अड्तीस", "उनन्चालीस",
    "चालीस", "एकचालीस", "बयानलीस", "त्रिचालीस", "चौवालिस", "पैँतालीस", "छयालीस", "सत्चालीस", "अड्चालीस", "उनन्पचास",
    "पचास", "एकाउन्न", "बाउन्न", "त्रिपन्न", "चौवन्न", "पचपन्न", "छपन्न", "सन्ताउन्न", "अन्ठाउन्न", "उनन्साठी",
    "साठी", "एकसट्ठी", "बासट्ठी", "त्रिसट्ठी", "चौँसट्ठी", "पैँसट्ठी", "छयसट्ठी", "सतसट्ठी", "अठसट्ठी", "उनन्सत्तरी",
    "सत्तरी", "एकहत्तर", "बहत्तर", "त्रिहत्तर", "चौहत्तर", "पचहत्तर", "छहत्तर", "सतहत्तर", "अठहत्तर", "उन्यासी",
    "असी", "एकासी", "बयासी", "त्रियासी", "चौरासी", "पचासी", "छयासी", "सत्तासी", "अठासी", "उनन्नब्बे",
    "नब्बे", "एकानब्बे", "बयानब्बे", "त्रियानब्बे", "चौरानब्बे", "पन्चानब्बे", "छ्यानब्बे", "सन्तानब्बे", "अन्ठानब्बे", "उनन्सय"
]


def num_to_nepali_words(n: int) -> str:
    """पूर्णाङ्क संख्यालाई नेपाली शब्दमा रूपान्तरण गर्छ।"""
    if n < 0:
        return "माइनस " + num_to_nepali_words(-n)
    if n < 100:
        return WORDS_0_99[n]
    if n < 1000:
        hundreds = n // 100
        rem = n % 100
        h_str = (WORDS_0_99[hundreds] + " सय") if hundreds > 0 else ""
        return (h_str + (" " + num_to_nepali_words(rem) if rem else "")).strip()
    if n < 100000:
        thousands = n // 1000
        rem = n % 1000
        t_str = num_to_nepali_words(thousands) + " हजार"
        return (t_str + (" " + num_to_nepali_words(rem) if rem else "")).strip()
    if n < 10000000:
        lakhs = n // 100000
        rem = n % 100000
        l_str = num_to_nepali_words(lakhs) + " लाख"
        return (l_str + (" " + num_to_nepali_words(rem) if rem else "")).strip()
    crores = n // 10000000
    rem = n % 10000000
    c_str = num_to_nepali_words(crores) + " करोड"
    return (c_str + (" " + num_to_nepali_words(rem) if rem else "")).strip()


def verbalize_numbers(text: str) -> str:
    """कुनै पनि वाक्यमा रहेका अंकहरूलाई देवनागरी शब्दमा रूपान्तरण गर्छ।"""
    import re
    def repl(m):
        raw = m.group(0).translate(DEV_TO_LATIN)
        try:
            return num_to_nepali_words(int(raw))
        except Exception:
            return m.group(0)
    return re.sub(r"[०-९0-9]+", repl, text)


def synthesize_text(
    model,
    text: str,
    instruct: str,
    seed: int,
    speed: float,
    guidance: float,
    lang: str = "npi",
    num_step: int = 16
) -> np.ndarray:
    """Synthesizes clean speech for a single text segment (auto-verbalizing numbers)."""
    verbalized = verbalize_numbers(text.strip())
    torch.manual_seed(seed)
    np.random.seed(seed)
    res = model.generate(
        text=verbalized,
        language=lang,
        instruct=instruct,
        speed=speed,
        guidance_scale=guidance,
        num_step=num_step,
        denoise=True,
        postprocess_output=True
    )
    raw = res[0] if isinstance(res, (list, tuple)) else res
    if isinstance(raw, torch.Tensor):
        raw = raw.detach().cpu().numpy()
    if raw.ndim > 1:
        raw = raw.squeeze()
    return raw.astype(np.float32)


# ───────────────────────────────────────────────────────────
# १. इन्ट्रो (Intro) भ्वाइसओभर — स्क्रिनसँग सिङ्क
# ───────────────────────────────────────────────────────────
def generate_intro_audio(
    model,
    content: dict,
    instruct: str,
    seed: int,
    speed: float,
    guidance: float,
    sr: int = 24000
) -> np.ndarray:
    """
    इन्ट्रो स्क्रिनमा अक्षरहरू देखा पर्ने समयसँग दुरुस्तै मिलाएर अडियो बनाउँछ।
    सबै अंकहरू (वि.सं. र ई.सं. मिति) शुद्ध नेपाली शब्दमा वाचन गरिन्छ।
    - 1.5s: "आजको दैनिक राशिफल।"
    - 3.4s: "विक्रम संवत् दुई हजार त्रियासी साल कार्तिक सोह्र गते सोमवार, तदनुसार सन् दुई हजार छब्बीस नोभेम्बर दश तारिख।"
    - 12.0s: "नेपडेट पात्रोमा यहाँहरुलाई हार्दिक स्वागत छ।"
    - 14.8s: "सुरु गरौं {first_sign} राशिबाट।"
    """
    total_samples = int(INTRO_DURATION * sr)
    timeline = np.zeros(total_samples, dtype=np.float32)

    intro_cfg = content.get("intro", {})
    lines = intro_cfg.get("lines", [
        "नेपडेट पात्रोमा यहाँहरुलाई हार्दिक स्वागत छ।",
        "भिडियो अन्त्यसम्म हेर्नुहोला।"
    ])
    d = content.get("date", {})
    bs_year = d.get("year", "२०८३")
    bs_month = d.get("month", "कार्तिक")
    bs_day = d.get("day", "१६")
    weekday = d.get("weekday", "सोमवार")
    ad_spoken = d.get("ad_spoken", f"सन् {d.get('ad_year', '२०२६')} {d.get('ad_month', 'नोभेम्बर')} {d.get('ad_day', '१०')} तारिख")
    first_sign = content.get("signs", [{}])[0].get("name", "मेष")

    # Cue 1: t = 1.5s - आजको दैनिक राशिफल
    a1 = synthesize_text(model, "आजको दैनिक राशिफल।", instruct, seed, speed, guidance)
    i1 = int(1.5 * sr)
    timeline[i1 : i1 + len(a1)] = a1[: total_samples - i1]

    # Cue 2: t = 3.4s - मिति (वि.सं. र तदनुसार ईस्वी संवत् AD मिति पूर्ण नेपाली शब्दमा)
    date_speech = d.get("full_spoken")
    if not date_speech:
        bs_spoken = d.get("bs_spoken") or f"विक्रम संवत् {bs_year} साल {bs_month} {bs_day} गते {weekday}"
        date_speech = f"{bs_spoken}, तदनुसार {ad_spoken}।"
    date_speech = verbalize_numbers(date_speech)
    a2 = synthesize_text(model, date_speech, instruct, seed + 2, speed, guidance)
    i2 = int(3.4 * sr)
    timeline[i2 : i2 + len(a2)] = a2[: total_samples - i2]

    # Cue 3: t = 12.0s - स्वागत सन्देश
    welcome_text = "नेपडेट पात्रोमा यहाँहरुलाई हार्दिक स्वागत छ।"
    if lines and len(lines) > 0:
        welcome_text = lines[0]
    a3 = synthesize_text(model, welcome_text, instruct, seed + 5, speed, guidance)
    i3 = int(12.0 * sr)
    timeline[i3 : i3 + len(a3)] = a3[: total_samples - i3]

    # Cue 4: t = 14.8s - सुरु गरौं पहिलो राशिबाट
    a4 = synthesize_text(model, f"सुरु गरौं {first_sign} राशिबाट।", instruct, seed + 8, speed, guidance)
    i4 = int(14.8 * sr)
    timeline[i4 : i4 + len(a4)] = a4[: total_samples - i4]

    return timeline


# ───────────────────────────────────────────────────────────
# २. एक राशिको भ्वाइसओभर — प्रत्येक कार्डसँग सिङ्क
# ───────────────────────────────────────────────────────────
def generate_sign_audio(
    model,
    sign: dict,
    idx: int,
    instruct: str,
    seed: int,
    speed: float,
    guidance: float,
    sr: int = 24000
) -> Tuple[np.ndarray, float, List[float]]:
    """
    एक राशिको प्रत्येक वाक्यको लम्बाइ अनुसार कार्डको समय बढाएर बिना कुनै कट-अफ
    स्पष्ट र प्राकृतिक रूपमा भ्वाइसओभर तयार गर्छ।
    """
    name = sign.get("name", "").strip()
    sents = [s["text"].strip() for s in sign.get("sentences", []) if s.get("text")]
    if not sents:
        sents = ["आजको राशिफल उपलब्ध छैन।"]

    # १. राशि नाम (t = 1.0s)
    a_name = synthesize_text(model, f"{name} राशि।", instruct, seed + idx * 20, speed, guidance)

    # २. प्रत्येक वाक्य सिन्थेसाइज गर्ने (NO CUTOFF! वास्तविक अडियो अनुसार समय निर्धारण)
    chunks_audio = []
    card_durations = []
    for c_i, sent in enumerate(sents):
        chunk_audio = synthesize_text(
            model,
            sent,
            instruct,
            seed + idx * 20 + (c_i + 1) * 3,
            speed,
            guidance
        )
        audio_dur = len(chunk_audio) / float(sr)
        # Dynamic card duration: text length estimate vs actual audio duration + 1.2s pause
        c_dur = max(calc_card_duration(sent), round(audio_dur + 1.2, 1))
        chunks_audio.append(chunk_audio)
        card_durations.append(c_dur)

    total_dur = C0_REL + sum(card_durations) + 0.8
    total_samples = int(total_dur * sr)
    timeline = np.zeros(total_samples, dtype=np.float32)

    # राशि नाम राख्ने (t = 1.0s)
    i_name = int(1.0 * sr)
    timeline[i_name : i_name + len(a_name)] = a_name[: total_samples - i_name]

    # प्रत्येक वाक्य आफ्नो कार्ड फ्लिप हुँदा राख्ने (तुरुन्तै सुरु, कुनै कट-अफ बिना)
    cur_t = C0_REL
    for chunk_audio, c_dur in zip(chunks_audio, card_durations):
        t_card = cur_t + 0.2
        i_card = int(t_card * sr)
        end_c = min(total_samples, i_card + len(chunk_audio))
        timeline[i_card : end_c] = chunk_audio[: end_c - i_card]
        cur_t += c_dur

    return timeline, total_dur, card_durations


# ───────────────────────────────────────────────────────────
# ३. आउट्रो (Outro) भ्वाइसओभर — स्क्रिनसँग सिङ्क
# ───────────────────────────────────────────────────────────
def generate_outro_audio(
    model,
    content: dict,
    instruct: str,
    seed: int,
    speed: float,
    guidance: float,
    sr: int = 24000
) -> np.ndarray:
    """
    आउट्रो लोगो, ब्रान्डिङ र एप डाउनलोडसँग सिङ्क गरेर अडियो बनाउँछ।
    भिडियो सकिनुभन्दा अगाडि नै अडियो प्राकृतिक रूपमा समाप्त हुन्छ (audio ends before video)।
    - 0.8s: "{tagline}, नेपडेट।"
    - 2.4s: "आजै गुगल प्ले स्टोरबाट नेपडेट डाउनलोड गर्नुहोस्। धन्यवाद, शुभ दिन रहोस्।"
    (अडियो ~7.6s मा सकिन्छ, भिडियो 10.0s सम्म जारी रहन्छ र अन्त्यमा कालो फेड आउट हुन्छ)
    """
    total_samples = int(OUTRO_DURATION * sr)
    timeline = np.zeros(total_samples, dtype=np.float32)

    tag = content.get("tagline", "हरेक दिनको विश्वास")

    # Cue 1: t = 0.8s
    a1 = synthesize_text(model, f"{tag}, नेपडेट।", instruct, seed, speed, guidance)
    i1 = int(0.8 * sr)
    timeline[i1 : i1 + len(a1)] = a1[: total_samples - i1]

    # Cue 2: t = 2.4s
    outro_cta = "आजै गुगल प्ले स्टोरबाट नेपडेट डाउनलोड गर्नुहोस्। धन्यवाद, शुभ दिन रहोस्।"
    a2 = synthesize_text(model, outro_cta, instruct, seed + 4, speed, guidance)
    i2 = int(2.4 * sr)
    timeline[i2 : i2 + len(a2)] = a2[: total_samples - i2]

    return timeline


# ───────────────────────────────────────────────────────────
# ४. Main Pipeline & Shard Splitter
# ───────────────────────────────────────────────────────────
def parse_shard(shard_str: str) -> Tuple[int, int]:
    """Parses 'X/Y' e.g. '1/4' -> (1, 4)."""
    parts = shard_str.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid shard format '{shard_str}'. Expected 'X/Y' e.g. '1/4'.")
    curr, total = int(parts[0]), int(parts[1])
    if curr < 1 or curr > total:
        raise ValueError(f"Shard index {curr} out of range 1..{total}.")
    return curr, total


def main():
    ap = argparse.ArgumentParser(description="NepDate Rashifal Voice TTS — OmniVoice Native Nepali")
    ap.add_argument("content", nargs="?", default="content.today.json",
                    help="JSON सामग्री फाइल (default: content.today.json)")
    ap.add_argument("--out", default="videos", help="आउटपुट अडियो फोल्डर (default: videos)")
    ap.add_argument("--model", default=None,
                    help="OmniVoice मोडल बाटो वा HF repo (default: auto-detected local/hf)")
    ap.add_argument("--instruct", default="male, young adult, moderate pitch",
                    help="भ्वाइस स्टाइल प्रम्प्ट (default: 'male, young adult, moderate pitch')")
    ap.add_argument("--seed", type=int, default=253,
                    help="Random seed (default: 253)")
    ap.add_argument("--speed", type=float, default=0.95,
                    help="बोलीको गति (default: 0.95)")
    ap.add_argument("--guidance", type=float, default=1.4,
                    help="Guidance scale (default: 1.4)")
    ap.add_argument("--lang", default="npi",
                    help="भाषा कोड (default: npi - नेपाली)")
    ap.add_argument("--num-step", type=int, default=16,
                    help="CFM inference steps (default: 16)")
    ap.add_argument("--only", nargs="*", type=int,
                    help="छानिएका राशि नम्बरहरू (१=मेष ... १२=मीन)")
    ap.add_argument("--test", action="store_true",
                    help="टेस्ट मोड: पहिलो राशि (मेष) मात्र")
    ap.add_argument("--intro", action="store_true",
                    help="इन्ट्रो भ्वाइस (_voice_intro.wav) मात्र बनाउने")
    ap.add_argument("--outro", action="store_true",
                    help="आउट्रो भ्वाइस (_voice_outro.wav) मात्र बनाउने")
    ap.add_argument("--shard", default=None,
                    help="GitHub Actions Matrix shard (e.g. 1/4, 2/4, 3/4, 4/4)")
    ap.add_argument("--concat-full", action="store_true",
                    help="सबै अडियो जोडेर एउटै _voice_full.wav फाइल पनि बनाउने")
    ap.add_argument("--device", default=None,
                    help="Device override: cpu, cuda, xpu (default: auto)")

    args = ap.parse_args()

    content_path = Path(args.content)
    if not content_path.is_absolute():
        content_path = HERE / content_path

    if not content_path.exists():
        sys.exit(f"त्रुटि: सामग्री फाइल भेटिएन: {content_path}\n"
                 f"कृपया पहिले 'python daily.py --dry' चलाउनुहोस्।")

    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = HERE / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # Device
    if args.device:
        device = args.device
    elif torch.cuda.is_available():
        device = "cuda"
    elif hasattr(torch, "xpu") and torch.xpu.is_available():
        device = "xpu"
    else:
        device = "cpu"

    model_source = resolve_model_path(args.model)

    print(f"============================================================")
    print(f"🎙️  OmniVoice Native Nepali On-Screen Synced Voice Engine")
    print(f"⚙️  Device:         {device.upper()}")
    print(f"📦  Model Source:   {model_source}")
    print(f"👤  Voice Style:    '{args.instruct}'")
    print(f"🎲  Seed:           {args.seed}")
    print(f"⚡  Speed:          {args.speed}x")
    print(f"🎯  Guidance:       {args.guidance}")
    print(f"🌐  Language:       {args.lang}")
    if args.shard:
        print(f"⚡  Matrix Shard:   {args.shard} (Parallel Processing)")
    print(f"============================================================", flush=True)

    with open(content_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    signs = content.get("signs", [])

    # Determine tasks
    do_intro = False
    do_outro = False
    sign_indices = []

    if args.intro:
        do_intro = True
    elif args.outro:
        do_outro = True
    elif args.test:
        sign_indices = [0]
    elif args.only:
        sign_indices = [i - 1 for i in args.only]
    elif args.shard:
        curr_shard, total_shards = parse_shard(args.shard)
        # 14 total tasks: 0=intro, 1..12=signs, 13=outro
        all_tasks = ["intro"] + list(range(len(signs))) + ["outro"]
        
        # Split evenly among total_shards
        # e.g. 14 tasks with 4 shards: [0..3], [4..6], [7..9], [10..13]
        n = len(all_tasks)
        shard_tasks = [all_tasks[i] for i in range(n) if i % total_shards == (curr_shard - 1)]
        
        for t in shard_tasks:
            if t == "intro":
                do_intro = True
            elif t == "outro":
                do_outro = True
            elif isinstance(t, int):
                sign_indices.append(t)
        print(f"📌 Shard {curr_shard}/{total_shards} Tasks: {shard_tasks}", flush=True)
    else:
        do_intro = True
        do_outro = True
        sign_indices = list(range(len(signs)))

    # Load Model
    model = load_model(model_source, device)
    sr = getattr(model, "sampling_rate", 24000)

    # 1. Intro
    if do_intro:
        print(f"\n🎬 [Intro] स्क्रिन-सिङ्क्ड इन्ट्रो भ्वाइसओभर तयार गर्दै...", flush=True)
        t0 = time.time()
        intro_wav = generate_intro_audio(model, content, args.instruct, args.seed, args.speed, args.guidance, sr)
        intro_path = out_dir / "_voice_intro.wav"
        sf.write(str(intro_path), intro_wav, sr)
        print(f"   ✓ {intro_path.name} तयार ({len(intro_wav)/sr:.1f}s, taken {time.time()-t0:.1f}s)", flush=True)

    # 2. Signs
    if sign_indices:
        print(f"\n♈ [Signs] कुल {len(sign_indices)} राशिका लागि स्क्रिन-सिङ्क्ड भ्वाइसओभर सुरु...", flush=True)
        for s_idx in sign_indices:
            if s_idx >= len(signs):
                continue
            sign = signs[s_idx]
            name = sign.get("name", f"rashi_{s_idx+1}")
            out_wav = out_dir / f"_voice_{s_idx+1:02d}.wav"

            print(f"   [{s_idx+1:02d}/12] {name} राशि: पाठ अनुसार कार्डको समय सिङ्किङ...", flush=True)
            t_s = time.time()
            s_audio, s_dur, c_durs = generate_sign_audio(
                model, sign, s_idx, args.instruct, args.seed, args.speed, args.guidance, sr
            )
            sf.write(str(out_wav), s_audio, sr)

            # Save timing metadata for video renderer
            timing_file = out_dir / f"_timing_sign_{s_idx+1:02d}.json"
            timing_file.write_text(
                json.dumps({"si": s_idx, "name": name, "durations": c_durs, "total_dur": s_dur}, indent=2),
                encoding="utf-8"
            )

            # Update content sentences with exact durations
            for c_i, dur_val in enumerate(c_durs):
                if c_i < len(signs[s_idx].get("sentences", [])):
                    signs[s_idx]["sentences"][c_i]["dur"] = dur_val

            print(f"       ✓ {out_wav.name} तयार ({s_dur:.1f}s, कार्ड समयहरू: {c_durs}, time: {time.time()-t_s:.1f}s)", flush=True)

        # Update content.today.json with dynamic durations
        try:
            content_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    # 3. Outro
    if do_outro:
        print(f"\n🏁 [Outro] स्क्रिन-सिङ्क्ड आउट्रो भ्वाइसओभर तयार गर्दै...", flush=True)
        t0 = time.time()
        outro_wav = generate_outro_audio(model, content, args.instruct, args.seed, args.speed, args.guidance, sr)
        outro_path = out_dir / "_voice_outro.wav"
        sf.write(str(outro_path), outro_wav, sr)
        print(f"   ✓ {outro_path.name} तयार ({len(outro_wav)/sr:.1f}s, taken {time.time()-t0:.1f}s)", flush=True)

    print(f"\n🎉 सम्पन्न भयो! तयार भएका फाइलहरू: {out_dir}")
    for f in sorted(out_dir.glob("_voice_*.wav")):
        print(f"   • {f.name} ({f.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
