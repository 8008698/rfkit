# NepDate दैनिक राशिफल भिडियो किट र स्टुडियो (Automated Rashifal Video Kit & Studio)

स्वचालित रूपमा दैनिक नेपाली राशिफल भिडियो (१०८०×१०८० MP4/WebM, आकर्षक वैदिक एनिमेसन, शुभ रङ्ग, शुभ अङ्क, तारा, राशि तस्बिर र बाँसुरी-तानपुरा सङ्गीत सहित) उत्पादन गर्ने किट।

यो किट **१००% स्थानीय (Local First)**, **ब्राउजर/जाभास्क्रिप्ट स्टुडियो (Web UI / GitHub Pages)**, र **GitHub Actions क्लाउड पाइपलाइन** तीनवटै तरिकाबाट चलाउन मिल्ने गरी तयार पारिएको छ।

---

## १. जाभास्क्रिप्ट स्टुडियो (Complete Web Studio & Editor - `index.html`)

ब्राउजरबाटै सबै प्रक्रिया नियन्त्रण गर्न सकिने आधुनिक वेब स्टुडियो `rashifal-kit/index.html` मा उपलब्ध छ।

### मुख्य सुविधाहरू:
1. **१००% Self-Contained**: सबै १२ राशिका तस्बिर, लोगो र ब्याड्ज बेस६४ (Base64) मा इनलाइन छन्। कुनै बाह्य सर्भर वा इमेज फाइल आवश्यक पर्दैन (अफ्लाइन पनि खुल्छ)।
2. **प्रक्रिया र डेटा स्रोत नियन्त्रण (Process Control)**:
   - **निःशुल्क NepDate AI API**: कुनै API Key बिना सिधै ताजा डेटा तान्ने सुविधा (CORS Open)।
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

### निःशुल्क NepDate AI API बाट चलाउने:
```bash
# आजको मितिमा:
python daily.py --dry

# कुनै निश्चित मितिमा:
python daily.py --date 2026-09-15 --dry
```

---

## ४. GitHub Actions दैनिक स्वचालन (Daily Cron Pipeline)

`.github/workflows/daily.yml` ले हरेक दिन नेपाली समय **बिहान ५:१५ (UTC 23:30)** मा आफैँ चल्छ:
1. दिनको राशिफल तान्छ।
2. तानपुरा-बाँसुरी सङ्गीत सहित १०८०×१०८० MP4 भिडियो बनाउँछ।
3. GitHub Releases मा `daily-YYYYMMDD-HHMM` ट्याग सहित फोन-मैत्री डाउनलोड लिङ्क अपलोड गर्छ।
4. चाहेको बेला `workflow_dispatch` मार्फत मिति (`date`) र राशि (`only`) दिएर जुनसुकै बेला चलाउन सकिन्छ।
