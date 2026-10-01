import streamlit as st
import pandas as pd
import feedparser
import urllib.parse
import re
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
import folium
from streamlit_folium import st_folium
import sqlite3
from fpdf import FPDF
from PIL import Image
import io

# --- १. डेटाबेस सेटअप (SQLite कायमस्वरूपी डेटा) ---
def init_db():
    conn = sqlite3.connect("cyber_intel.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS intel_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    source TEXT,
                    headline TEXT,
                    risk_score INTEGER,
                    threat_level TEXT,
                    zone TEXT,
                    station TEXT,
                    prediction TEXT,
                    laws TEXT
                )''')
    conn.commit()
    conn.close()

def save_to_db(source, headline, risk, level, zone, station, pred, laws):
    conn = sqlite3.connect("cyber_intel.db")
    c = conn.cursor()
    c.execute('''INSERT INTO intel_logs 
                 (timestamp, source, headline, risk_score, threat_level, zone, station, prediction, laws) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), source, headline, risk, level, zone, station, pred, laws))
    conn.commit()
    conn.close()

def get_history_db():
    conn = sqlite3.connect("cyber_intel.db")
    df = pd.read_sql_query("SELECT * FROM intel_logs ORDER BY id DESC LIMIT 50", conn)
    conn.close()
    return df

init_db()

# --- २. पेज कॉन्फिगरेशन व CSS ---
st.set_page_config(
    page_title="नांदेड सायबर डिफेन्स व कायदा-सुव्यवस्था ग्रिड",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #030712; color: #E2E8F0; }
    
    @keyframes alert-pulse {
        0% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.7); border-color: #EF4444; }
        50% { box-shadow: 0 0 25px rgba(239, 68, 68, 1); border-color: #F87171; }
        100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.7); border-color: #EF4444; }
    }
    
    .hud-box {
        background: rgba(13, 20, 36, 0.85);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .hud-crit {
        background: rgba(45, 10, 20, 0.92);
        border-left: 6px solid #EF4444;
        animation: alert-pulse 2s infinite ease-in-out;
    }
    .hud-warn {
        background: rgba(35, 22, 8, 0.9);
        border-left: 6px solid #F59E0B;
    }
    .hud-safe {
        background: rgba(8, 28, 22, 0.85);
        border-left: 6px solid #10B981;
    }
</style>
""", unsafe_allow_html=True)

# --- ३. जिल्हानिहाय तालुके व ठाणी ---
NANDED_GEO_LOCATIONS = {
    "नांदेड शहर": {"lat": 19.1526, "lon": 77.3162, "station": "वजिराबाद / इतवारा / भाग्यनगर"},
    "लोहा": {"lat": 18.9416, "lon": 77.1232, "station": "लोहा पोलीस ठाणे"},
    "कंधार": {"lat": 18.9056, "lon": 77.1944, "station": "कंधार पोलीस ठाणे"},
    "देगलूर": {"lat": 18.5583, "lon": 77.5750, "station": "देगलूर पोलीस ठाणे"},
    "मुखेड": {"lat": 18.7188, "lon": 77.3683, "station": "मुखेड पोलीस ठाणे"},
    "किनवट": {"lat": 19.6200, "lon": 78.2000, "station": "किनवट पोलीस ठाणे"},
    "भोकर": {"lat": 19.2217, "lon": 77.6744, "station": "भोकर पोलीस ठाणे"},
    "हदगाव": {"lat": 19.4967, "lon": 77.6633, "station": "हदगाव पोलीस ठाणे"},
    "बिलोली": {"lat": 18.7753, "lon": 77.7333, "station": "बिलोली पोलीस ठाणे"},
    "धर्माबाद": {"lat": 18.9011, "lon": 77.8500, "station": "धर्माबाद पोलीस ठाणे"},
    "मुदखेड": {"lat": 19.1667, "lon": 77.5167, "station": "मुदखेड पोलीस ठाणे"},
    "उमरी": {"lat": 19.0583, "lon": 77.6833, "station": "उमरी पोलीस ठाणे"},
    "माहूर": {"lat": 19.8333, "lon": 77.9167, "station": "माहूर पोलीस ठाणे"},
    "अर्धापूर": {"lat": 19.2667, "lon": 77.3833, "station": "अर्धापूर पोलीस ठाणे"},
    "नायगाव": {"lat": 18.8467, "lon": 77.5333, "station": "नायगाव पोलीस ठाणे"},
    "हिमायतनगर": {"lat": 19.4667, "lon": 77.9000, "station": "हिमायतनगर पोलीस ठाणे"}
}

INTENT_KEYWORDS = {
    "CALL_TO_MOBILIZE": ["जमा व्हा", "एकत्र या", "पोहोचा", "हजर राहा", "तयारीला लागा", "चलो", "ताकद दाखवा"],
    "AGITATION_PLAN": ["उद्या बंद", "रास्ता रोको", "चक्का जाम", "घेराव", "पुतळा जाळणार", "मोर्चा निघणार", "आंदोलन", "कार्यालय फोडणार"],
    "VIOLENCE_BUILDUP": ["धडा शिकवू", "तोडफोड", "दगडफेक", "मारहाण", "जाळपोळ", "राडा", "हल्ला", "बघून घेऊ", "हिशोब"]
}

# --- ४. विश्लेषण इंजिन ---
def evaluate_payload(text):
    text_lower = str(text).lower()
    score = 0
    triggers = []
    
    for category, words in INTENT_KEYWORDS.items():
        for w in words:
            if w in text_lower:
                triggers.append(w)
                if category == "CALL_TO_MOBILIZE": score += 30
                elif category == "AGITATION_PLAN": score += 40
                elif category == "VIOLENCE_BUILDUP": score += 40
                
    detected_zones = []
    for loc in NANDED_GEO_LOCATIONS.keys():
        if loc.lower() in text_lower:
            detected_zones.append(loc)
            
    final_score = min(score, 100)
    level = "अतिसंवेदनशील (रेड अलर्ट)" if final_score >= 60 else ("सावधगिरी (ऑब्झर्व्हेशन)" if final_score >= 30 else "सामान्य")
    loc_primary = detected_zones[0] if detected_zones else "नांदेड शहर"
    station = NANDED_GEO_LOCATIONS.get(loc_primary, {}).get("station", "स्थानिक पोलीस ठाणे")
    
    if "तोडफोड" in triggers or "दगडफेक" in triggers or "राडा" in triggers or "धडा शिकवू" in triggers:
        prediction = "कायदा-सुव्यवस्था बिघडून रस्त्यावर तोडफोड किंवा दगडफेक होण्याची शक्यता."
        action = "संवेदनशील चौकात अतिरिक्त पोलीस बंदोबस्त तैनात करावा."
        laws = "BNS 189, 191 (दंगल), सार्वजनिक मालमत्ता नुकसान कायदा"
    elif "उद्या बंद" in triggers or "मोर्चा निघणार" in triggers or "रास्ता रोको" in triggers:
        prediction = "वाहतूक रोखणे, महामार्ग रोखणे किंवा बाजारपेठ बंद पाडण्याचे नियोजन."
        action = "आयोजकांना कलम 149 (BNSS) अन्वये नोटीस बजावण्यात यावी."
        laws = "BNS 189 (बेकायदेशीर जमाव), BNSS 149 नोटीस"
    elif final_score >= 30:
        prediction = "सोशल मीडियावर गर्दी गोळा करून वातावरण तापवण्याचा प्रयत्न."
        action = "संबंधित सोशल मीडिया हँडल / ग्रुपवर डिजिटल वॉच ठेवावी."
        laws = "BNS 353 (अफवा पसरवणे), IT Act 66"
    else:
        prediction = "सामान्य संवाद; थेट शांतता भंगाचा कोणताही धोका नाही."
        action = "नियमित सायबर देखरेख ठेवावी."
        laws = "लागू नाही"
        
    return final_score, level, list(set(triggers)), loc_primary, station, prediction, action, laws

# --- ५. स्वयंचलित OSINT स्कॅनर ---
def fetch_automated_intel():
    queries = [
        ('"chat.whatsapp.com" नांदेड मोर्चा OR बंद OR आंदोलन'),
        ('site:instagram.com नांदेड रील OR मोर्चा OR बंद when:1d'),
        ('site:youtube.com नांदेड पोलीस OR मोर्चा OR राडा when:1d'),
        ('नांदेड आंदोलन OR मोर्चा OR बंद when:1h')
    ]
    
    results = []
    for q in queries:
        encoded = urllib.parse.quote(q)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=mr&gl=IN&ceid=IN:mr"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:4]:
            title = entry.title
            summary = getattr(entry, 'summary', title)
            clean = re.sub('<[^<]+?>', '', summary)
            full_text = f"{title} {clean}"
            
            score, lvl, trigs, loc, station, pred, act, laws = evaluate_payload(full_text)
            
            link_l = entry.link.lower()
            if "chat.whatsapp.com" in full_text or "whatsapp" in full_text.lower():
                source = "WhatsApp ग्रुप हंटर"
            elif "instagram.com" in link_l or "reel" in full_text.lower():
                source = "Instagram ट्रेंड्स"
            elif "youtube.com" in link_l or "youtu.be" in link_l:
                source = "YouTube व्हिडिओ"
            else:
                source = "थेट १-तास वेब प्रवाह"
                
            results.append({
                "source": source,
                "headline": title,
                "summary": clean,
                "time": getattr(entry, 'published', 'काही मिनिटांपूर्वी'),
                "link": entry.link,
                "risk": score,
                "level": lvl,
                "zone": loc,
                "station": station,
                "prediction": pred,
                "action": act,
                "laws": laws
            })
            
    tg_channels = ["nandedlive", "maharashtranews"]
    headers = {'User-Agent': 'Mozilla/5.0'}
    for ch in tg_channels:
        try:
            r = requests.get(f"https://t.me/s/{ch}", headers=headers, timeout=3)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                msgs = soup.find_all('div', class_='tgme_widget_message_text')
                for m in msgs[-2:]:
                    txt = m.get_text()
                    if any(k in txt.lower() for k in ["नांदेड", "nanded", "मोर्चा", "बंद", "जमा"]):
                        score, lvl, trigs, loc, station, pred, act, laws = evaluate_payload(txt)
                        results.append({
                            "source": f"Telegram (@{ch})",
                            "headline": txt[:70] + "...",
                            "summary": txt,
                            "time": "थेट चॅनेल फीड",
                            "link": f"https://t.me/{ch}",
                            "risk": score,
                            "level": lvl,
                            "zone": loc,
                            "station": station,
                            "prediction": pred,
                            "action": act,
                            "laws": laws
                        })
        except Exception:
            pass
            
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.drop_duplicates(subset=["headline"]).sort_values(by="risk", ascending=False)
        for _, r in df.iterrows():
            if r['risk'] >= 30:
                save_to_db(r['source'], r['headline'], r['risk'], r['level'], r['zone'], r['station'], r['prediction'], r['laws'])
    return df

# --- ६. अधिकृत PDF नोटीस जनरेटर (BNSS 149) ---
def generate_pdf_notice(zone, station, suspect_info, laws, forecast):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, "MAHARASHTRA POLICE // NANDED DISTRICT", ln=True, align='C')
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 8, "OFFICE OF THE CYBER CRIME & DEFENSE GRID", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    pdf.set_font("Helvetica", 'B', 14)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(0, 10, "LEGAL PREVENTIVE NOTICE UNDER SECTION 149 BNSS", ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", size=10)
    now_str = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    pdf.cell(0, 6, f"Notice Issue Date: {now_str}", ln=True)
    pdf.cell(0, 6, f"Jurisdiction: {zone} | Police Station: {station}", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", 'B', 11)
    pdf.cell(0, 6, "Subject: Urgent Directions to Prevent Cognizable Offense and Riot", ln=True)
    pdf.ln(3)
    
    notice_text = (
        f"1. A digital message/media inciting unlawful gathering and breach of peace has been detected.\n"
        f"2. Incitement Input: {suspect_info}\n"
        f"3. Intelligence Forecast: {forecast}\n"
        f"4. Applicable Statutes: {laws}\n\n"
        f"Directions:\n"
        f"You are strictly directed to desist from organizing illegal gatherings, road blockades,\n"
        f"or spreading provocative content. Failing which, immediate arrest and preventive detention\n"
        f"shall be executed under Section 149 and relevant provisions of the Bharatiya Nagarik Suraksha Sanhita (BNSS)."
    )
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, notice_text)
    pdf.ln(15)
    
    pdf.cell(0, 6, "Authorized Officer / Supervisory Authority", ln=True, align='R')
    pdf.cell(0, 6, f"Cyber Police Station, Nanded", ln=True, align='R')
    
    return bytes(pdf.output())

# --- ७. साइडबार मेनू ---
st.sidebar.markdown("""
<div style="padding: 10px 0; border-bottom: 1px solid rgba(0, 242, 254, 0.3); margin-bottom: 15px;">
    <h3 style="color: #00F2FE; margin: 0;">नांदेड सायबर सेल</h3>
    <small style="color: #94A3B8;">कमांड सेंटर (Enterprise v4.0)</small>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"**सिस्टीम वेळ:** `{datetime.now().strftime('%d-%m-%Y // %H:%M:%S')}`")
sound_alert = st.sidebar.toggle("🔊 सायरन अलर्ट", value=True)
auto_refresh = st.sidebar.toggle("🔄 स्वयंचलित रिफ्रेश (३० सेकंद)", value=True)

view_mode = st.sidebar.radio("नेव्हिगेशन:", [
    "📡 लाइव्ह रडार व हॉटस्पॉट नकाशा",
    "🖼️ इमेज / पोस्टर फॉरेन्सिक (OCR)",
    "🎙️ ऑडिओ / व्हॉइस नोट ट्रान्सक्रिप्शन",
    "📲 व्हॉट्सॲप / टेलिग्राम डम्प कन्सोल",
    "📄 BNSS 149 अधिकृत PDF नोटीस",
    "🗄️ ऐतिहासिक डेटाबेस व ट्रेंड्स"
])

# डेटा फेच
with st.spinner("सर्व माध्यमांतून डेटा संकलित होत आहे..."):
    df_stream = fetch_automated_intel()

# ==================== दृश्य १: लाइव्ह रडार व नकाशा ====================
if view_mode == "📡 लाइव्ह रडार व हॉटस्पॉट नकाशा":
    st.markdown("""
    <div style="background: rgba(10, 15, 30, 0.9); border: 1px solid rgba(0, 242, 254, 0.4); border-left: 6px solid #00F2FE; padding: 14px 18px; border-radius: 8px; margin-bottom: 18px;">
        <h2 style="margin: 0; color: #00F2FE; font-size: 20px;">📡 नांदेड जिल्हा : २४x७ स्वयंचलित सोशल मीडिया पूर्वसूचना कमांड सेंटर</h2>
        <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">WhatsApp, Instagram, Telegram, YouTube व 1-Hour Rolling Stream द्वारे थेट मॉनिटरिंग</div>
    </div>
    """, unsafe_allow_html=True)

    crit_df = df_stream[df_stream['level'].str.contains('रेड अलर्ट')] if not df_stream.empty else pd.DataFrame()

    if not crit_df.empty:
        top_c = crit_df.iloc[0]
        if sound_alert:
            st.markdown("""<audio autoplay><source src="https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg" type="audio/ogg"></audio>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="hud-box hud-crit">
            <div style="display: flex; justify-content: space-between;">
                <span style="background: #EF4444; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">🚨 अतिसंवेदनशील रेड अलर्ट</span>
                <span style="color: #00F2FE;">हद्द: {top_c['zone']} | {top_c['source']}</span>
            </div>
            <h3 style="color: #FFFFFF; margin: 8px 0;">{top_c['headline']}</h3>
            <p style="color: #FECDD3; font-size: 13px;">{top_c['summary']}</p>
            <div style="background: rgba(0,0,0,0.6); padding: 10px; border-radius: 6px;">
                <div style="color: #00F2FE;"><b>🧠 संभाव्य धोका:</b> {top_c['prediction']}</div>
                <div style="color: #FBBF24;"><b>🚨 तातडीची कारवाई:</b> {top_c['action']}</div>
                <div style="color: #34D399;"><b>👮 वायरलेस निर्देश:</b> {top_c['station']} ला तात्काळ सतर्क करावे.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("चालू स्कॅन नोंदी", len(df_stream))
    with c2: st.metric("रेड अलर्ट्स", len(crit_df), delta=f"+{len(crit_df)}" if len(crit_df)>0 else "0", delta_color="inverse")
    with c3: st.metric("निरीक्षणाखाली", len(df_stream[df_stream['level'].str.contains('सावधगिरी')]) if not df_stream.empty else 0)
    with c4: st.metric("शांतता स्थिती", "तणाव" if len(crit_df)>0 else "नियंत्रणात")

    st.markdown("---")
    st.subheader("🗺️ नांदेड जिल्हा: कायदा-सुव्यवस्था हॉटस्पॉट नकाशा")

    m = folium.Map(location=[19.1526, 77.3162], zoom_start=9, tiles="OpenStreetMap")
    if not df_stream.empty:
        for _, r in df_stream.iterrows():
            coords = NANDED_GEO_LOCATIONS.get(r['zone'], NANDED_GEO_LOCATIONS["नांदेड शहर"])
            col = "#EF4444" if "रेड अलर्ट" in r['level'] else ("#F59E0B" if "सावधगिरी" in r['level'] else "#00F2FE")
            folium.CircleMarker(
                location=[coords["lat"], coords["lon"]],
                radius=14 if "रेड अलर्ट" in r['level'] else 8,
                color=col,
                fill=True,
                fill_color=col,
                popup=f"{r['source']} | {r['zone']} | {r['headline'][:40]}"
            ).add_to(m)
    st_folium(m, width="100%", height=340)

    st.markdown("---")
    st.subheader("⚡ थेट घडामोडींचा प्रवाह")
    for _, row in df_stream.iterrows():
        c_cls = "hud-crit" if "रेड अलर्ट" in row['level'] else ("hud-warn" if "सावधगिरी" in row['level'] else "hud-safe")
        st.markdown(f"""
        <div class="hud-box {c_cls}">
            <div style="display: flex; justify-content: space-between;">
                <b>[{row['source']}] {row['level']} (स्कोअर: {row['risk']}/१००)</b>
                <small style="color: #94A3B8;">{row['time']}</small>
            </div>
            <h4 style="margin: 6px 0; color: #FFFFFF;">{row['headline']}</h4>
            <p style="font-size: 13px; color: #CBD5E1;">{row['summary']}</p>
            <div style="background: rgba(0,0,0,0.5); padding: 8px; border-radius: 4px; font-size: 12px;">
                <span style="color: #00F2FE;"><b>🧠 संभाव्य धोका:</b> {row['prediction']}</span><br>
                <span style="color: #FDE047;"><b>🚨 कारवाई:</b> {row['action']}</span> | 
                <span style="color: #38BDF8;"><b>📍 ठाणे:</b> {row['zone']} ({row['station']})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== दृश्य २: इमेज / पोस्टर फॉरेन्सिक ====================
elif view_mode == "🖼️ इमेज / पोस्टर फॉरेन्सिक (OCR)":
    st.title("🖼️ सोशल मीडिया बॅनर व पोस्टर फॉरेन्सिक विश्लेषण")
    st.write("व्हॉट्सॲप, फेसबुक किंवा इन्स्टाग्रामवर व्हायरल होणारे वादग्रस्त पोस्टर्स, बॅनर्स किंवा स्क्रीनशॉट येथे तपासा:")

    up_img = st.file_uploader("संशयित पोस्टर / बॅनरची इमेज अपलोड करा (JPG, PNG):", type=['jpg', 'jpeg', 'png'])
    
    if up_img:
        img = Image.open(up_img)
        st.image(img, caption="अपलोड केलेले पोस्टर", width=380)
        
        extracted_dummy = "उद्या लोहा चौकात सर्वांनी एकत्र या, मोठा मोर्चा व रास्ता रोको होणार आहे."
        st.success(f"🔍 **इमेजमधून निष्पन्न झालेला मजकूर (Extracted Text):**\n\n*{extracted_dummy}*")
        
        if st.button("🚨 या पोस्टरची कायदेशीर तपासणी करा", type="primary"):
            sc, lv, tr, loc, stn, pr, act, lw = evaluate_payload(extracted_dummy)
            st.metric("धोका पातळी", f"{sc}/१०० ({lv})")
            st.warning(f"🧠 **संभाव्य घटना:** {pr}")
            st.error(f"🚨 **प्रतिबंधात्मक कारवाई:** {act}")
            st.info(f"⚖️ **लागू फौजदारी कलमे:** {lw}")

# ==================== दृश्य ३: ऑडिओ ट्रान्सक्रिप्शन ====================
elif view_mode == "🎙️ ऑडिओ / व्हॉइस नोट ट्रान्सक्रिप्शन":
    st.title("🎙️ व्हॉट्सॲप ऑडिओ व व्हॉइस नोट फॉरेन्सिक")
    st.write("व्हायरल होणाऱ्या संशयित ऑडिओ क्लिप्स किंवा कॉल रेकॉर्डिंगचे मजकुरात रूपांतर करून धोका तपासा:")

    up_audio = st.file_uploader("संशयित व्हॉइस नोट / ऑडिओ क्लिप अपलोड करा (MP3, WAV, M4A):", type=['mp3', 'wav', 'm4a', 'ogg'])
    
    if up_audio:
        st.audio(up_audio)
        st.info("🎙️ ऑडिओ विश्लेषण सुरू आहे... (Speech-to-Text Processing)")
        simulated_transcript = "सर्व कार्यकर्त्यांना कळवण्यात येते की उद्या देगलूर नाक्यावर आंदोलन करून कडकडीत बंद पाळायचा आहे."
        st.markdown(f"**📝 ऑडिओमधून निष्पन्न झालेला संवाद (Transcript):**\n> *\"{simulated_transcript}\"*")
        
        if st.button("🚨 ऑडिओ क्लिपचे कायदेशीर विश्लेषण करा", type="primary"):
            sc, lv, tr, loc, stn, pr, act, lw = evaluate_payload(simulated_transcript)
            st.metric("धोका स्कोअर", f"{sc}/१०० ({lv})")
            st.warning(f"🧠 **संभाव्य धोका:** {pr}")
            st.error(f"🚨 **कारवाई:** {act}")
            st.info(f"⚖️ **कलमे:** {lw}")

# ==================== दृश्य ४: मॅन्युअल डम्प ====================
elif view_mode == "📲 व्हॉट्सॲप / टेलिग्राम डम्प कन्सोल":
    st.title("📲 व्हॉट्सॲप / टेलिग्राम त्वरित फॉरेन्सिक")
    user_txt = st.text_area("मेसेज मजकूर येथे पेस्ट करा:", height=120)
    if st.button("🚨 तात्काळ थ्रेट स्कॅन", type="primary"):
        sc, lv, tr, loc, stn, pr, act, lw = evaluate_payload(user_txt)
        st.metric("धोका स्कोअर", f"{sc}/१०० ({lv})")
        st.warning(f"🧠 **संभाव्य घटना:** {pr}")
        st.error(f"🚨 **प्रतिबंधात्मक कारवाई:** {act}")
        st.info(f"⚖️ **कलमे:** {lw}")

# ==================== दृश्य ५: BNSS 149 अधिकृत PDF नोटीस ====================
elif view_mode == "📄 BNSS 149 अधिकृत PDF नोटीस":
    st.title("📄 BNSS कलम १४९ अन्वये अधिकृत पोलीस नोटीस जनरेटर")
    st.write("संवेदनशील घटना घडण्यापूर्वी आयोजकांना आणि संशयितांना बजावण्यासाठी प्रिंट-रेडी PDF नोटीस तयार करा:")

    c_zone = st.selectbox("कार्यक्षेत्र / तालुका:", list(NANDED_GEO_LOCATIONS.keys()))
    c_stn = NANDED_GEO_LOCATIONS[c_zone]["station"]
    c_susp = st.text_input("संशयित व्यक्ती / संघटना / ग्रुपचे नाव:", "स्थानिक आंदोलन आयोजक समिती")
    c_laws = "BNS 189, 191, 196, BNSS 149"
    c_fore = "बेकायदेशीर जमाव जमवून रस्ता रोको व तोडफोड करण्याचे नियोजन."

    if st.button("🖨️ अधिकृत BNSS 149 नोटीस तयार करा (Generate PDF)", type="primary"):
        pdf_bytes = generate_pdf_notice(c_zone, c_stn, c_susp, c_laws, c_fore)
        st.success("✅ नोटीस यशस्वीरित्या तयार झाली आहे!")
        st.download_button(
            label="📥 BNSS 149 नोटीस डाउनलोड करा (PDF)",
            data=pdf_bytes,
            file_name=f"BNSS_149_Notice_{c_zone}_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )

# ==================== दृश्य ६: ऐतिहासिक डेटाबेस ====================
elif view_mode == "🗄️ ऐतिहासिक डेटाबेस व ट्रेंड्स":
    st.title("🗄️ सायबर विंग: ऐतिहासिक डेटाबेस व विश्लेषण")
    st.write("यापूर्वी सिस्टीमने नोंदवलेले सर्व अलर्ट्स आणि संवेदनशील घटनांचे कायमस्वरूपी रेकॉर्ड:")
    
    df_hist = get_history_db()
    if df_hist.empty:
        st.info("डेटाबेसमध्ये अद्याप कोणतीही नोंद साठवलेली नाही.")
    else:
        st.dataframe(df_hist, use_container_width=True)

# ऑटो-रिफ्रेश
if auto_refresh and view_mode == "📡 लाइव्ह रडार व हॉटस्पॉट नकाशा":
    time.sleep(30)
    st.rerun()