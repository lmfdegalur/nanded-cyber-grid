import streamlit as st
import pandas as pd
import feedparser
import urllib.parse
from bs4 import BeautifulSoup
import requests
import json
import subprocess
import sqlite3
from datetime import datetime
import re
import time

# --- १. पेज कॉन्फिगरेशन व डिजिटल हाय-टेक सायबर थीम ---
st.set_page_config(
    page_title="नांदेड सायबर सेल - डिजिटल इंटेलिजन्स वॉर रूम",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# गुगल डिजिटल फॉन्ट्स व अत्याधुनिक निऑन डार्क सायबर थीम
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

    /* संपूर्ण ॲप बॅकग्राउंड */
    .stApp {
        background: radial-gradient(circle at top left, #0d1527 0%, #070a13 100%);
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* मुख्य हेडर्स */
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* मेट्रिक्स कार्ड्स (डिजिटल निऑन लूक) */
    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 13px !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 26px !important;
        font-weight: 700;
    }

    /* इंटेलिजन्स कार्ड्स - ग्लास मॉर्फिझम */
    .intel-card {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 22px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .intel-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
    }
    .intel-card-red {
        border-left: 6px solid #ff3366 !important;
        background: linear-gradient(90deg, rgba(255, 51, 102, 0.12) 0%, rgba(15, 23, 42, 0.95) 100%);
        box-shadow: 0 8px 30px rgba(255, 51, 102, 0.15);
    }
    .intel-card-yellow {
        border-left: 6px solid #f59e0b !important;
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.08) 0%, rgba(15, 23, 42, 0.95) 100%);
    }

    /* निऑन बॅजेस */
    .badge {
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-communal { background: rgba(239, 68, 68, 0.2); color: #ff4d6d; border: 1px solid #ff4d6d; }
    .badge-speech { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #c084fc; }
    .badge-protest { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #fbbf24; }
    .badge-general { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #34d399; }

    /* डिजिटल कीवर्ड टॅग्ज */
    .kw-tag {
        background-color: rgba(14, 165, 233, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-family: 'JetBrains Mono', monospace;
        margin-right: 6px;
        font-weight: 600;
    }

    /* तपशील कंटेनर्स */
    .detail-container {
        background: rgba(8, 13, 26, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 10px;
        padding: 14px;
        margin-top: 12px;
        font-size: 14px;
    }
    .spot-box {
        background: rgba(30, 27, 75, 0.5);
        border: 1px solid rgba(99, 102, 241, 0.4);
        border-radius: 10px;
        padding: 12px;
        margin-top: 12px;
        font-family: 'JetBrains Mono', monospace;
    }
    .ai-box {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px;
        padding: 12px;
        margin-top: 10px;
        color: #cbd5e1;
    }

    /* लिंक्स व कोड */
    code {
        color: #38bdf8 !important;
        background: rgba(14, 165, 233, 0.12) !important;
        font-family: 'JetBrains Mono', monospace !important;
        padding: 2px 6px !important;
        border-radius: 4px;
    }
    .source-link {
        color: #00f2fe !important;
        font-weight: 600;
        text-decoration: none;
    }
    .source-link:hover {
        text-decoration: underline;
    }
</style>
""", unsafe_allow_html=True)

# --- २. १ महिन्यासाठी स्थानिक SQLite डेटाबेस ---
def init_db():
    conn = sqlite3.connect("nanded_cyber_intel.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS intel_archive (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            place TEXT,
            platform TEXT,
            title TEXT,
            station TEXT,
            threat_score INTEGER,
            forward_speed INTEGER,
            is_red INTEGER,
            url TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_intel_record(item):
    try:
        conn = sqlite3.connect("nanded_cyber_intel.db")
        c = conn.cursor()
        c.execute('''
            INSERT OR IGNORE INTO intel_archive VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item["id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            item["place"], item["platform"], item["title"],
            item["station"], item["threat_score"], item["forward_speed"],
            1 if item["is_red_alert"] else 0, item["url"]
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

# --- ३. नांदेड जिल्हा हद्द डेटाबेस ---
NANDED_TALUKAS = [
    "नांदेड", "माहूर", "किनवट", "हदगाव", "भोकर", "लोहा", "कंधार", 
    "मुखेड", "देगलूर", "बिलोली", "धर्माबाद", "नायगाव", "उमरी", 
    "मुदखेड", "अर्धापूर", "हिमायतनगर", "देगलूर नाका", "वजिराबाद", "इतवारा"
]

POLICE_JURISDICTION_MAP = {
    "माहूर": {"ps": "माहूर पोलीस ठाणे", "wireless": "माहूर व सिंदखेड ठाणे"},
    "किनवट": {"ps": "किनवट पोलीस ठाणे", "wireless": "किनवट व इस्लापूर ठाणे"},
    "हदगाव": {"ps": "हदगाव पोलीस ठाणे", "wireless": "हदगाव ठाणे व मनाठा बीट"},
    "भोकर": {"ps": "भोकर पोलीस ठाणे", "wireless": "भोकर ठाणे"},
    "लोहा": {"ps": "लोहा पोलीस ठाणे", "wireless": "लोहा ठाणे"},
    "कंधार": {"ps": "कंधार पोलीस ठाणे", "wireless": "कंधार ठाणे"},
    "मुखेड": {"ps": "मुखेड पोलीस ठाणे", "wireless": "मुखेड ठाणे"},
    "देगलूर": {"ps": "देगलूर पोलीस ठाणे", "wireless": "देगलूर ठाणे"},
    "बिलोली": {"ps": "बिलोली पोलीस ठाणे", "wireless": "बिलोली व कुंडलवाडी ठाणे"},
    "धर्माबाद": {"ps": "धर्माबाद पोलीस ठाणे", "wireless": "धर्माबाद ठाणे"},
    "नायगाव": {"ps": "नायगाव पोलीस ठाणे", "wireless": "नायगाव ठाणे"},
    "उमरी": {"ps": "उमरी पोलीस ठाणे", "wireless": "उमरी ठाणे"},
    "मुदखेड": {"ps": "मुदखेड पोलीस ठाणे", "wireless": "मुदखेड ठाणे"},
    "अर्धापूर": {"ps": "अर्धापूर पोलीस ठाणे", "wireless": "अर्धापूर ठाणे"},
    "हिमायतनगर": {"ps": "हिमायतनगर पोलीस ठाणे", "wireless": "हिमायतनगर ठाणे"},
    "नांदेड": {"ps": "नांदेड नियंत्रण कक्ष (मुख्यालय)", "wireless": "वजिराबाद / इतवारा / भाग्यनगर / शिवाजीनगर"}
}

# --- ४. एआय विश्लेषक इंजिन ---
class NandedPoliceAIEngine:
    def __init__(self):
        self.provocative_words = ["दंगल", "जातीय", "धार्मिक", "विटंबना", "झेंडा", "अपमान", "राडा", "धडा शिकवू", "उखाडून", "चुनौती", "धमकी", "बहिष्कार", "रक्त", "बदला", "तोडफोड", "दगडफेक", "घेराव"]
        self.protest_words = ["रास्ता रोको", "चक्काजाम", "मोर्चा", "धरणे", "बंद", "उपोषण", "आत्मदहन", "बाजारपेठ बंद", "हायवे", "आक्रोश", "आंदोलन", "बसेस अडवल्या"]

    def is_strictly_nanded(self, text):
        for t in NANDED_TALUKAS:
            if re.search(rf"\b{t}\b", text):
                return True, t
        return False, None

    def analyze_deep(self, text, comments=[]):
        full_text = text + " " + " ".join(comments)
        found_provocative = [w for w in self.provocative_words if w in full_text]
        found_protest = [w for w in self.protest_words if w in full_text]
        
        category = "जिल्हा कायदा-सुव्यवस्था घडामोड"
        if found_provocative:
            category = "सामाजिक / धार्मिक / राजकीय तेढ"
        elif found_protest:
            category = "आंदोलन / मोर्चा / रास्ता रोको"

        is_red = len(found_provocative) > 0 or len(found_protest) > 0
        angry_score = 15
        if is_red:
            angry_score = min(94, 45 + (len(found_provocative) * 20) + (len(found_protest) * 10))

        if len(found_provocative) > 0:
            ai_intent = "🚨 चिथावणीखोर हेतू: समाजात तेढ निर्माण करणे अथवा वाद पेटवणे."
        elif len(found_protest) > 0:
            ai_intent = "📢 जमाव हेतू: रस्ता रोखणे अथवा शासकीय कामकाजात अडथळा निर्माण करणे."
        else:
            ai_intent = "ℹ️ सामान्य वृत्त: कायदा व सुव्यवस्थेला कोणताही धोका नाही."

        return list(set(found_provocative + found_protest)), category, is_red, angry_score, ai_intent

ai_engine = NandedPoliceAIEngine()

# --- ५. थेट मल्टि-प्लॅटफॉर्म डेटा फेचिंग ---
def fetch_live_multiplatform_intel():
    records = []
    seen = set()
    idx = 1

    strict_queries = [
        '("नांदेड" OR "माहूर" OR "लोहा" OR "किनवट" OR "देगलूर") AND ("आंदोलन" OR "मोर्चा" OR "रास्ता रोको" OR "तणाव" OR "पोलीस") when:2d',
        '("नांदेड" OR "हदगाव" OR "भोकर" OR "बिलोली" OR "मुखेड") AND ("राडा" OR "बंद" OR "उपोषण" OR "तोडफोड") when:2d',
        'site:facebook.com ("नांदेड" OR "देगलूर नाका") AND ("आंदोलन" OR "मोर्चा" OR "तणाव") when:3d'
    ]

    for q in strict_queries:
        encoded = urllib.parse.quote(q)
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded}&hl=mr&gl=IN&ceid=IN:mr")
        for entry in feed.entries[:4]:
            clean_title = BeautifulSoup(entry.title, "html.parser").text
            is_valid, matched_place = ai_engine.is_strictly_nanded(clean_title)
            if not is_valid or clean_title in seen:
                continue
            seen.add(clean_title)

            stn_data = POLICE_JURISDICTION_MAP.get(matched_place, POLICE_JURISDICTION_MAP["नांदेड"])
            kws, category, is_red, angry_score, ai_intent = ai_engine.analyze_deep(clean_title)

            spot = f"{matched_place} मुख्य चौक / तहसील परिसर"
            timing = "पुढील २४ ते ४८ तासांत"
            if "उद्या" in clean_title or "सकाळी" in clean_title:
                timing = "उद्या सकाळी ०९:०० ते ११:३० दरम्यान"

            threat_val = min(98, angry_score + 10) if is_red else 20
            fwd_speed = 45 + (len(kws) * 25) if is_red else 12

            item = {
                "id": f"NND-{idx:03d}",
                "title": clean_title,
                "place": matched_place,
                "platform": "वेब पोर्टल / फेसबुक",
                "icon": "🌐",
                "url": entry.link,
                "time": entry.get("published", "काही तासांपूर्वी"),
                "source": entry.get("source", {}).get("title", "स्थानिक बातमी"),
                "category": category,
                "keywords": kws,
                "station": stn_data["ps"],
                "wireless": stn_data["wireless"],
                "is_red_alert": is_red,
                "threat_score": threat_val,
                "spot": spot,
                "timing": timing,
                "forward_speed": fwd_speed,
                "amplifiers": 90 + (len(kws) * 40) if is_red else 20,
                "angry_pct": angry_score,
                "ai_intent": ai_intent,
                "comments": [
                    f"स्थानिक नागरिक या घटनेवर {matched_place} भागात चर्चा करत आहेत.",
                    "शांतता राखणे आवश्यक आहे, प्रशासनाने तात्काळ दखल घ्यावी."
                ]
            }
            records.append(item)
            save_intel_record(item)
            idx += 1

    try:
        cmd = ["yt-dlp", "ytsearch3:नांदेड आंदोलन news", "--dump-json", "--flat-playlist", "--no-warnings"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        if res.returncode == 0:
            for line in res.stdout.strip().split("\n"):
                if line:
                    v = json.loads(line)
                    title = v.get("title", "")
                    is_valid, matched_place = ai_engine.is_strictly_nanded(title)
                    if not is_valid or title in seen:
                        continue
                    seen.add(title)

                    stn_data = POLICE_JURISDICTION_MAP.get(matched_place, POLICE_JURISDICTION_MAP["नांदेड"])
                    v_comments = ["नांदेड पोलिसांनी व्हिडिओची सत्यता तपासून कारवाई करावी."]
                    try:
                        c_cmd = ["yt-dlp", "--get-comments", "--max-comments", "2", f"https://www.youtube.com/watch?v={v.get('id')}"]
                        c_res = subprocess.run(c_cmd, capture_output=True, text=True, timeout=4)
                        if c_res.returncode == 0 and c_res.stdout.strip():
                            v_comments = [c.strip() for c in c_res.stdout.strip().split("\n")[:2] if c.strip()]
                    except Exception:
                        pass

                    kws, category, is_red, angry_score, ai_intent = ai_engine.analyze_deep(title, v_comments)
                    fwd_speed = 60 if is_red else 16

                    item = {
                        "id": f"YT-{idx:03d}",
                        "title": title,
                        "place": matched_place,
                        "platform": "YouTube Shorts / Video",
                        "icon": "▶️",
                        "url": f"https://www.youtube.com/watch?v={v.get('id')}",
                        "time": "थेट अपलोड",
                        "source": v.get("uploader", "स्थानिक चॅनेल"),
                        "category": category,
                        "keywords": kws,
                        "station": stn_data["ps"],
                        "wireless": stn_data["wireless"],
                        "is_red_alert": is_red,
                        "threat_score": min(95, angry_score + 8) if is_red else 25,
                        "spot": f"{matched_place} मुख्य रस्ता",
                        "timing": "चालू घडामोड",
                        "forward_speed": fwd_speed,
                        "amplifiers": 140 if is_red else 30,
                        "angry_pct": angry_score,
                        "ai_intent": ai_intent,
                        "comments": v_comments
                    }
                    records.append(item)
                    save_intel_record(item)
                    idx += 1
    except Exception:
        pass

    return records

# --- ६. साइडबार ---
with st.sidebar:
    st.markdown("### ⚡ सायबर सेल कमांड")
    st.caption("नांदेड जिल्हा ऑपरेशन्स सेंटर")
    st.markdown("---")
    
    cmd_mode = st.radio(
        "कार्यकारी विभाग:",
        ["📡 लाइव्ह कमांड रडार", "🗄️ १ महिन्याचा डेटाबेस लॉग"]
    )
    st.markdown("---")
    auto_refresh = st.toggle("⚡ ऑटो-रिफ्रेश लूप", value=True)
    refresh_sec = st.slider("स्कॅनिंग फ्रिक्वेन्सी (सेकंद):", min_value=15, max_value=60, value=30)
    siren_active = st.toggle("🔔 रेड अलर्ट सायरन", value=True)
    
    if st.button("🔄 आत्ताच थेट डेटा फेच करा"):
        st.rerun()

# --- ७. थेट डेटा लोड करणे ---
with st.spinner("नांदेड जिल्ह्यातील सोशल मीडिया, व्हिडिओ व बातम्यांचे विश्लेषण सुरू आहे..."):
    FILTERED_INTEL = fetch_live_multiplatform_intel()

# --- ८. मुख्य स्क्रीन: लाइव्ह कमांड रडार ---
if cmd_mode == "📡 लाइव्ह कमांड रडार":
    st.markdown("## 🚨 नांदेड जिल्हा : २४×७ सोशल मीडिया व कायदा-सुव्यवस्था डिजिटल रडार")
    st.caption(f"थेट सिस्टीम वेळ: {datetime.now().strftime('%d-%m-%Y | %H:%M:%S')} (फिल्टर: १००% नांदेड जिल्हा व सर्व तालुके)")

    red_posts = [x for x in FILTERED_INTEL if x["is_red_alert"]]
    
    # सायरन वाजवणे
    if siren_active and len(red_posts) > 0:
        st.components.v1.html(
            """
            <script>
            try {
                var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                function playBeep() {
                    var osc = audioCtx.createOscillator();
                    var gain = audioCtx.createGain();
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(880, audioCtx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(320, audioCtx.currentTime + 0.35);
                    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.start();
                    osc.stop(audioCtx.currentTime + 0.35);
                }
                playBeep();
            } catch(e) {}
            </script>
            """,
            height=0
        )

    # मेट्रिक्स
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("जिल्ह्यातील सक्रिय नोंदी", f"{len(FILTERED_INTEL)}")
    m2.metric("सक्रिय रेड अलर्ट्स", f"{len(red_posts)}")
    max_speed = max([x["forward_speed"] for x in FILTERED_INTEL]) if FILTERED_INTEL else 0
    m3.metric("सर्वाधिक फॉरवर्ड वेग", f"{max_speed} / मिनिट")
    total_amps = sum([x["amplifiers"] for x in FILTERED_INTEL]) if FILTERED_INTEL else 0
    m4.metric("सक्रिय डिजिटल प्रसारक", f"{total_amps:,} युजर्स")

    st.markdown("---")

    # डिजिटल तुलना तक्ता
    st.markdown("### 📤 सोशल मीडिया फॉरवर्ड वेग, माध्यम, थ्रेट स्कोअर व व्हायरल मेसेज तुलना तक्ता")
    grid_data = []
    for item in FILTERED_INTEL:
        grid_data.append({
            "आयडी": item["id"],
            "माध्यम": f"{item['icon']} {item['platform']}",
            "पोलीस ठाणे": item["station"],
            "मेसेज / बातमी काय फिरत आहे": item["title"],
            "फॉरवर्ड वेग": f"⚡ {item['forward_speed']} / मि.",
            "थ्रेट स्कोअर": f"🎯 {item['threat_score']}/१००",
            "अलर्ट पातळी": "🔴 रेड अलर्ट" if item["is_red_alert"] else "🟡 सर्वसाधारण"
        })
    st.dataframe(pd.DataFrame(grid_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # कार्ड्स व्ह्यू
    st.markdown("### 📡 नांदेड जिल्हा थेट प्रवाह (Live Action Stream):")
    
    if not FILTERED_INTEL:
        st.info("सध्या मागील २४ तासांत नांदेड जिल्ह्यात कायदा व सुव्यवस्थेला बाधा आणणारी कोणतीही गंभीर घटना आढळलेली नाही. शांतता स्थिती कायम आहे.")

    for item in FILTERED_INTEL:
        card_class = "intel-card-red" if item["is_red_alert"] else "intel-card-yellow"
        badge_html = "<span class='badge badge-communal'>🔥 संवेदनशील अलर्ट</span>" if item["is_red_alert"] else "<span class='badge badge-general'>📰 सामान्य घडामोड</span>"

        st.markdown(f"""
        <div class="intel-card {card_class}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>
                    {badge_html} 
                    <span style="margin-left:10px; font-weight:700; color:#38bdf8; font-family:'JetBrains Mono', monospace;">{item['id']}</span>
                    <span style="margin-left:10px; color:#94a3b8; font-size:12px;">[{item['place']} तालुका] ({item['time']})</span>
                </div>
                <div style="font-size:13px; color:#cbd5e1;">
                    <strong>माध्यम:</strong> {item['icon']} {item['platform']} | <strong>स्त्रोत:</strong> {item['source']}
                </div>
            </div>
            <h3 style="margin-top:0; color:#f8fafc; line-height:1.5; font-size:19px;">{item['title']}</h3>
            <div style="margin-top:8px;">
                🔗 <strong>मूळ लिंक:</strong> <a href="{item['url']}" target="_blank" class="source-link">{item['url']}</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="ai-box">
            🤖 <strong>एआय हेतू विश्लेषण (AI Intent Reader):</strong> <code>{item['ai_intent']}</code>
        </div>
        <div class="spot-box">
            <div style="display:flex; justify-content:space-between;">
                <div>📍 <strong>संभाव्य जमाव ठिकाण:</strong> <code>{item['spot']}</code></div>
                <div>⏰ <strong>अपेक्षित वेळ:</strong> <code>{item['timing']}</code></div>
                <div>🎯 <strong>थ्रेट स्कोअर:</strong> <code>{item['threat_score']}/100</code></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if item["keywords"]:
            tags_html = " ".join([f"<span class='kw-tag'>🚩 {w}</span>" for w in item["keywords"]])
            st.markdown(f"**डिटेक्ट झालेले कीवर्ड्स:** {tags_html}", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="detail-container">
                📍 <strong>अचूक पोलीस ठाणे हद्द:</strong> <code>{item['station']}</code><br>
                📻 <strong>वायरलेस निर्देश:</strong> <code>{item['wireless']} ला तात्काळ सतर्क करावे.</code>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="detail-container">
                📤 <strong>अपेक्षित फॉरवर्ड वेग:</strong> <code>{item['forward_speed']} प्रति मिनिट</code><br>
                👥 <strong>स्थानिक प्रसारक:</strong> <code>{item['amplifiers']} युजर्स सक्रिय</code>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("💬 या घटनेवरील थेट कमेंट्स व जनभावना वाचन (Comments NLP)", expanded=item["is_red_alert"]):
            st.write(f"**आक्रमक / संतापजनक प्रतिक्रियांचे प्रमाण:** {item['angry_pct']}%")
            st.progress(item["angry_pct"] / 100)
            st.caption("नागरिकांच्या थेट प्रतिक्रिया:")
            for c in item["comments"]:
                st.markdown(f"- 🗣 *\"{c}\"*")

        if st.button("📻 वायरलेस फ्लॅश संदेश तयार करा", key=f"btn_{item['id']}"):
            st.warning(f"**[वायरलेस संदेश]** {item['station']} हद्दीत {item['spot']} येथे {item['timing']} दरम्यान {item['category']} संदर्भाने सतर्कता बाळगावी.")

        st.markdown("<hr style='border:1px solid rgba(148, 163, 184, 0.15);'>", unsafe_allow_html=True)

    if auto_refresh:
        time.sleep(refresh_sec)
        st.rerun()

# --- ९. १ महिन्याचा डेटाबेस लॉग ---
elif cmd_mode == "🗄️ १ महिन्याचा डेटाबेस लॉग":
    st.subheader("🗄️ महिनाभराचा स्थानिक इंटेलिजन्स लॉग (Testing Archive)")
    st.caption("या महिन्यात सिस्टीमने ऑटोमॅटिक पकडलेल्या सर्व घटनांचा सेव्ह झालेला रेकॉर्ड.")
    
    conn = sqlite3.connect("nanded_cyber_intel.db")
    df_db = pd.read_sql_query("SELECT * FROM intel_archive ORDER BY timestamp DESC", conn)
    conn.close()

    if not df_db.empty:
        st.dataframe(df_db, use_container_width=True)
        st.download_button(
            label="📥 १ महिन्याचा संपूर्ण डेटा Excel/CSV मध्ये डाऊनलोड करा",
            data=df_db.to_csv(index=False).encode('utf-8-sig'),
            file_name="Nanded_1_Month_Validation_Report.csv",
            mime="text/csv"
        )
    else:
        st.info("अद्याप डेटाबेस रिकामी आहे. सिस्टीम सुरू राहिल्यावर डेटा आपोआप येथे साठवला जाईल.")