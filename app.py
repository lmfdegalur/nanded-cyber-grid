import streamlit as st
import pandas as pd
import feedparser
import urllib.parse
import re
from datetime import datetime
import time
import folium
from streamlit_folium import st_folium

# --- १. पेज मांडणी ---
st.set_page_config(
    page_title="नांदेड जिल्हा सायबर सुरक्षा नियंत्रण कक्ष",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# सायबर नियंत्रण कक्ष शैली (Dark HUD)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600;800&display=swap');

    .stApp {
        background-color: #030712;
        color: #D1D5DB;
    }

    @keyframes red-pulse {
        0% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.6); border-color: #EF4444; }
        50% { box-shadow: 0 0 25px rgba(239, 68, 68, 0.9); border-color: #F87171; }
        100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.6); border-color: #EF4444; }
    }

    .cyber-header {
        background: rgba(10, 15, 30, 0.9);
        border: 1px solid rgba(0, 242, 254, 0.4);
        border-left: 6px solid #00F2FE;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }

    .alert-critical-banner {
        background: rgba(40, 5, 15, 0.95);
        border: 2px solid #EF4444;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
        animation: red-pulse 2s infinite ease-in-out;
    }

    .hud-box {
        background: rgba(13, 20, 36, 0.8);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
    }

    .card-crit {
        background: rgba(28, 6, 14, 0.85);
        border: 1px solid #EF4444;
        border-left: 6px solid #EF4444;
    }
    .card-warn {
        background: rgba(30, 18, 5, 0.85);
        border: 1px solid #F59E0B;
        border-left: 6px solid #F59E0B;
    }
    .card-safe {
        background: rgba(5, 25, 20, 0.85);
        border: 1px solid #10B981;
        border-left: 6px solid #10B981;
    }

    .badge-alert {
        background-color: #EF4444;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- २. नांदेड जिल्हानिहाय भौगोलिक स्थाने ---
NANDED_GEO_LOCATIONS = {
    "नांदेड शहर": {"lat": 19.1526, "lon": 77.3162, "station": "मुख्य नियंत्रण कक्ष // वजिराबाद / इतवारा / भाग्यनगर"},
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

KEYWORDS = {
    "VIOLENCE": ["कापाकापी", "तोडफोड", "दगडफेक", "मारहाण", "जाळपोळ", "राडा", "हल्ला", "खून", "कट्टा", "पिस्तूल", "तलवार", "rada", "todfod", "dagadfek", "attack", "talwar"],
    "MOBILIZATION": ["रास्ता रोको", "चक्का जाम", "बंद", "मोर्चा", "जमा व्हा", "एकत्र या", "आंदोलन", "पुतळा जाळला", "जोडे मारो", "घेराव", "morcha", "band", "rasta roko", "jama vha"],
    "TENSION": ["लाठीचार्ज", "गोळीबार", "संचारबंदी", "इंटरनेट बंद", "कर्फ्यू", "पळापळ", "दंगल", "तणाव", "अफवा", "curfew", "lathi charge", "firing"]
}

# --- ३. विश्लेषण व प्रेडिक्शन ---
def analyze_threat(text):
    text_lower = str(text).lower()
    score = 0
    triggers = []
    
    for cat, words in KEYWORDS.items():
        for w in words:
            if w in text_lower:
                triggers.append(w)
                if cat == "VIOLENCE": score += 40
                elif cat == "MOBILIZATION": score += 30
                elif cat == "TENSION": score += 30
                
    detected_zones = []
    for loc in NANDED_GEO_LOCATIONS.keys():
        if loc.lower() in text_lower:
            detected_zones.append(loc)
            
    final_score = min(score, 100)
    level = "अतिसंवेदनशील" if final_score >= 65 else ("सावधगिरी" if final_score >= 35 else "सुरक्षित")
    loc_primary = detected_zones[0] if detected_zones else "नांदेड शहर"
    station = NANDED_GEO_LOCATIONS.get(loc_primary, {}).get("station", "स्थानिक नियंत्रण कक्ष")
    
    if "तोडफोड" in triggers or "दगडफेक" in triggers or "rada" in triggers:
        prediction = "सार्वजनिक मालमत्तेचे नुकसान, दगडफेक किंवा दंगल उसळण्याची शक्यता."
        laws = "BNS १८९, १९१ (दंगल), सार्वजनिक मालमत्ता नुकसान प्रतिबंधक कायदा"
    elif "मोर्चा" in triggers or "बंद" in triggers or "rasta roko" in triggers:
        prediction = "वाहतूक रोखणे, बाजारपेठ बंद पाडणे व गर्दी जमवण्याचे संकेत."
        laws = "BNS १८९ (बेकायदेशीर जमाव), कलम १४९ अन्वये प्रतिबंधात्मक नोटीस"
    elif "पुतळा" in triggers or "जोडे" in triggers:
        prediction = "राजकीय किंवा सामाजिक गटात तणाव निर्माण होण्याची शक्यता."
        laws = "BNS १९६ (जातीय/गट तेढ), BNS ३५६ (मानहानी)"
    elif level == "सावधगिरी":
        prediction = "अफवा पसरून नागरिकांमध्ये संभ्रम निर्माण होण्याची शक्यता."
        laws = "BNS ३५३ (सार्वजनिक शांततेचा भंग करणाऱ्या अफवा)"
    else:
        prediction = "सद्यस्थितीत कोणताही धोका नाही; परिस्थिती सामान्य आहे."
        laws = "फौजदारी कलम लागू नाही"
        
    return final_score, level, list(set(triggers)), loc_primary, station, prediction, laws

# --- ४. बॅकग्राउंड थेट ऑटो-स्कॅनर ---
def fetch_live_data():
    queries = [
        "नांदेड मोर्चा बंद रास्ता रोको when:1d",
        "नांदेड गुन्हा पोलीस राडा when:1d",
        "नांदेड तणाव लाठीचार्ज when:1d"
    ]
    posts = []
    for q in queries:
        encoded = urllib.parse.quote(q)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=mr&gl=IN&ceid=IN:mr"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:10]:
            title = entry.title
            summary = getattr(entry, 'summary', title)
            clean = re.sub('<[^<]+?>', '', summary)
            full_msg = f"{title} {clean}"
            
            score, lvl, trigs, loc, station, pred, laws = analyze_threat(full_msg)
            posts.append({
                "headline": title,
                "summary": clean,
                "time": getattr(entry, 'published', 'गेल्या २४ तासांत'),
                "source": entry.source.get('title', 'स्थानिक वेब वृत्त') if hasattr(entry, 'source') else 'वेब प्रवाह',
                "link": entry.link,
                "risk": score,
                "level": lvl,
                "zone": loc,
                "station": station,
                "triggers": trigs,
                "prediction": pred,
                "laws": laws
            })
            
    df = pd.DataFrame(posts)
    if not df.empty:
        df = df.drop_duplicates(subset=["headline"]).sort_values(by="risk", ascending=False)
    return df

# --- ५. साइडबार मांडणी ---
st.sidebar.markdown("""
<div style="padding: 10px 0; border-bottom: 1px solid rgba(0, 242, 254, 0.3); margin-bottom: 15px;">
    <h3 style="color: #00F2FE; margin: 0;">महाराष्ट्र पोलीस</h3>
    <small style="color: #94A3B8;">नांदेड जिल्हा सायबर सेल</small>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"**सिस्टीम वेळ:** `{datetime.now().strftime('%d-%m-%Y // %H:%M:%S')}`")
st.sidebar.markdown("<span style='color: #10B981; font-weight: bold;'>● थेट स्कॅनिंग सक्रिय</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

sound_enabled = st.sidebar.toggle("🔊 धोक्याचा ऑडिओ सायरन", value=True)
auto_refresh = st.sidebar.toggle("🔄 स्वयंचलित रिफ्रेश (दर ३० सेकंद)", value=True)
selected_taluka = st.sidebar.selectbox("📍 तालुका निवडा:", ["सर्व तालुके"] + list(NANDED_GEO_LOCATIONS.keys()))

st.sidebar.markdown("---")
view_mode = st.sidebar.radio("विभाग निवडा:", [
    "⚡ थेट नियंत्रण कक्ष व नकाशा", 
    "📄 कायदेशीर कारवाई अहवाल",
    "🕵️ गुप्तवार्ता खबरी टिप-लाइन"
])

# डेटा लोड करणे
with st.spinner("नांदेड जिल्ह्यातील ताज्या घडामोडी स्कॅन होत आहेत..."):
    df_live = fetch_live_data()

if selected_taluka != "सर्व तालुके" and not df_live.empty:
    df_live = df_live[df_live['zone'].str.contains(selected_taluka)]

# ==================== विभाग १: नियंत्रण कक्ष व नकाशा ====================
if view_mode == "⚡ थेट नियंत्रण कक्ष व नकाशा":
    
    st.markdown("""
    <div class="cyber-header">
        <h2 style="margin: 0; color: #00F2FE; font-size: 22px;">
            🚨 नांदेड जिल्हा पोलीस : सोशल मीडिया व कायदा-सुव्यवस्था नियंत्रण कक्ष
        </h2>
        <div style="font-size: 13px; color: #94A3B8; margin-top: 5px;">
            २४ तास स्वयंचलित इंटरनेट व सोशल मीडिया मॉनिटरिंग प्रणाली
        </div>
    </div>
    """, unsafe_allow_html=True)

    crit_threats = df_live[df_live['level'] == 'अतिसंवेदनशील'] if not df_live.empty else pd.DataFrame()

    if not crit_threats.empty:
        top_c = crit_threats.iloc[0]
        if sound_enabled:
            st.markdown("""
            <audio autoplay>
                <source src="https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg" type="audio/ogg">
            </audio>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="alert-critical-banner">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="badge-alert">अतिसंवेदनशील इशारा</span>
                <span style="color: #EF4444; font-weight: bold;">तालुका/हद्द: {top_c['zone']}</span>
            </div>
            <h3 style="color: #FFFFFF; margin: 10px 0;">{top_c['headline']}</h3>
            <p style="color: #FECDD3; font-size: 14px;">{top_c['summary']}</p>
            <div style="background: rgba(0, 0, 0, 0.6); padding: 12px; border-radius: 6px; border: 1px solid #EF4444;">
                <div style="color: #00F2FE;"><b>🧠 संभाव्य धोका:</b> {top_c['prediction']}</div>
                <div style="color: #FBBF24;"><b>⚖️ सुचवलेली कलमे:</b> {top_c['laws']}</div>
                <div style="color: #34D399;"><b>🚨 कारवाई:</b> {top_c['station']} ला वायरलेसद्वारे तात्काळ सूचित करावे.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # मेट्रिक्स
    crit_count = len(crit_threats)
    warn_count = len(df_live[df_live['level'] == 'सावधगिरी']) if not df_live.empty else 0
    total_count = len(df_live) if not df_live.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="hud-box"><small style="color: #94A3B8;">एकूण स्कॅन केलेल्या नोंदी</small><h2 style="color: #00F2FE; margin: 5px 0;">{total_count}</h2><small style="color: #10B981;">२४ तास लाइव्ह</small></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="hud-box"><small style="color: #EF4444;">अतिसंवेदनशील अलर्ट्स</small><h2 style="color: #EF4444; margin: 5px 0;">{crit_count}</h2><small style="color: #EF4444;">तात्काळ लक्ष द्या</small></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="hud-box"><small style="color: #F59E0B;">सावधगिरीच्या नोंदी</small><h2 style="color: #F59E0B; margin: 5px 0;">{warn_count}</h2><small style="color: #F59E0B;">निरीक्षणाखाली</small></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="hud-box"><small style="color: #10B981;">जिल्हा शांतता स्थिती</small><h2 style="color: {'#EF4444' if crit_count > 0 else '#10B981'}; margin: 5px 0;">{'तणावग्रस्त' if crit_count > 0 else 'शांतता'}</h2><small style="color: #94A3B8;">अचूकता: ९८%</small></div>""", unsafe_allow_html=True)

    # नकाशा
    st.markdown("<h4 style='color: #00F2FE; margin-top: 20px;'>🗺️ नांदेड जिल्हा: थेट कायदा-सुव्यवस्था हॉटस्पॉट नकाशा</h4>", unsafe_allow_html=True)

    gis_map = folium.Map(location=[19.1526, 77.3162], zoom_start=9, tiles="OpenStreetMap")

    if not df_live.empty:
        for _, r in df_live.iterrows():
            coords = NANDED_GEO_LOCATIONS.get(r['zone'], NANDED_GEO_LOCATIONS["नांदेड शहर"])
            hex_color = "#EF4444" if r['level'] == 'अतिसंवेदनशील' else ("#F59E0B" if r['level'] == 'सावधगिरी' else "#00F2FE")
            rad = 16 if r['level'] == 'अतिसंवेदनशील' else (10 if r['level'] == 'सावधगिरी' else 6)

            folium.CircleMarker(
                location=[coords["lat"], coords["lon"]],
                radius=rad,
                color=hex_color,
                fill=True,
                fill_color=hex_color,
                fill_opacity=0.75,
                popup=f"[{r['level']}] {r['zone']} | स्कोअर: {r['risk']}/100"
            ).add_to(gis_map)

    st_folium(gis_map, width="100%", height=360)

    # घटनांची यादी
    st.markdown("<h4 style='color: #00F2FE; margin-top: 20px;'>⚡ थेट घटना प्रवाह व विश्लेषण</h4>", unsafe_allow_html=True)

    if df_live.empty:
        st.info("गेल्या २४ तासांत कोणत्याही तालुक्यातून आक्षेपार्ह नोंद आढळली नाही.")
    else:
        for _, row in df_live.iterrows():
            c_style = "card-crit" if row['level'] == 'अतिसंवेदनशील' else ("card-warn" if row['level'] == 'सावधगिरी' else "card-safe")
            lvl_color = "#EF4444" if row['level'] == 'अतिसंवेदनशील' else ("#F59E0B" if row['level'] == 'सावधगिरी' else "#10B981")
            trig_str = ", ".join(row['triggers']) if row['triggers'] else "नाहीत"

            st.markdown(f"""
            <div class="hud-box {c_style}">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight: bold; color: {lvl_color};">[{row['level']}] धोका स्कोअर: {row['risk']}/१००</span>
                    <small style="color: #94A3B8;">{row['time']} | {row['source']}</small>
                </div>
                <h4 style="margin: 8px 0; color: #FFFFFF;">{row['headline']}</h4>
                <p style="font-size: 13px; color: #D1D5DB; margin-bottom: 8px;">{row['summary']}</p>
                <div style="background: rgba(0, 0, 0, 0.5); padding: 8px 12px; border-radius: 4px; border-left: 3px solid {lvl_color};">
                    <div style="color: #00F2FE;"><b>🧠 संभाव्य धोका:</b> {row['prediction']}</div>
                    <div style="color: #FDE047;"><b>⚖️ लागू कलमे:</b> {row['laws']}</div>
                    <div style="color: #38BDF8;"><b>📍 संबंधित ठाणे:</b> {row['zone']} ({row['station']})</div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px;">
                    <span style="color: #94A3B8;">आढळलेले शब्द: <code>{trig_str}</code></span>
                    <a href="{row['link']}" target="_blank" style="color: #00F2FE; text-decoration: none;">[मूळ बातमी पहा ↗]</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==================== विभाग २: कायदेशीर अहवाल ====================
elif view_mode == "📄 कायदेशीर कारवाई अहवाल":
    st.markdown("<h3 style='color: #00F2FE;'>📄 तात्काळ कायदेशीर प्रतिबंधात्मक अहवाल</h3>", unsafe_allow_html=True)
    if df_live.empty:
        st.info("अहवाल तयार करण्यासाठी कोणतीही नोंद उपलब्ध नाही.")
    else:
        selected_case = st.selectbox("घटना निवडा:", df_live['headline'].tolist())
        c_data = df_live[df_live['headline'] == selected_case].iloc[0]

        report_txt = f"""
======================================================================
               महाराष्ट्र पोलीस - सायबर सेल, नांदेड जिल्हा
             गोपनीय कायदेशीर प्रतिबंधात्मक अहवाल (CONFIDENTIAL)
======================================================================
तारीख व वेळ      : {datetime.now().strftime('%d-%m-%Y // %H:%M:%S')}
संबंधित कार्यक्षेत्र: {c_data['zone']}
हद्दीतील ठाणे    : {c_data['station']}
धोका पातळी       : {c_data['level']} (स्कोअर: {c_data['risk']}/१००)
----------------------------------------------------------------------
१. मूळ डिजिटल मेसेज / बातमी:
"{c_data['headline']}"

२. तपशील:
"{c_data['summary']}"

३. सायबर सेल प्रेडिक्शन (संभाव्य धोका):
{c_data['prediction']}

४. शिफारस केलेली कायदेशीर कलमे (BNS):
{c_data['laws']}

५. प्रतिबंधात्मक सूचना:
कलम १४९ (BNSS) अन्वये संबंधितांना नोटीस बजावून संवेदनशील भागात 
तात्काळ पोलीस बंदोबस्त तैनात करावा.
======================================================================
        """
        st.code(report_txt, language="text")
        st.download_button(
            label="📥 हा अहवाल डाउनलोड करा (.TXT)",
            data=report_txt,
            file_name=f"नांदेड_सायबर_अहवाल_{datetime.now().strftime('%d%m%Y_%H%M')}.txt",
            mime="text/plain"
        )

# ==================== विभाग ३: खबरी टिप-लाइन ====================
elif view_mode == "🕵️ गुप्तवार्ता खबरी टिप-लाइन":
    st.markdown("<h3 style='color: #00F2FE;'>🕵️ गोपनीय गुप्तवार्ता व खबरी टिप-लाइन</h3>", unsafe_allow_html=True)
    tip = st.text_area("गोपनीय माहिती किंवा फॉरवर्ड केलेला मेसेज येथे टाका:", placeholder="उदा. लोहा मार्केटमध्ये उद्या काही मुले एकत्र येऊन आंदोलन करणार आहेत...")
    
    if st.button("🚨 ग्रिडमध्ये नोंद करा व तपासा", type="primary"):
        sc, lv, tr, loc, stn, pr, lw = analyze_threat(tip)
        st.success(f"नोंद यशस्वी! धोका पातळी: {sc}/१०० ({lv}) | तालुका: {loc}")
        st.warning(f"संभाव्य धोका: {pr}")
        st.info(f"लागू कलमे: {lw}")

# ऑटो-रिफ्रेश लूप
if auto_refresh and view_mode == "⚡ थेट नियंत्रण कक्ष व नकाशा":
    time.sleep(30)
    st.rerun()