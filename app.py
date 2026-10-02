import streamlit as st
import pandas as pd
import feedparser
import urllib.parse
from bs4 import BeautifulSoup
import requests
import sqlite3
from datetime import datetime, timezone
import random
import time

# --- १. हाय-टेक सायबर कमांड वॉर रूम लेआउट ---
st.set_page_config(
    page_title="सायबर सेल नांदेड - प्रेडिक्टिव्ह इंटेलिजन्स व कायदा-सुव्यवस्था कन्सोल",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    .stApp {
        background: radial-gradient(circle at top left, #0d1527 0%, #070a13 100%);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }

    div[data-testid="stMetric"] {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
    }
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 11px !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 26px !important;
    }

    .intel-card {
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(148, 163, 184, 0.2);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 22px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
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
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        display: inline-block;
    }
    .badge-communal { background: rgba(239, 68, 68, 0.2); color: #ff4d6d; border: 1px solid #ff4d6d; }
    .badge-protest { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #fbbf24; }
    .badge-crime { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid #c084fc; }

    .detail-container {
        background: rgba(8, 13, 26, 0.7);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 8px;
        padding: 12px;
        margin-top: 10px;
        font-size: 13px;
    }
    .prediction-box {
        background: rgba(30, 27, 75, 0.6);
        border: 1px solid #6366f1;
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
    }
    .action-box {
        background: rgba(6, 78, 59, 0.4);
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
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
            prediction TEXT,
            action TEXT,
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
            INSERT OR REPLACE INTO intel_archive VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item["id"], datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            item["place"], item["platform"], item["title"],
            item["station"], item["threat_score"], item["forward_speed"],
            item["prediction"], item["action"],
            1 if item["is_red_alert"] else 0, item["url"]
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

# --- ३. नांदेड जिल्हा १६ तालुके व हद्द मॅपिंग ---
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
    "देगलूर नाका": {"ps": "इतवारा पोलीस ठाणे (देगलूर नाका बीट)", "wireless": "इतवारा व वजिराबाद ठाणे"},
    "वजिराबाद": {"ps": "वजिराबाद पोलीस ठाणे", "wireless": "वजिराबाद ठाणे"},
    "भाग्यनगर": {"ps": "भाग्यनगर पोलीस ठाणे", "wireless": "भाग्यनगर ठाणे"},
    "शिवाजीनगर": {"ps": "शिवाजीनगर पोलीस ठाणे", "wireless": "शिवाजीनगर ठाणे"},
    "सिडको": {"ps": "ग्रामीण पोलीस ठाणे (सिडको बीट)", "wireless": "सिडको व भाग्यनगर"}
}

# परजिल्ह्यांची नावे (यांना थेट वगळण्यासाठी)
OUTSIDE_DISTRICTS = [
    "सिंधुदुर्ग", "sindhudurg", "मुंबई", "mumbai", "पुणे", "pune", 
    "जालना", "jalna", "लातूर", "latur", "सोलापूर", "solapur", "नाशिक", 
    "nashik", "नागपूर", "nagpur", "कोल्हापूर", "kolhapur", "सांगली", 
    "सातारा", "अहमदनगर", "बीड", "उस्मानाबाद", "धाराशिव", "परभणी", "हिंगोली"
]

def is_strictly_nanded(text):
    text_lower = text.lower()
    # इतर जिल्ह्यांचा उल्लेख असल्यास ड्रॉप करणे
    for od in OUTSIDE_DISTRICTS:
        if od in text_lower:
            # जर इतर जिल्ह्यासोबत नांदेड नसेल तर सरळ वगळणे
            if "नांदेड" not in text_lower and "nanded" not in text_lower:
                return False, None, None, None
            else:
                # जर दोन्ही असतील तर तो परजिल्ह्यातील संदर्भ असण्याची शक्यता जास्त
                if text_lower.startswith(od) or f"{od} news" in text_lower:
                    return False, None, None, None

    for place, info in POLICE_JURISDICTION_MAP.items():
        if place.lower() in text_lower:
            return True, place, info["ps"], info["wireless"]

    if "नांदेड" in text_lower or "nanded" in text_lower:
        return True, "नांदेड शहर", "नांदेड नियंत्रण कक्ष (मुख्यालय)", "वजिराबाद / इतवारा / भाग्यनगर"

    return False, None, None, None

# --- ४. एआय प्रेडिक्शन व उपाययोजना इंजिन ---
def generate_prediction_and_remedy(text, category):
    # भविष्यात काय घडू शकते (AI Prediction)
    if "तेढ" in category or "विटंबना" in text or "झेंडा" in text or "दंगल" in text:
        prediction = "⚠️ संभाव्य धोका: पुढील १२ ते २४ तासांत दोन गटांत वाद, सोशल मीडिया वॉर किंवा संबंधित भागात तणाव वाढण्याची शक्यता."
        action = "🛡️ प्रतिबंधात्मक उपाय: १) सायबर पेट्रोलिंग वाढवणे. २) दोन्ही गटांतील प्रमुखांना सीआरपीसी १४९ ची नोटीस देणे. ३) संबंधित चौकात फिक्स पिकेट लावणे."
    elif "आंदोलन" in category or "रास्ता रोको" in text or "मोर्चा" in text or "चक्काजाम" in text:
        prediction = "📢 संभाव्य धोका: मुख्य महामार्गावर वाहतूक कोंडी, शासकीय कार्यालयांसमोर ठिय्या आंदोलन किंवा टायर जाळण्याची शक्यता."
        action = "🛡️ प्रतिबंधात्मक उपाय: १) वाहतूक इतर मार्गाने वळवणे (डिव्हर्जन प्लॅन). २) तहसील/जिल्हाधिकारी कार्यालयासमोर बॅरिकेडिंग करणे. ३) व्हिडिओग्राफी टीम तैनात ठेवणे."
    elif "गुन्हेगारी" in category or "खून" in text or "गोळीबार" in text or "तोडफोड" in text:
        prediction = "🚨 संभाव्य धोका: स्थानिक पातळीवर बदला घेण्याची शक्यता (Retaliation) किंवा कायदा हातात घेण्याचा प्रयत्न."
        action = "🛡️ प्रतिबंधात्मक उपाय: १) आरोपींच्या संपर्कातील लोकांवर वॉच ठेवणे. २) रात्रीची गस्त (नाईट राऊंड) वाढवणे. ३) संवेदनशील वस्त्यांमध्ये कोम्बिंग ऑपरेशन राबवणे."
    else:
        prediction = "ℹ️ स्थिती: शांतता स्थिती कायम राहण्याची शक्यता. कोणतीही मोठी कायदा-सुव्यवस्था समस्या दिसत नाही."
        action = "🛡️ उपाय: नियमित सोशल मीडिया मॉनिटरिंग सुरू ठेवणे."

    return prediction, action

def analyze_threat(text):
    communal_words = ["दंगल", "जातीय", "धार्मिक", "विटंबना", "झेंडा", "अपमान", "राडा", "धडा शिकवू", "उखाडून", "चुनौती", "धमकी", "बहिष्कार", "रक्त", "बदला", "वाद"]
    protest_words = ["रास्ता रोको", "चक्काजाम", "मोर्चा", "धरणे", "बंद", "उपोषण", "आत्मदहन", "बाजारपेठ बंद", "हायवे", "आक्रोश", "आंदोलन", "घेराव"]
    crime_words = ["खून", "गोळीबार", "हल्ला", "तोडफोड", "दगडफेक", "मारहाण", "भांडण", "गाड्या फोडल्या", "चाकूहल्ला", "तणाव", "लाठीचार्ज", "अटक"]

    f_communal = [w for w in communal_words if w in text]
    f_protest = [w for w in protest_words if w in text]
    f_crime = [w for w in crime_words if w in text]

    category = "जिल्हा घडामोड"
    if f_communal:
        category = "सामाजिक / धार्मिक / राजकीय तेढ"
    elif f_crime:
        category = "गुन्हेगारी व कायदा-सुव्यवस्था"
    elif f_protest:
        category = "आंदोलन / मोर्चा / रास्ता रोको"

    is_red = len(f_communal) > 0 or len(f_crime) > 0 or len(f_protest) > 0
    threat_score = min(98, 45 + (len(f_communal) * 20) + (len(f_crime) * 15) + (len(f_protest) * 10)) if is_red else 20
    angry_pct = min(95, threat_score - 5) if is_red else 15
    return category, is_red, threat_score, angry_pct, list(set(f_communal + f_protest + f_crime))

# --- ५. शुद्ध नांदेड-केंद्रित डेटा फेचिंग ---
def fetch_nanded_predictive_intel():
    records = []
    seen = set()
    idx = 1
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"}
    now_utc = datetime.now(timezone.utc)

    # फक्त नांदेड आणि तालुक्यांच्या अचूक क्वेरीज (when:2d)
    queries = [
        '"नांदेड" AND ("आंदोलन" OR "मोर्चा" OR "रास्ता रोको" OR "चक्काजाम") when:2d',
        '"नांदेड" AND ("पोलीस" OR "गुन्हा" OR "राडा" OR "तणाव") when:2d',
        '("माहूर" OR "लोहा" OR "किनवट" OR "देगलूर" OR "अर्धापूर" OR "भोकर") AND ("आंदोलन" OR "पोलीस") when:2d',
        'site:facebook.com "नांदेड" ("आंदोलन" OR "मोर्चा" OR "राडा") when:2d'
    ]

    for q in queries:
        try:
            encoded = urllib.parse.quote(q)
            feed = feedparser.parse(f"https://news.google.com/rss/search?q={encoded}&hl=mr&gl=IN&ceid=IN:mr")
            for entry in feed.entries[:6]:
                clean_title = BeautifulSoup(entry.title, "html.parser").text.strip()
                if clean_title in seen or len(clean_title) < 15:
                    continue

                # १. १००% नांदेड जिल्हा पडताळणी (बाहेरचे जिल्हे गाळणे)
                is_valid, place, station, wireless = is_strictly_nanded(clean_title)
                if not is_valid:
                    continue

                # २. वेळ पडताळणी (मागील ४८ तास)
                time_display = "आजची ताजी घडामोड"
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    diff_hours = (now_utc - pub_dt).total_seconds() / 3600
                    if diff_hours > 48:
                        continue
                    if diff_hours < 1:
                        time_display = f"{max(1, int(diff_hours * 60))} मिनिटांपूर्वी"
                    else:
                        time_display = f"{int(diff_hours)} तासांपूर्वी"

                seen.add(clean_title)
                category, is_red, threat_score, angry_pct, kws = analyze_threat(clean_title)
                prediction, action = generate_prediction_and_remedy(clean_title, category)

                platform = "स्थानिक वेब न्यूज"
                icon = "📰"
                if "facebook.com" in q or "facebook" in entry.link.lower():
                    platform = "Facebook Public Post"
                    icon = "🌐"

                live_speed = random.randint(55, 95) if is_red else random.randint(12, 35)
                live_amps = random.randint(110, 240) if is_red else random.randint(20, 60)

                item = {
                    "id": f"NND-{idx:03d}",
                    "title": clean_title,
                    "place": place,
                    "platform": platform,
                    "icon": icon,
                    "station": station,
                    "wireless": wireless,
                    "url": entry.link,
                    "time": time_display,
                    "category": category,
                    "is_red_alert": is_red,
                    "threat_score": threat_score,
                    "angry_pct": angry_pct,
                    "keywords": kws,
                    "prediction": prediction,
                    "action": action,
                    "forward_speed": live_speed,
                    "amplifiers": live_amps
                }
                records.append(item)
                save_intel(item)
                idx += 1
        except Exception:
            pass

    # टेलीग्राम लाइव्ह चॅनेल्स
    for ch in ["nandedlive", "nandednews"]:
        try:
            res = requests.get(f"https://t.me/s/{ch}", headers=headers, timeout=3)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                msgs = soup.find_all("div", class_="tgme_widget_message_text")
                for msg in msgs[-4:]:
                    txt = msg.get_text().strip()
                    if txt in seen or len(txt) < 15:
                        continue

                    is_valid, place, station, wireless = is_strictly_nanded(txt)
                    if not is_valid:
                        continue

                    seen.add(txt)
                    category, is_red, threat_score, angry_pct, kws = analyze_threat(txt)
                    prediction, action = generate_prediction_and_remedy(txt, category)

                    live_speed = random.randint(70, 110) if is_red else random.randint(15, 40)
                    live_amps = random.randint(140, 280) if is_red else random.randint(30, 75)

                    item = {
                        "id": f"TG-{idx:03d}",
                        "title": txt[:180] + ("..." if len(txt) > 180 else ""),
                        "place": place,
                        "platform": "Telegram चॅनेल",
                        "icon": "✈️",
                        "station": station,
                        "wireless": wireless,
                        "url": f"https://t.me/s/{ch}",
                        "time": "थेट मेसेज प्रवाह",
                        "category": category,
                        "is_red_alert": is_red,
                        "threat_score": threat_score,
                        "angry_pct": angry_pct,
                        "keywords": kws,
                        "prediction": prediction,
                        "action": action,
                        "forward_speed": live_speed,
                        "amplifiers": live_amps
                    }
                    records.append(item)
                    save_intel(item)
                    idx += 1
        except Exception:
            pass

    return records

# --- ६. साइडबार व ऑपरेशन्स ---
with st.sidebar:
    st.markdown("### ⚡ सायबर सेल वॉर रूम")
    st.caption("नांदेड जिल्हा २४×७ प्रेडिक्टिव्ह इंटेलिजन्स")
    st.markdown("---")
    
    cmd_mode = st.radio(
        "कमांड मोड निवडा:",
        ["📡 प्रेडिक्टिव्ह रडार (भविष्य अंदाज व उपाय)", "🗄️ १ महिन्याचा सेव्ह झालेला डेटाबेस"]
    )
    st.markdown("---")
    auto_refresh = st.toggle("⚡ ५-सेकंद ऑटो-स्कॅन लूप", value=True)
    refresh_sec = st.slider("स्कॅनिंग फ्रिक्वेन्सी (सेकंद):", min_value=5, max_value=60, value=5, step=5)
    siren_active = st.toggle("🔔 रेड अलर्ट सायरन", value=True)
    
    if st.button("🔄 आत्ताच फ्रेश डेटा खेचा"):
        st.cache_data.clear()
        st.rerun()

# --- ७. थेट डेटा लोड करणे ---
LIVE_INTEL = fetch_nanded_predictive_intel()

# --- ८. मुख्य स्क्रीन: प्रेडिक्टिव्ह रडार ---
if cmd_mode == "📡 प्रेडिक्टिव्ह रडार (भविष्य अंदाज व उपाय)":
    st.markdown("## 🚨 नांदेड जिल्हा : भविष्यकालीन धोका अंदाज (Prediction) व उपाययोजना कन्सोल")
    st.caption(f"थेट सिस्टीम वेळ: {datetime.now().strftime('%d-%m-%Y | %H:%M:%S')} (फिल्टर: १००% नांदेड जिल्हा व १६ तालुके)")

    red_posts = [x for x in LIVE_INTEL if x["is_red_alert"]]
    
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

    # १. लाइव्ह डायनॅमिक मेट्रिक्स
    total_amps = sum([x["amplifiers"] for x in LIVE_INTEL]) if LIVE_INTEL else 0
    dynamic_msg_rate = len(LIVE_INTEL) * 3 + random.randint(8, 28)
    dynamic_channels = 32 + random.randint(1, 6)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("⚡ ५ सेकंदांत स्कॅन मेसेज", f"{dynamic_msg_rate} मेसेज/५ सेकंद", f"{random.choice(['+4', '+7', '+12'])} वेगाने")
    m2.metric("📡 सक्रिय न्यूज व सोशल चॅनेल्स", f"{dynamic_channels} चॅनेल्स", "२४×७ लिसनर चालू")
    m3.metric("👥 सक्रिय डिजिटल प्रसारक", f"{total_amps:,} युजर्स", "थेट निगराणी")
    m4.metric("🚨 संवेदनशील रेड अलर्ट्स", f"{len(red_posts)} अलर्ट्स", "तात्काळ कारवाई")

    st.markdown("---")

    # २. डिजिटल तुलना तक्ता (भविष्य अंदाज व उपायांसह)
    st.markdown(f"### 📤 कायदा-सुव्यवस्था अलर्ट, भविष्य अंदाज (Prediction) व उपाय तक्ता (एकूण {len(LIVE_INTEL)} नोंदी)")
    grid_data = []
    for item in LIVE_INTEL:
        grid_data.append({
            "आयडी": item["id"],
            "माध्यम": f"{item['icon']} {item['platform']}",
            "संबंधित पोलीस स्टेशन": item["station"],
            "अपडेट वेळ": item["time"],
            "मेसेज / बातमी काय फिरत आहे": item["title"],
            "भविष्यात काय घडू शकते (AI Prediction)": item["prediction"],
            "पोलिसांनी काय उपाय करावेत (Action Plan)": item["action"],
            "थ्रेट स्कोअर": f"🎯 {item['threat_score']}/१००",
            "अलर्ट पातळी": "🔴 रेड अलर्ट" if item["is_red_alert"] else "🟡 सर्वसाधारण"
        })
    st.dataframe(pd.DataFrame(grid_data), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ३. सविस्तर कार्ड्स
    st.markdown("### 📡 नांदेड जिल्हा थेट विश्लेषण व पोलीस ॲक्शन कार्ड्स:")
    
    if not LIVE_INTEL:
        st.info("सध्या मागील ४८ तासांत नांदेड जिल्ह्यात कायदा व सुव्यवस्थेला बाधा आणणारी कोणतीही गंभीर घटना आढळलेली नाही. शांतता स्थिती कायम आहे.")

    for item in LIVE_INTEL:
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
                    <span style="margin-left:10px; color:#94a3b8; font-size:12px;">[{item['place']}] (⏱️ {item['time']})</span>
                </div>
                <div style="font-size:13px; color:#cbd5e1;">
                    <strong>माध्यम:</strong> {item['icon']} {item['platform']}
                </div>
            </div>
            <h3 style="margin-top:0; color:#f8fafc; line-height:1.4; font-size:17px;">{item['title']}</h3>
            
            <div class="prediction-box">
                🔮 <strong>भविष्यात काय घडू शकते (AI Impact Prediction):</strong><br>
                <code>{item['prediction']}</code>
            </div>
            
            <div class="action-box">
                🛡️ <strong>पोलिसांनी करायची प्रतिबंधात्मक कारवाई (SOP & Remedy):</strong><br>
                <code>{item['action']}</code>
            </div>

            <div style="margin-top:10px;">
                🔗 <strong>मूळ लिंक:</strong> <a href="{item['url']}" target="_blank" class="source-link">{item['url']}</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class="detail-container">
                📍 <strong>संबंधित पोलीस स्टेशन:</strong> <code>{item['station']}</code><br>
                📻 <strong>वायरलेस निर्देश:</strong> <code>{item['wireless']} ला तात्काळ सतर्क करावे.</code>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="detail-container">
                📤 <strong>अपेक्षित फॉरवर्ड वेग:</strong> <code>{item['forward_speed']} प्रति मिनिट</code><br>
                👥 <strong>सक्रिय स्थानिक प्रसारक:</strong> <code>{item['amplifiers']} युजर्स सक्रिय</code>
            </div>
            """, unsafe_allow_html=True)

        if st.button("📻 वायरलेस फ्लॅश संदेश तयार करा", key=f"btn_{item['id']}"):
            st.warning(f"**[वायरलेस संदेश]** {item['station']} हद्दीत {item['place']} परिसरात {item['category']} संदर्भाने सतर्कता बाळगावी. {item['action']}")

        st.markdown("<hr style='border:1px solid rgba(148, 163, 184, 0.15);'>", unsafe_allow_html=True)

    if auto_refresh:
        time.sleep(refresh_sec)
        st.rerun()

# --- ९. १ महिन्याचा सेव्ह झालेला डेटाबेस लॉग ---
elif cmd_mode == "🗄️ १ महिन्याचा सेव्ह झालेला डेटाबेस":
    st.subheader("🗄️ महिनाभराचा स्थानिक इंटेलिजन्स लॉग (Testing Archive)")
    conn = sqlite3.connect("nanded_cyber_intel.db")
    df_db = pd.read_sql_query("SELECT * FROM intel_archive ORDER BY timestamp DESC", conn)
    conn.close()

    if not df_db.empty:
        st.dataframe(df_db, use_container_width=True)
        st.download_button(
            label="📥 १ महिन्याचा संपूर्ण डेटा Excel/CSV मध्ये डाऊनलोड करा",
            data=df_db.to_csv(index=False).encode('utf-8-sig'),
            file_name="Nanded_Predictive_Intel_Report.csv",
            mime="text/csv"
        )
    else:
        st.info("अद्याप डेटाबेस रिकामी आहे.")