# NepDate दैनिक राशिफल भिडियो किट र स्टुडियो (Automated Rashifal Video Kit & Studio)

स्वचालित रूपमा दैनिक नेपाली राशिफल भिडियो (१०८०×१०८० MP4/WebM, आकर्षक वैदिक एनिमेसन, शुभ रङ्ग, शुभ अङ्क, तारा, राशि तस्बिर र बाँसुरी-तानपुरा सङ्गीत सहित) उत्पादन गर्ने किट।

यो किट **१००% स्थानीय (Local First)**, **ब्राउजर/जाभास्क्रिप्ट स्टुडियो (Web UI / GitHub Pages)**, र **GitHub Actions क्लाउड पाइपलाइन** तीनवटै तरिकाबाट चलाउन मिल्ने गरी तयार पारिएको छ।

---

## १. जाभास्क्रिप्ट स्टुडियो (Complete Web Studio & Editor - `index.html`)

ब्राउजरबाटै सबै प्रक्रिया नियन्त्रण गर्न सकिने आधुनिक वेब स्टुडियो `rashifal-kit/index.html` मा उपलब्ध छ।

### मुख्य सुविधाहरू:
1. **१००% Self-Contained**: सबै १२ राशिका तस्बिर, लोगो र ब्याड्ज बेस६४ (Base64) मा इनलाइन छन्। कुनै बाह्य सर्भर वा इमेज फाइल आवश्यक पर्दैन (अफ्लाइन पनि खुल्छ)।
2. **प्रक्रिया र डेटा स्रोत नियन्त्रण (Process Control)**:
   - **स्थानीय JSON फाइल अपलोड**: कम्प्युटरमा भएको कुनै पनि NepDate JSON फाइल (e.g. `nepdate_2026-09-15.json`) छानेर सिधै १२ राशि लोड गर्ने सुविधा।
   - **Enterprise API**: API Key प्रयोग गर्ने विकल्प।
   - **API उपलब्धता र लेटेन्सी इन्डिकेटर**: हरियो पिलले API सक्रिय रहेको देखाउँछ।
3. **लाइभ पूर्वावलोकन र स्क्रबर (Live 1080×1080 Preview)**:
   - कुनै पनि स्क्रिन साइजमा आफैँ स्केलिङ हुने १:१ स्टेज।
   - Web Animations API मार्फत कुनै पनि मिलिसेकेन्डमा टाइमलाइन स्क्रबिङ।
   - मोड छनोट: इन्ट्रो + मेष, छानिएको राशि, मीन + आउट्रो, वा पूरा भिडियो।
4. **राशि सम्पादक (Full Editor)**:
   - १२ राशिका ट्याबहरू (मेष देखि मीन)।
   - तारा मूल्याङ्कन (★ १ देखि ५ र शून्य)।
   - **शुभ रङ्ग (Shubha Color)** र रङ्ग पिकर (`<input type="color">`)।
   - **शुभ अङ्क (Shubha Number)** देवनागरी अङ्कमा।
   - भविष्यवाणी वाक्यहरू, श्रेणी छनोट (`यात्रा`, `स्वास्थ्य`, `परिवार`, `सम्बन्ध`, `आर्थिक`, `कार्यक्षेत्र`, `आजको सन्देश`), र थप/हटाउने सुविधा।
5. **ब्राउजरमै भिडियो बनाउने (In-Browser Client-Side Render)**:
   - कुनै सर्भर वा Python/FFmpeg बिना, ब्राउजरको MediaRecorder बाट सिधै WebM वा MP4 भिडियो उत्पादन।
   - प्रगति बार (Progress Bar) र सिधा भिडियो डाउनलोड।
6. **GitHub Actions सिधा आह्वान (Cloud Dispatch & Instant Download)**:
   - ब्राउजरबाटै एक क्लिकमा GitHub Actions workflow चलाउने (`workflow_dispatch`)।
   - हरेक ५ सेकेन्डमा स्थिति पोलिङ (Queued → Running → Completed)।
   - भिडियो तयार हुनासाथ **तयार भिडियो डाउनलोड गर्नुहोस् (Download MP4)** बटन देखाउने।
7. **कच्चा JSON कोड**:
   - एक क्लिकमा JSON कपी, नयाँ JSON लोड, वा नमुना रिसेट।

---

## २. GitHub Pages मा होस्ट गर्ने तरिका (GitHub Pages Deployment)

यस किटमा `.github/workflows/pages.yml` समावेश छ। तपाईंले नयाँ GitHub Repo मा कोड पुश गर्नासाथ GitHub Pages आफैँ सक्रिय हुन्छ:

```bash
cd /media/computebox/files/projects/new/nepdate-api-source/rashifal-kit

# नयाँ git repo सुरु गर्ने:
git init
git add .
git commit -m "feat: Automated NepDate Rashifal Video Kit & Studio"
git branch -M main
git remote add origin https://github.com/<YOUR-USERNAME>/<YOUR-REPO-NAME>.git
git push -u origin main
```

GitHub रिपोको `Settings` → `Pages` मा गएर **Source: GitHub Actions** छान्नुहोस्। त्यसपछि तपाईंको वेब स्टुडियो निम्न ठेगानामा खुल्नेछ:
`https://<YOUR-USERNAME>.github.io/<YOUR-REPO-NAME>/`

---

## ३. स्थानीय कम्प्युटरमा चलाउने (Python Local-First Pipeline)

### आवश्यक सफ्टवेयर:
```bash
sudo apt update && sudo apt install -y ffmpeg fonts-noto-core fonts-noto-cjk
pip install -r requirements.txt
playwright install chromium
```

### स्थानीय डेटाबाट अफ्लाइन चलाउने:
```bash
# १. सामग्री मात्र परीक्षण गर्ने (Dry run):
python daily.py --file ../data/nepdate/nepdate_2026-09-15.json --dry

# २. छिटो टेस्ट (२-३ सेकेन्डमा मुख्य फ्रेमका फोटो मात्र हेर्ने):
python daily.py --file ../data/nepdate/nepdate_2026-09-15.json --test --only 1

# ३. छानिएको राशि मात्र भिडियो बनाउने (e.g. मेष र वृष):
python daily.py --file ../data/nepdate/nepdate_2026-09-15.json --only 1 2

# ४. १२ वटै राशिको पूरा भिडियो रेन्डर गर्ने:
python daily.py --file ../data/nepdate/nepdate_2026-09-15.json
```

### NepDate API बाट चलाउने:
```bash
# आजको मितिमा:
python daily.py --dry

# कुनै निश्चित मितिमा:
python daily.py --date 2026-09-15 --dry
```

---

## ४. OmniVoice नेपाली भ्वाइसओभर (Native Nepali Synced Voice)

यस किटमा **OmniVoice** न्यूरल टीटीएस इन्जिन समावेश गरिएको छ, जसले शुद्ध तथा स्पष्ट नेपाली (`npi`) उच्चारणमा स्क्रिन-सिङ्क्ड भ्वाइसओभर उत्पादन गर्छ।

### पूर्वनिर्धारित भ्वाइस सेटिङहरू:
- **भ्वाइस स्टाइल (Instruct):** `male, young adult, moderate pitch`
- **रेन्डम सिड (Seed):** `253` (सधैँ उस्तै सुसंगत आवाज)
- **बोलीको गति (Speed):** `0.95x`
- **गाइडेन्स (Guidance):** `1.4`
- **भाषा (Language):** `npi` (नेपाली)

### मुख्य विशेषताहरू:
1. **पाठको लम्बाइ अनुसार गतिशील समय (Dynamic Card Duration - No Audio Cutoff):**
   - लामा वाक्यहरूमा आवाज नटुक्रियोस् (कट-अफ नहोस्) भन्नका लागि अक्षर संख्या तथा वाचन अवधिको आधारमा कार्ड स्क्रिनमा रहने समय आफैँ समायोजन (Dynamic Scaling) हुन्छ।
   - व्हिल खुल्दा: `{name} राशि` उच्चारण।
   - कार्ड १ स्क्रिनमा आउँदा: वाक्य १ वाचन (पूरा बोलेर शान्त विराम भएपछि मात्र अर्को कार्ड आउने)।
   - कार्ड २, ३, ४ स्क्रिनमा फ्लिप हुँदा सोही वाक्यहरू दुरुस्तै वाचन।
2. **इन्ट्रो र आउट्रो भ्वाइसओभर:**
   - **इन्ट्रो (`_voice_intro.wav` - १६ सेकेन्ड):** शीर्षक खुल्दा "आजको दैनिक राशिफल", त्यसपछि विक्रम संवत् (वि.सं.) तथा तदनुसार ईस्वी संवत् (AD) मिति वाचन, स्वागत सन्देश र पहिलो राशिको घोषणा।
   - **आउट्रो (`_voice_outro.wav` - १० सेकेन्ड):** आकर्षक एनिमेटेड ब्रान्डिङ, पञ्चाङ्ग/कुण्डली/साइत सुविधाहरू, र गुगल प्ले डाउनलोड ब्याड्ज; अडियो ७.६ सेकेन्डमै सकिएर २.४ सेकेन्ड शान्त विश्रामपछि भिडियो कालो पर्दामा स्मूथ फेड आउट (Fade out to black) हुन्छ।
3. **क्लाउडमा समानान्तर प्रोसेसिङ (4-Shard Parallel Speedup):**
   - GitHub Actions मा ४ वटा Shards (`shard: [1, 2, 3, 4]`) एकैपटक समानान्तर रूपमा चल्छन्।
   - १२ वटै राशि, इन्ट्रो र आउट्रो केही मिनेटमै तयार हुन्छन्।

---

## ५. GitHub Actions दैनिक स्वचालन (Daily Cron Pipeline)

`.github/workflows/daily.yml` ले हरेक दिन नेपाली समय **बिहान ५:०० (UTC 23:15)** मा आफैँ चल्छ:
1. **Fetch Job:** दिनको ताजा राशिफल तान्छ र `content.today.json` बनाउँछ।
2. **Voice Job (4 Shards in Parallel):** ४ वटा भर्चुअल मेसिनले एकैसाथ १२ वटै राशि, इन्ट्रो र आउट्रोको OmniVoice अडियो बनाउँछन्।
3. **Render Job:** सबै अडियो जोडेर १०८०×१०८० MP4 भिडियो बनाउँछ र GitHub Releases मा अपलोड गर्छ।
4. चाहेको बेला `workflow_dispatch` मार्फत कुनै पनि मितिको भिडियो हातैले उत्पादन गर्न सकिन्छ।
