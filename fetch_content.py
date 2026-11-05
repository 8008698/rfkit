"""NepDate API / स्थानीय JSON बाट आजको राशिफल तानेर content.json मा मिलाउने।
config.json को "api" भागले API/स्थानीय ठेगाना र JSON को बनावट बताउँछ।"""
import json, os, re, urllib.request

NAMES = [
    ["मेष", "aries", "mesh", "mesha", "mes"],
    ["वृष", "वृषभ", "taurus", "brish", "brisha", "vrish", "vrishabha", "brishabh"],
    ["मिथुन", "gemini", "mithun", "mithuna"],
    ["कर्कट", "कर्क", "cancer", "karkat", "karka", "kark"],
    ["सिंह", "leo", "singha", "simha", "sinha"],
    ["कन्या", "virgo", "kanya"],
    ["तुला", "libra", "tula"],
    ["वृश्चिक", "scorpio", "brischik", "vrishchik", "vrishchika", "brishchik"],
    ["धनु", "sagittarius", "dhanu"],
    ["मकर", "capricorn", "makar"],
    ["कुम्भ", "कुंभ", "aquarius", "kumbha", "kumbh"],
    ["मीन", "pisces", "meen", "min"]
]

COLOR_HEX_MAP = {
    "रातो": "#E53E3E", "लाल": "#E53E3E", "red": "#E53E3E",
    "गुलाबी": "#EC4899", "pink": "#EC4899",
    "सिन्दुरे": "#DC2626", "सिन्दुर": "#DC2626", "सिंदूरी": "#DC2626", "coral": "#F87171",
    "कलेजी": "#991B1B", "maroon": "#991B1B",
    "पहेँलो": "#F59E0B", "पहेलो": "#F59E0B", "पीला": "#F59E0B", "yellow": "#F59E0B",
    "सुनौलो": "#D97706", "सुनहरा": "#D97706", "gold": "#D97706", "golden": "#D97706",
    "सुन्तला": "#F97316", "नारंगी": "#F97316", "orange": "#F97316",
    "केशरी": "#EA580C", "केसरिया": "#EA580C", "saffron": "#EA580C",
    "हरियो": "#10B981", "हरा": "#10B981", "green": "#10B981",
    "गाढा हरियो": "#047857", "गहरा हरा": "#047857", "हल्का हरियो": "#34D399", "हल्का हरा": "#34D399", "emerald": "#059669",
    "नीलो": "#3B82F6", "नीला": "#3B82F6", "blue": "#3B82F6",
    "आकाशी": "#06B6D4", "आसमानी": "#06B6D4", "sky blue": "#06B6D4", "हल्का नीलो": "#60A5FA", "navy": "#1E3A8A",
    "बैजनी": "#8B5CF6", "बैंगनी": "#8B5CF6", "purple": "#8B5CF6",
    "सेतो": "#94A3B8", "सफेद": "#94A3B8", "white": "#94A3B8",
    "चाँदी": "#A0AEC0", "चांदी": "#A0AEC0", "silver": "#A0AEC0",
    "क्रिम": "#FDE68A", "क्रीम": "#FDE68A", "cream": "#FDE68A",
    "कालो": "#334155", "काला": "#334155", "black": "#334155"
}

DEV_MAP = str.maketrans("0123456789", "०१२३४५६७८९")

FALLBACK_COLORS = [
    ("रातो", "#E53E3E"), ("सेतो", "#94A3B8"), ("हरियो", "#10B981"),
    ("सेतो", "#94A3B8"), ("सुनौलो", "#D97706"), ("हरियो", "#10B981"),
    ("सेतो", "#94A3B8"), ("रातो", "#E53E3E"), ("पहेँलो", "#F59E0B"),
    ("नीलो", "#3B82F6"), ("नीलो", "#3B82F6"), ("पहेँलो", "#F59E0B")
]
FALLBACK_NUMBERS = ["९", "६", "५", "२", "१", "५", "६", "९", "३", "८", "८", "३"]

def norm(s):
    return re.sub(r"[^\w\u0900-\u097F]+", "", str(s)).lower()

ALIAS = {}
for i, l in enumerate(NAMES):
    for n in l + [str(i + 1)]:
        ALIAS[norm(n)] = i

def sign_index(x):
    if x is None:
        return None
    x = norm(x)
    if x in ALIAS:
        return ALIAS[x]
    for k, v in ALIAS.items():
        if len(k) > 2 and (k in x or x in k) and len(x) > 2:
            return v
    return None

def getp(o, path):
    if path in (None, ""):
        return o
    for part in re.findall(r"[^.\[\]]+|\[\d+\]", path):
        if part.startswith("["):
            try:
                o = o[int(part[1:-1])]
            except (IndexError, TypeError):
                return None
        elif isinstance(o, dict):
            if part in o:
                o = o[part]
            else:
                return None
        else:
            return None
    return o

def envsub(s):
    return re.sub(r"\$\{(\w+)\}", lambda m: os.environ.get(m.group(1), ""), s) if isinstance(s, str) else s

def load(url, headers=None):
    if headers is None:
        headers = {}
    clean_path = url.replace("file://", "")
    if url.startswith("file://") or os.path.exists(clean_path):
        with open(clean_path, encoding="utf-8") as f:
            return json.load(f)
    req = urllib.request.Request(url, headers={"User-Agent": "nepdate-video/1.0", **headers})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))

def clean_text(t):
    if not t:
        return ""
    # Strip HTML tags
    t = re.sub(r"<[^>]+>", " ", str(t))
    # Normalize whitespaces
    t = re.sub(r"\s+", " ", t).strip()
    return t

def split_sentences(t):
    t = clean_text(t)
    return [s.strip() for s in re.split(r"(?<=।)", t) if s.strip()]

def to_int(v):
    s = str(v).translate(str.maketrans("०१२३४५६७८९", "0123456789"))
    if "★" in s:
        return s.count("★")
    m = re.search(r"\d+(\.\d+)?", s)
    return max(0, min(5, round(float(m.group())))) if m else None

KEYS_NAME = ("name", "sign", "rashi", "rashi_name", "rashiName", "key", "id", "slug", "title")
LABEL = {
    "love": ("सम्बन्ध", "r"),
    "relationship": ("सम्बन्ध", "r"),
    "career": ("कार्यक्षेत्र", "w"),
    "work": ("कार्यक्षेत्र", "w"),
    "business": ("कार्यक्षेत्र", "w"),
    "wealth": ("आर्थिक", "m"),
    "money": ("आर्थिक", "m"),
    "finance": ("आर्थिक", "m"),
    "health": ("स्वास्थ्य", "h"),
    "family": ("परिवार", "f"),
    "travel": ("यात्रा", "t"),
    "luck": ("भाग्य", "g")
}

def find_items(data):
    """JSON भित्र १२ राशिको सूची/डिक्सनरी आफैँ खोज्छ।"""
    def score(x):
        if isinstance(x, list):
            return sum(1 for it in x if isinstance(it, dict) and any(sign_index(it.get(k)) is not None for k in KEYS_NAME if k in it))
        if isinstance(x, dict):
            return sum(1 for k in x if sign_index(k) is not None)
        return 0

    best = (score(data), data)
    stack = [data]
    while stack:
        o = stack.pop()
        vals = o.values() if isinstance(o, dict) else (o if isinstance(o, list) else [])
        for v in vals:
            if isinstance(v, (dict, list)):
                sc = score(v)
                if sc > best[0]:
                    best = (sc, v)
                stack.append(v)
    return best[1]

def pick_text(item):
    """विशिष्ट field नभए सबैभन्दा लामो नेपाली अनुच्छेद पाठ खोज्छ।"""
    if isinstance(item, dict):
        for k in ("prediction", "summary", "text", "description"):
            if k in item and isinstance(item[k], str) and len(item[k]) > 10:
                return item[k]
    cands = []
    def walk(o, depth=0):
        if depth > 3:
            return
        if isinstance(o, dict):
            for k, v in o.items():
                # Avoid picking HTML/nakshatraBishesh markup
                if k in ("nakshatraBishesh", "technicalReason"):
                    continue
                if isinstance(v, str) and len(v) > 25 and k not in KEYS_NAME:
                    cands.append((len(v), v))
                elif isinstance(v, list) and v and all(isinstance(z, str) for z in v) and sum(map(len, v)) > 25:
                    cands.append((sum(map(len, v)), v))
                elif isinstance(v, (dict, list)):
                    walk(v, depth + 1)
        elif isinstance(o, list):
            for z in o:
                walk(z, depth + 1)
    walk(item)
    return max(cands, key=lambda x: x[0])[1] if cands else None

def from_scores(item):
    cats = item.get("categories") if isinstance(item, dict) else None
    out = []
    if isinstance(cats, dict):
        for k, v in cats.items():
            pct = v.get("percentage") if isinstance(v, dict) else v
            lab = LABEL.get(str(k).lower())
            if lab is None or not isinstance(pct, (int, float)):
                continue
            lvl = "अत्यन्त राम्रो" if pct >= 80 else "राम्रो" if pct >= 60 else "मध्यम" if pct >= 40 else "सावधानी आवश्यक"
            n = str(round(pct)).translate(DEV_MAP)
            out.append({"text": (f"आजको भाग्य {lvl} रहनेछ ({n}%)।" if str(k).lower() == "luck" else f"{lab[0]} क्षेत्रमा आज स्थिति {lvl} रहनेछ ({n}%)।"), "cat": lab[1]})
    return out

def raw(api, fmt):
    url = envsub(api["url"]).format(**fmt)
    headers = {k: envsub(v) for k, v in api.get("headers", {}).items()}
    return load(url, headers)

def extract_meta_date(data):
    """NepDate JSON बाट विक्रम संवत् मिति र बार निकाल्छ।"""
    if not isinstance(data, dict):
        return None
    bs = data.get("bikramSambat")
    dow = data.get("dayOfWeek")
    if isinstance(bs, dict) and "year" in bs and "month" in bs and "day" in bs:
        return {
            "year": bs["year"],
            "month": bs["month"],
            "day": bs["day"],
            "monthName": bs.get("monthName"),
            "dayOfWeek": dow
        }
    return None

def fetch(api, fmt):
    data = raw(api, fmt)
    meta_date = extract_meta_date(data)
    items = getp(data, api["signs_path"]) if api.get("signs_path") else find_items(data)
    mk = api.get("match")
    if isinstance(items, dict):
        pairs = list(items.items())
    elif isinstance(items, list):
        pairs = []
        for it in items:
            if isinstance(it, dict):
                k = it.get(mk) if mk else next((it[key] for key in KEYS_NAME if key in it), None)
                pairs.append((k, it))
            else:
                pairs.append((None, it))
    else:
        pairs = []

    F = api.get("fields", {})
    out = {}
    for key, item in pairs:
        i = sign_index(key) if key is not None else None
        if i is None:
            continue

        g = lambda f: (getp(item, F[f]) if f in F and isinstance(item, dict) else None)

        # 1. Prediction Text / Sentences
        raw_t = g("text") if "text" in F else (item.get("prediction") if isinstance(item, dict) and "prediction" in item else pick_text(item))
        r = {}
        if raw_t is not None:
            if isinstance(raw_t, list):
                r["sentences"] = [{"text": clean_text(str(x)), "cat": "auto"} for x in raw_t if clean_text(str(x))]
            else:
                r["sentences"] = [{"text": t, "cat": "auto"} for t in split_sentences(raw_t)]
        elif isinstance(item, dict):
            sc = from_scores(item)
            if sc:
                r["sentences"] = sc
                r["_fallback"] = "scores"

        # 2. Syllables / Letters
        letters = g("letters") if "letters" in F else (item.get("syllables") or item.get("letters") if isinstance(item, dict) else None)
        if letters:
            r["letters"] = str(letters).strip()

        # 3. Rating / Stars
        stars_val = g("stars") if "stars" in F else (item.get("rating") or item.get("stars") if isinstance(item, dict) else None)
        if stars_val is not None and to_int(stars_val) is not None:
            r["stars"] = to_int(stars_val)

        # 4. Shubha Color & Hex
        c_name = g("colorName") if "colorName" in F else (item.get("shubhaColor") or item.get("luckyColor") or item.get("colorName") if isinstance(item, dict) else None)
        if not c_name:
            c_name = FALLBACK_COLORS[i][0]
        r["colorName"] = str(c_name).strip()

        c_hex = g("colorHex") if "colorHex" in F else (item.get("colorHex") if isinstance(item, dict) else None)
        if not c_hex:
            c_hex = COLOR_HEX_MAP.get(r["colorName"], FALLBACK_COLORS[i][1])
        r["colorHex"] = str(c_hex).strip()

        # 5. Shubha Number
        num_val = g("number") if "number" in F else (item.get("shubhaNumber") or item.get("luckyNumber") or item.get("number") if isinstance(item, dict) else None)
        if num_val is None:
            num_val = FALLBACK_NUMBERS[i]
        # Format as Devanagari digit string
        r["number"] = str(num_val).translate(DEV_MAP)

        out[i] = r

    return out, meta_date
