#!/usr/bin/env bash
# NepDate दैनिक राशिफल स्वचालन — OmniVoice Native Nepali Voiceover & Video Render
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "============================================================"
echo "🌟 NepDate दैनिक राशिफल स्वचालन (OmniVoice + Video)"
echo "============================================================"

# १. भर्चुअल इन्भाइरोनमेन्ट छनोट
PYTHON="python3"
if [ -f "$DIR/../.venv/bin/python" ]; then
    PYTHON="$DIR/../.venv/bin/python"
elif [ -f "$DIR/.venv/bin/python" ]; then
    PYTHON="$DIR/.venv/bin/python"
fi

echo "🐍 Python Interpreter: $($PYTHON --version)"

# २. आजको सामग्री तान्ने (Fetch Content)
echo ""
echo "📥 १/३: राशिफल सामग्री तान्दै (Fetch)..."
$PYTHON daily.py --dry --allow-stale --out videos "$@"

# ३. OmniVoice नेपाली भ्वाइसओभर उत्पादन (Voiceover Generation)
echo ""
echo "🎙️ २/३: OmniVoice नेपाली भ्वाइसओभर उत्पादन गर्दै (Exact Screen-Sync)..."
$PYTHON voice_omnivoice.py content.today.json \
    --out videos \
    --instruct "male, young adult, moderate pitch" \
    --seed 253 \
    --speed 0.95 \
    --guidance 1.4 \
    --lang npi

echo ""
echo "✅ भ्वाइसओभर फाइलहरू तयार भए:"
ls -lh videos/_voice_*.wav

# ४. भिडियो रेन्डर (Video Render if Playwright available)
if $PYTHON -c "import playwright" &>/dev/null; then
    echo ""
    echo "🎬 ३/३: भिडियो रेन्डर सुरु गर्दै (Render with Voice)..."
    $PYTHON daily.py --out videos --no-fetch "$@"
    echo ""
    echo "🎉 बधाई छ! भिडियो सफलतापूर्वक तयार भयो:"
    ls -lh videos/*.mp4
else
    echo ""
    echo "ℹ️ स्थानीय प्रणालीमा Playwright/Chromium नभएकाले भिडियो रेन्डर स्किप गरियो।"
    echo "   (सम्पूर्ण भिडियो रेन्डरिङ GitHub Actions मा स्वचालित रूपमा चल्नेछ)"
fi

echo "============================================================"

