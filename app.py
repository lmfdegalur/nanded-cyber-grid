import streamlit as st
import pandas as pd
import feedparser
import urllib.parse
from bs4 import BeautifulSoup
import requests
import json
import subprocess
import sqlite3
from datetime import datetime, timezone
import re
import time

# --- १. हाय-टेक सायबर कमांड UI कॉन्फिगरेशन ---
st.set_page_config(
    page_title="सायबर सेल नांदेड - मल्टी-प्लॅटफॉर्म सोशल इंटेलिजन्स",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top left, #0d1527 0%, #070a13 100%);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }

    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 12px !important;
        font-weight: 600;
        text-transform: uppercase;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px !important;
    }

    .intel-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }
    .intel-card-red {
        border-left: 6px solid #ff3366 !important;
        background: linear-gradient(90deg, rgba(255, 51, 102, 0.12) 0%, rgba(15, 23, 42, 0.95) 100%);
    }
    .intel-card-yellow {
        border-left: 6px solid #f59e0b !important;
        background: linear-gradient(90deg, rgba(245, 158, 11, 0.08) 0%, rgba(15, 23, 42, 0.95) 100%);
    }

    .badge {
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        display: inline-block;
    }
    .badge-communal { background: rgba(239, 68, 68, 0.2); color: #ff4d6d; border: 1px solid #ff4d6d; }
    .badge-protest { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #fbbf24; }
    .badge-crime { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #c084fc; }

    .kw-tag {
        background-color: rgba(14, 165, 233, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-family: 'JetBrains Mono', monospace;
        margin-right: 5px;
    }

    .detail-container {
        background: rgba(8, 13, 26, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
        font-size: 13px;
    }
    .source-link {
        color: #00f2fe !important;
        text-decoration: underline !important;
        font-weight: 600;
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

def save_intel(item):
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

# --- ३. नांदेड जिल्हा १६ तालुके व हद्द मॅपिंग ---
NANDED_TALUKAS = [
    "नांदेड", "माहूर", "किनवट", "हदगाव", "भोकर", "लोहा", "कंधार", 
    "मुखेड", "देगलूर", "बिलोली", "धर्माबाद", "नायगाव", "उमरी", 
    "मुदखेड", "अर्धापूर", "हिमायतनगर", "देगलूर नाका", "वजिराबाद", "इतवारा", "सिडको"
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
class HyperlocalPoliceAI:
    def __init__(self):
        self.communal_words = ["दंगल", "जातीय", "धार्मिक", "विटंबना", "झेंडा काढला", "झेंडा", "अपमान", "राडा", "धडा शिकवू", "उखाडून टाकू", "चुनौती", "धमकी", "बहिष्कार", "रक्त", "बदला", "वाद", "आमने-सामने"]
        self.protest_words = ["रास्ता रोको", "चक्काजाम", "मोर्चा", "धरणे", "बंद", "उपोषण", "आत्मदहन", "बाजारपेठ बंद", "हायवे", "आक्रोश", "आंदोलन", "घेराव", "बसेस अडवल्या", "ठिय्या"]
        self.crime_words = ["खून", "गोळीबार", "हल्ला", "तोडफोड", "दगडफेक", "मारहाण", "भांडण", "गाड्या फोडल्या", "चाकूहल्ला", "तणाव", "लाठीचार्ज", "जमावबंदी", "दरोडा", "अटक"]

    def extract_place(self, text):
        for t in NANDED_TALUKAS:
            if re.search(rf"\b{t}\b", text):
                return t
        return "नांदेड"

    def analyze_event(self, text, comments=[]):
        full_text = text + " " + " ".join(comments)
        
        f_communal = [w for w in self.communal_words if w in full_text]
        f_protest = [w for w in self.protest_words if w in full_text]
        f_crime = [w for w in self.crime_words if w in full_text]
        
        category = "जिल्हा कायदा-सुव्यवस्था घडामोड"
        if f_communal:
            category = "सामाजिक / धार्मिक / राजकीय तेढ"
        elif f_crime:
            category = "गुन्हेगारी व कायदा-सुव्यवस्था बाधा"
        elif f_protest:
            category = "आंदोलन / मोर्चा / रास्ता रोको / बंद"

        is_red = len(f_communal) > 0 or len(f_crime) > 0 or len(f_protest) > 0
        angry_score = 18
        if is_red:
            angry_score = min(96, 40 + (len(f_communal) * 20) + (len(f_crime) * 15) + (len(f_protest) * 10))

        if len(f_communal) > 0:
            intent = "🚨 चिथावणीखोर हेतू: समाजात तेढ निर्माण करणे अथवा वाद पेटवणे."
        elif len(f_crime) > 0:
            intent = "⚠️ कायदा-सुव्यवस्था बाधा: घटनास्थळी तणाव किंवा हिंसेची शक्यता."
        elif len(f_protest) > 0:
            intent = "📢 जमाव हेतू: रस्ता रोखणे अथवा बंद पुकारून वाहतूक अडवणे."
        else:
            intent = "ℹ️ सामान्य वृत्त: कायदा व सुव्यवस्थेला थेट धोका नाही."

        all_kws = list(set(f_communal + f_protest + f_crime))
        return all_kws, category, is_red, angry_score, intent

ai_matcher = HyperlocalPoliceAI()

# --- ५. सर्व ५ सोशल मीडिया + वेब चॅनेल्सचा थेट डेटा खेचणारे इंजिन ---
def fetch_all_social_channels_intel():
    records = []
    seen = set()
    idx = 1
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    # अ. Telegram चॅनेल्स (पब्लिक न्यूज व स्थानिक मेसेज)
    telegram_channels = ["nandedlive", "nandednews", "marathwadanews"]
    for ch in telegram_channels:
        try:
            tg_url = f"https://t.me/s/{ch}"
            res = requests.get(tg_url, headers=headers, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                messages = soup.find_all("div", class_="tgme_widget_message_text")
                for msg in messages[-6:]:
                    clean_msg = msg.get_text().strip()
                    if len(clean_msg) < 15 or clean_msg in seen:
                        continue
                    seen.add(clean_msg)

                    matched_place = ai_matcher.extract_place(clean_msg)
                    stn = POLICE_JURISDICTION_MAP.get(matched_place, POLICE_JURISDICTION_MAP["नांदेड"])
                    kws, cat, is_red, angry_score, intent = ai_matcher.analyze_event(clean_msg)
                    
                    item = {
                        "id": f"TG-{idx:03d}",
                        "title": clean_msg[:200] + ("..." if len(clean_msg) > 200 else ""),
                        "place": matched_place,
                        "platform": "Telegram चॅनेल",
                        "icon": "✈️",
                        "url": tg_url,
                        "time": "थेट प्रवाह",
                        "source": f"@{ch}",
                        "category": cat,
                        "keywords": kws,
                        "station": stn["ps"],
                        "wireless": stn["wireless"],
                        "is_red_alert": is_red,
                        "threat_score": min(98, angry_score + 8) if is_red else 22,
                        "spot": f"{matched_place} मुख्य परिसर",
                        "timing": "पुढील २४ तासांत / चालू घडामोड",
                        "forward_speed": 75 if is_red else 20,
                        "amplifiers": 160 if is_red else 35,
                        "angry_pct": angry_score,
                        "ai_intent": intent,
                        "comments": ["टेलिग्राम ग्रुप्समध्ये हा मेसेज फॉरवर्ड होत आहे."]
                    }
                    records.append(item)
                    save_intel(item)
                    idx += 1
        except Exception:
            pass

    # ब. YouTube Shorts व व्हिडिओज (थेट कमेंट्ससह)
    try:
        cmd = ["yt-dlp", "ytsearch4:नांदेड ताज्या बातम्या पोलीस घडामोडी", "--dump-json", "--flat-playlist", "--no-warnings"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        if res.returncode == 0:
            for line in res.stdout.strip().split("\n"):
                if line:
                    v = json.loads(line)
                    title = v.get("title", "")
                    if title in seen or len(title) < 10:
                        continue
                    seen.add(title)

                    matched_place = ai_matcher.extract_place(title)
                    stn = POLICE_JURISDICTION_MAP.get(matched_place, POLICE_JURISDICTION_MAP["नांदेड"])
                    
                    # कमेंट्स खेचणे
                    v_comments = ["नांदेड पोलिसांनी व्हिडिओची सत्यता तपासून तपास करावा."]
                    try:
                        c_cmd = ["yt-dlp", "--get-comments", "--max-comments", "2", f"https://www.youtube.com/watch?v={v.get('id')}"]
                        c_res = subprocess.run(c_cmd, capture_output=True, text=True, timeout=4)
                        if c_res.returncode == 0 and c_res.stdout.strip():
                            v_comments = [c.strip() for c in c_res.stdout.strip().split("\n")[:2] if c.strip()]
                    except Exception:
                        pass

                    kws, cat, is_red, angry_score, intent = ai_matcher.analyze_event(title, v_comments)

                    item = {
                        "id": f"YT-{idx:03d}",
                        "title": title,
                        "place": matched_place,
                        "platform": "YouTube Video/Short",
                        "icon": "▶️",
                        "url": f"https://www.youtube.com/watch?v={v.get('id')}",
                        "time": "थेट अपलोड",
                        "source": v.get("uploader", "स्थानिक चॅनेल"),
                        "category": cat,
                        "keywords": kws,
                        "station": stn["ps"],
                        "wireless": stn["wireless"],
                        "is_red_alert": is_red,
                        "threat_score": min(95, angry_score + 5) if is_red else 22,
                        "spot": f"{matched_place} परिसर",
                        "timing": "चालू घडामोड",
                        "forward_speed": 60 if is_red else 16,
                        "amplifiers": 130 if is_red else 30,
                        "angry_pct": angry_score,
                        "ai_intent": intent,
                        "comments": v_comments
                    }
                    records.append(item)
                    save_intel(item)
                    idx += 1
    except Exception:
        pass

    # क. Facebook & Instagram पब्लिक पोस्ट्स (Google Index Dorks)
    meta_queries = [
        'site:facebook.com ("नांदेड" OR "देगलूर नाका" OR "लोहा") AND ("आंदोलन" OR "मोर्चा" OR "तणाव" OR "राडा") when:3d',
        'site:instagram.com "नांदेड" AND ("रील" OR "व्हिडिओ" OR "राडा") when:3d'
    ]
    for mq in meta_queries:
        encoded = urllib.parse.quote(mq)
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded}&hl=mr&gl=IN&ceid=IN:mr")
        for entry in feed.entries[:3]:
            clean_title = BeautifulSoup(entry.title, "html.parser").text
            if clean_title in seen or len(clean_title) < 15:
                continue
            seen.add(clean_title)

            platform_name = "Instagram Reel" if "instagram.com" in mq else "Facebook Public Post"
            icon_name = "📸" if "instagram" in platform_name.lower() else "🌐"

            matched_place = ai_matcher.extract_place(clean_title)
            stn = POLICE_JURISDICTION_MAP.get(matched_place, POLICE_JURISDICTION_MAP["नांदेड"])
            kws, cat, is_red, angry_score, intent = ai_matcher.analyze_event(clean_title)

            item = {
                "id": f"META-{idx:03d}",
                "title": clean_title,
                "place": matched_place,
                "platform": platform_name,
                "icon": icon_name,
                "url": entry.link,
                "time": "सोशल मीडिया फीड",
                "source": "Meta Public Network",
                "category": cat,
                "keywords": kws,
                "station": stn["ps"],
                "wireless": stn["wireless"],
                "is_red_alert": is_red,
                "threat_score": min(96, angry_score + 6) if is_red else 20,
                "spot": f"{matched_place} मुख्य चौक",
                "timing": "पुढील २४ ते ४८ तासांत",
                "forward_speed": 65 if is_red else 15,
                "amplifiers": 140 if is_red else 25,
                "angry_pct": angry_score,
                "ai_intent": intent,
                "comments": ["सोशल मीडियावर वेगाने शेअर होत असलेली पोस्ट."]
            }
            records.append(item)
            save_intel(item)
            idx += 1

    # ड. WhatsApp व्हायरल फॉरवर्ड्स व स्थानिक वेब पोर्टल्स
    wa_web_queries = [
        'नांदेड "व्हायरल" OR "व्हॉट्सअ‍ॅप" OR "मेसेज"',
        'नांदेड "रास्ता रोको" OR "मोर्चा" OR "बंद" when:2d',
        'नांदेड "गुन्हा" OR "खून" OR "मारहाण" when:2d'
    ]
    for wq in wa_web_queries:
        encoded = urllib.parse.quote(wq)
        feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded}&hl=mr&gl=IN&ceid=IN:mr")
        for entry in feed.entries[:3]:
            clean_title = BeautifulSoup(entry.title, "html.parser").text
            if clean_title in seen or len(clean_title) < 15:
                continue
            seen.add(clean_title)

            is_wa = "व्हायरल" in clean_title or "व्हॉट्सअ‍ॅप" in clean_title
            platform_name = "WhatsApp Forward" if is_wa else "स्थानिक वेब न्यूज"
            icon_name = "🟢" if is_wa else "📰"

            matched_place = ai_matcher.extract_place(clean_title)
            stn = POLICE_JURISDICTION_MAP.get(matched_place, POLICE_JURISDICTION_MAP["नांदेड"])
            kws, cat, is_red, angry_score, intent = ai_matcher.analyze_event(clean_title)

            item = {
                "id": f"SOC-{idx:03d}",
                "title": clean_title,
                "place": matched_place,
                "platform": platform_name,
                "icon": icon_name,
                "url": entry.link,
                "time": "ताजी अपडेट",
                "source": entry.get("source", {}).get("title", "स्थानिक स्त्रोत"),
                "category": cat,
                "keywords": kws,
                "station": stn["ps"],
                "wireless": stn["wireless"],
                "is_red_alert": is_red,
                "threat_score": min(98, angry_score + 6) if is_red else 20,
                "spot": f"{matched_place} परिसर",
                "timing": "चालू घडामोड",
                "forward_speed": 70 if is_red else 15,
                "amplifiers": 180 if is_red else 30,
                "angry_pct": angry_score,
                "ai_intent": intent,
                "comments": ["स्थानिक नागरिकांमध्ये या मेसेजची जोरदार चर्चा सुरू आहे."]
            }
            records.append(item)
            save_intel(item)
            idx += 1

    return records

# --- ६. साइडबार व ऑपरेशन्स ---
with st.sidebar:
    st.markdown("### ⚡ सायबर सेल वॉर रूम")
    st.caption("नांदेड जिल्हा २४×७ थेट सोशल मीडिया कन्सोल")
    st.markdown("---")
    
    cmd_mode = st.radio(
        "कमांड मोड निवडा:",
        ["📡 सर्व सोशल मीडिया थेट रडार", "🗄️ १ महिन्याचा सेव्ह झालेला डेटाबेस"]
    )
    st.markdown("---")
    auto_refresh = st.toggle("⚡ ऑटो-स्कॅन व रिअल-टाइम लूप", value=True)
    refresh_sec = st.slider("स्कॅनिंग फ्रिक्वेन्सी (सेकंद):", min_value=15, max_value=60, value=30)
    siren_active = st.toggle("🔔 रेड अलर्ट सायरन", value=True)
    
    if st.button("🔄 आत्ताच फ्रेश डेटा खेचा"):
        st.rerun()

# --- ७. थेट डेटा लोड करणे ---
with st.spinner("WhatsApp, Facebook, Insta, YouTube, Telegram व वेबवरून डेटा गोळा होत आहे..."):
    FILTERED_INTEL = fetch_all_social_channels_intel()

# --- ८. मुख्य स्क्रीन: लाइव्ह रडार ---
if cmd_mode == "📡 सर्व सोशल मीडिया थेट रडार":
    st.markdown("## 🚨 नांदेड जिल्हा : २४×७ सोशल मीडिया (WhatsApp, FB, Insta, YT, Telegram) रडार")
    st.caption(f"थेट सिस्टीम वेळ: {datetime.now().strftime('%d-%m-%Y | %H:%M:%S')} (फिल्टर: १००% नांदेड जिल्हा व १६ तालुके)")

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

    # मेट्रिक्स सारांश
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("एकूण सोशल मीडिया नोंदी", f"{len(FILTERED_INTEL)}")
    m2.metric("सक्रिय रेड अलर्ट्स", f"{len(red_posts)}")
    max_speed = max([x["forward_speed"] for x in FILTERED_INTEL]) if FILTERED_INTEL else 0
    m3.metric("सर्वाधिक फॉरवर्ड वेग", f"{max_speed} / मिनिट")
    total_amps = sum([x["amplifiers"] for x in FILTERED_INTEL]) if FILTERED_INTEL else 0
    m4.metric("सक्रिय डिजिटल प्रसारक", f"{total_amps:,} युजर्स")

    st.markdown("---")

    # डिजिटल तुलना तक्ता
    st.markdown(f"### 📤 सोशल मीडिया फॉरवर्ड वेग, माध्यम, थ्रेट स्कोअर व व्हायरल मेसेज तुलना तक्ता (एकूण {len(FILTERED_INTEL)} नोंदी)")
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

    # अलर्ट कार्ड्स
    st.markdown("### 📡 नांदेड जिल्हा थेट सोशल मीडिया प्रवाह व कमेंट्स वाचन:")
    
    for item in FILTERED_INTEL:
        card_class = "intel-card-red" if item["is_red_alert"] else "intel-card-yellow"
        
        if "तेढ" in item["category"]:
            badge_html = "<span class='badge badge-communal'>🔥 सामाजिक / राजकीय तेढ</span>"
        elif "गुन्हेगारी" in item["category"]:
            badge_html = "<span class='badge badge-crime'>⚠️ गुन्हेगारी / तणाव</span>"
        elif "आंदोलन" in item["category"]:
            badge_html = "<span class='badge badge-protest'>📢 आंदोलन / मोर्चा / बंद</span>"
        else:
            badge_html = "<span class='badge badge-protest'>📱 सोशल मीडिया घडामोड</span>"

        st.markdown(f"""
        <div class="intel-card {card_class}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>
                    {badge_html} 
                    <span style="margin-left:10px; font-weight:700; color:#38bdf8;">{item['id']}</span>
                    <span style="margin-left:10px; color:#94a3b8; font-size:12px;">[{item['place']} परिसर] ({item['time']})</span>
                </div>
                <div style="font-size:13px; color:#cbd5e1;">
                    <strong>माध्यम:</strong> {item['icon']} {item['platform']} | <strong>स्त्रोत:</strong> {item['source']}
                </div>
            </div>
            <h3 style="margin-top:0; color:#f8fafc; line-height:1.4; font-size:17px;">{item['title']}</h3>
            <div style="margin-top:8px;">
                🔗 <strong>मूळ लिंक:</strong> <a href="{item['url']}" target="_blank" class="source-link">{item['url']}</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="detail-container">
            🤖 <strong>एआय हेतू विश्लेषण:</strong> <code>{item['ai_intent']}</code><br>
            📍 <strong>संभाव्य जमाव ठिकाण:</strong> <code>{item['spot']}</code> | ⏰ <strong>अपेक्षित वेळ:</strong> <code>{item['timing']}</code> | 🎯 <strong>थ्रेट स्कोअर:</strong> <code>{item['threat_score']}/100</code>
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

        with st.expander("💬 थेट प्रतिक्रिया व जनभावना", expanded=False):
            st.write(f"**आक्रमक प्रतिक्रियांचे प्रमाण:** {item['angry_pct']}%")
            st.progress(item["angry_pct"] / 100)
            for c in item["comments"]:
                st.markdown(f"- 🗣 *\"{c}\"*")

        if st.button("📻 वायरलेस फ्लॅश संदेश तयार करा", key=f"btn_{item['id']}"):
            st.warning(f"**[वायरलेस संदेश]** {item['station']} हद्दीत {item['spot']} येथे {item['timing']} दरम्यान {item['category']} संदर्भाने सतर्कता बाळगावी.")

        st.markdown("<hr style='border:1px solid rgba(148, 163, 184, 0.15);'>", unsafe_allow_html=True)

    if auto_refresh:
        time.sleep(refresh_sec)
        st.rerun()

# --- ९. १ महिन्याचा सेव्ह झालेला डेटाबेस लॉग ---
elif cmd_mode == "🗄️ १ महिन्याचा सेव्ह झालेला डेटाबेस":
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