import streamlit as st
import pandas as pd
import feedparser
import urllib.parse
import re
from datetime import datetime
import time
import folium
from streamlit_folium import st_folium

# --- १. मांडणी व हाय-टेक कमांड सेंटर CSS ---
st.set_page_config(
    page_title="नांदेड सायबर सेल - सर्वंकष सोशल मीडिया इंटेलिजन्स हब",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #030712; color: #D1D5DB; }
    
    @keyframes alert-glow {
        0% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.7); border-color: #EF4444; }
        50% { box-shadow: 0 0 25px rgba(239, 68, 68, 1); border-color: #F87171; }
        100% { box-shadow: 0 0 10px rgba(239, 68, 68, 0.7); border-color: #EF4444; }
    }
    
    .viral-flash {
        background: rgba(35, 5, 15, 0.95);
        border: 2px solid #EF4444;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 18px;
        animation: alert-glow 2s infinite;
    }
    
    .feed-card {
        background: rgba(13, 20, 36, 0.85);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 6px;
        padding: 14px;
        margin-bottom: 12px;
    }
    
    .badge-platform {
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        color: white;
    }
    .badge-yt { background-color: #FF0000; }
    .badge-fb { background-color: #1877F2; }
    .badge-insta { background: linear-gradient(45deg, #F09433 0%, #E6683C 25%, #DC2743 50%, #CC2366 75%, #BC1888 100%); }
    .badge-x { background-color: #000000; border: 1px solid #4B5563; }
    .badge-wa { background-color: #25D366; }
    .badge-web { background-color: #10B981; }
</style>
""", unsafe_allow_html=True)

# --- २. जिल्हानिहाय तालुके व स्थाने ---
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

# संवेदनशील कीवर्ड्स
KEYWORDS = {
    "VIOLENCE": ["कापाकापी", "तोडफोड", "दगडफेक", "मारहाण", "जाळपोळ", "राडा", "हल्ला", "खून", "कट्टा", "पिस्तूल", "तलवार", "rada", "todfod", "attack"],
    "MOBILIZATION": ["रास्ता रोको", "चक्का जाम", "बंद", "मोर्चा", "जमा व्हा", "एकत्र या", "आंदोलन", "पुतळा जाळला", "जोडे मारो", "घेराव", "morcha", "band"],
    "TENSION": ["लाठीचार्ज", "गोळीबार", "संचारबंदी", "इंटरनेट बंद", "कर्फ्यू", "पळापळ", "दंगल", "तणाव", "अफवा", "viral video", "reel"]
}

# --- ३. थ्रेट व प्रेडिक्शन इंजिन ---
def parse_threat_payload(text):
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
    level = "अतिसंवेदनशील" if final_score >= 65 else ("सावधगिरी" if final_score >= 35 else "सामान्य")
    loc_primary = detected_zones[0] if detected_zones else "नांदेड शहर"
    station = NANDED_GEO_LOCATIONS.get(loc_primary, {}).get("station", "स्थानिक नियंत्रण कक्ष")
    
    if "तोडफोड" in triggers or "दगडफेक" in triggers or "rada" in triggers:
        prediction = "व्हिडिओ व्हायरल होऊन कायदा-सुव्यवस्था बिघडणे व दगडफेकीची शक्यता."
        laws = "BNS १८९, १९१ (दंगल), IT Act कलम ६६"
    elif "मोर्चा" in triggers or "बंद" in triggers:
        prediction = "सोशल मीडियावर गर्दी जमवून रस्ता रोको किंवा बाजार बंद पाडण्याचे संकेत."
        laws = "BNS १८९ (बेकायदेशीर जमाव), कलम १४९ अन्वये प्रतिबंधात्मक नोटीस"
    elif "पुतळा" in triggers or "जोडे" in triggers:
        prediction = "गटसंघर्ष व राजकीय तणाव वाढवून सार्वजनिक शांतता भंग करणे."
        laws = "BNS १९६ (गटांमध्ये तेढ), BNS ३५६ (मानहानी)"
    else:
        prediction = "सामान्य संवाद; थेट शांतता भंगाचा धोका नाही."
        laws = "लागू नाही"
        
    return final_score, level, list(set(triggers)), loc_primary, station, prediction, laws

# --- ४. मल्टि-प्लॅटफॉर्म इंटेलिजन्स स्कॅनर ---
def scan_omni_platforms():
    queries = [
        # १. यूट्यूब व्हिडिओ / शॉर्ट्स
        "site:youtube.com नांदेड गुन्हा OR मोर्चा OR आंदोलन",
        # २. फेसबुक पब्लिक पोस्ट्स
        "site:facebook.com नांदेड बंद OR मोर्चा OR राडा",
        # ३. इन्स्टाग्राम रील्स / ट्रेंड्स
        "site:instagram.com नांदेड रील OR मोर्चा",
        # ४. एक्स (ट्विटर) व ओपन वेब
        "site:twitter.com नांदेड मोर्चा OR तणाव",
        "नांदेड व्हायरल व्हिडिओ गुन्हा when:1d"
    ]
    
    items = []
    for q in queries:
        encoded = urllib.parse.quote(q)
        rss_url = f"https://news.google.com/rss/search?q={encoded}&hl=mr&gl=IN&ceid=IN:mr"
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:6]:
            title = entry.title
            summary = getattr(entry, 'summary', title)
            clean = re.sub('<[^<]+?>', '', summary)
            full_msg = f"{title} {clean}"
            
            score, lvl, trigs, loc, station, pred, laws = parse_threat_payload(full_msg)
            
            # प्लॅटफॉर्म ओळखणे
            link_lower = entry.link.lower()
            if "youtube.com" in link_lower or "youtu.be" in link_lower:
                platform = "YouTube"
            elif "facebook.com" in link_lower:
                platform = "Facebook"
            elif "instagram.com" in link_lower:
                platform = "Instagram"
            elif "twitter.com" in link_lower or "x.com" in link_lower:
                platform = "X (Twitter)"
            else:
                platform = "ओपन वेब / न्यूज"
                
            items.append({
                "headline": title,
                "summary": clean,
                "time": getattr(entry, 'published', 'गेल्या २४ तासांत'),
                "platform": platform,
                "link": entry.link,
                "risk": score,
                "level": lvl,
                "zone": loc,
                "station": station,
                "triggers": trigs,
                "prediction": pred,
                "laws": laws
            })
            
    df = pd.DataFrame(items)
    if not df.empty:
        df = df.drop_duplicates(subset=["headline"]).sort_values(by="risk", ascending=False)
    return df

# --- ५. साइडबार मांडणी ---
st.sidebar.markdown("""
<div style="padding: 10px 0; border-bottom: 1px solid rgba(0, 242, 254, 0.3); margin-bottom: 15px;">
    <h3 style="color: #00F2FE; margin: 0;">महाराष्ट्र पोलीस</h3>
    <small style="color: #94A3B8;">नांदेड सोशल मीडिया इंटेलिजन्स सेल</small>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"**सिस्टीम वेळ:** `{datetime.now().strftime('%d-%m-%Y // %H:%M:%S')}`")
sound_alert = st.sidebar.toggle("🔊 व्हायरल सायरन (Critical Alert Audio)", value=True)
auto_refresh = st.sidebar.toggle("🔄 स्वयंचलित स्कॅन (दर ३० सेकंद)", value=True)

platform_filter = st.sidebar.selectbox("📱 प्लॅटफॉर्म निवडा:", ["सर्व प्लॅटफॉर्म्स", "YouTube", "Facebook", "Instagram", "X (Twitter)", "ओपन वेब / न्यूज"])
selected_taluka = st.sidebar.selectbox("📍 तालुका निवडा:", ["सर्व तालुके"] + list(NANDED_GEO_LOCATIONS.keys()))

st.sidebar.markdown("---")
view_mode = st.sidebar.radio("नेव्हिगेशन:", [
    "🛰️ मल्टि-सोशल मीडिया लाइव्ह कन्सोल", 
    "📲 व्हॉट्सॲप / टेलिग्राम व्हायरल इन्जेशन",
    "📄 कायदेशीर प्रतिबंधात्मक अहवाल"
])

# डेटा फेच
with st.spinner("यूट्यूब, फेसबुक, इन्स्टाग्राम व वेबवरून डेटा संकलित होत आहे..."):
    df_omni = scan_omni_platforms()

if platform_filter != "सर्व प्लॅटफॉर्म्स" and not df_omni.empty:
    df_omni = df_omni[df_omni['platform'] == platform_filter]

if selected_taluka != "सर्व तालुके" and not df_omni.empty:
    df_omni = df_omni[df_omni['zone'].str.contains(selected_taluka)]

# ==================== दृश्य १: मल्टि-सोशल मीडिया लाइव्ह कन्सोल ====================
if view_mode == "🛰️ मल्टि-सोशल मीडिया लाइव्ह कन्सोल":
    
    st.markdown("""
    <div style="background: rgba(10, 15, 30, 0.9); border: 1px solid rgba(0, 242, 254, 0.4); border-left: 6px solid #00F2FE; padding: 16px 20px; border-radius: 8px; margin-bottom: 20px;">
        <h2 style="margin: 0; color: #00F2FE; font-size: 22px;">
            🛰️ नांदेड जिल्हा : सर्वंकष सोशल मीडिया मॉनिटरिंग ग्रिड
        </h2>
        <div style="font-size: 13px; color: #94A3B8; margin-top: 5px;">
            YouTube, Instagram, Facebook, X आणि ओपन वेबवरील व्हायरल ट्रेंड्स व कायदा-सुव्यवस्थेचे स्वयंचलित ट्रॅकिंग
        </div>
    </div>
    """, unsafe_allow_html=True)

    crit_alerts = df_omni[df_omni['level'] == 'अतिसंवेदनशील'] if not df_omni.empty else pd.DataFrame()

    if not crit_alerts.empty:
        top_v = crit_alerts.iloc[0]
        if sound_alert:
            st.markdown("""
            <audio autoplay>
                <source src="https://actions.google.com/sounds/v1/alarms/alarm_clock.ogg" type="audio/ogg">
            </audio>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="viral-flash">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="background: #EF4444; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">🚨 अतिसंवेदनशील व्हायरल धोका</span>
                <span style="color: #00F2FE;">प्लॅटफॉर्म: {top_v['platform']} | हद्द: {top_v['zone']}</span>
            </div>
            <h3 style="color: #FFFFFF; margin: 10px 0;">{top_v['headline']}</h3>
            <p style="color: #FECDD3; font-size: 14px;">{top_v['summary']}</p>
            <div style="background: rgba(0, 0, 0, 0.6); padding: 10px; border-radius: 6px; border: 1px solid #EF4444;">
                <div style="color: #00F2FE;"><b>🧠 AI प्रेडिक्शन:</b> {top_v['prediction']}</div>
                <div style="color: #FBBF24;"><b>⚖️ लागू कलमे:</b> {top_v['laws']}</div>
                <div style="color: #34D399;"><b>🚨 ठाणे निर्देश:</b> {top_v['station']} ला वायरलेसद्वारे सतर्क करावे.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # मेट्रिक्स
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("एकूण स्कॅन नोंदी", len(df_omni))
    with c2: st.metric("अतिसंवेदनशील अलर्ट्स", len(crit_alerts), delta=f"+{len(crit_alerts)}" if len(crit_alerts)>0 else "0", delta_color="inverse")
    with c3: st.metric("सावधगिरीच्या नोंदी", len(df_omni[df_omni['level'] == 'सावधगिरी']) if not df_omni.empty else 0)
    with c4: st.metric("शांतता स्थिती", "तणावग्रस्त" if len(crit_alerts)>0 else "नियंत्रणात")

    st.markdown("---")
    st.subheader("🗺️ नांदेड जिल्हा: सोशल मीडिया हॉटस्पॉट नकाशा")

    m = folium.Map(location=[19.1526, 77.3162], zoom_start=9, tiles="OpenStreetMap")
    if not df_omni.empty:
        for _, r in df_omni.iterrows():
            coords = NANDED_GEO_LOCATIONS.get(r['zone'], NANDED_GEO_LOCATIONS["नांदेड शहर"])
            marker_color = "#EF4444" if r['level'] == 'अतिसंवेदनशील' else ("#F59E0B" if r['level'] == 'सावधगिरी' else "#00F2FE")
            folium.CircleMarker(
                location=[coords["lat"], coords["lon"]],
                radius=14 if r['level'] == 'अतिसंवेदनशील' else 8,
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                popup=f"{r['platform']} | {r['zone']} | स्कोअर: {r['risk']}/१००"
            ).add_to(m)
    st_folium(m, width="100%", height=350)

    st.markdown("---")
    st.subheader("⚡ थेट मल्टि-प्लॅटफॉर्म प्रवाह व विश्लेषण")

    if df_omni.empty:
        st.info("या निवडलेल्या पर्यायात सध्या कोणतीही आक्षेपार्ह पोस्ट आढळली नाही.")
    else:
        for _, row in df_omni.iterrows():
            if row['platform'] == "YouTube": badge_cls = "badge-yt"
            elif row['platform'] == "Facebook": badge_cls = "badge-fb"
            elif row['platform'] == "Instagram": badge_cls = "badge-insta"
            elif row['platform'] == "X (Twitter)": badge_cls = "badge-x"
            else: badge_cls = "badge-web"

            st.markdown(f"""
            <div class="feed-card">
                <div style="display: flex; justify-content: space-between;">
                    <span><span class="badge-platform {badge_cls}">{row['platform']}</span> <b>[{row['level']}] स्कोअर: {row['risk']}/१००</b></span>
                    <small style="color: #94A3B8;">{row['time']}</small>
                </div>
                <h4 style="margin: 8px 0; color: #FFFFFF;">{row['headline']}</h4>
                <p style="font-size: 13px; color: #D1D5DB;">{row['summary']}</p>
                <div style="background: rgba(0, 0, 0, 0.4); padding: 8px; border-radius: 4px; font-size: 12px;">
                    <span style="color: #00F2FE;"><b>🧠 AI प्रेडिक्शन:</b> {row['prediction']}</span><br>
                    <span style="color: #FDE047;"><b>⚖️ कायदेशीर कलमे:</b> {row['laws']}</span> | 
                    <span style="color: #38BDF8;"><b>📍 ठाणे:</b> {row['zone']} ({row['station']})</span>
                </div>
                <div style="margin-top: 6px;">
                    <a href="{row['link']}" target="_blank" style="color: #00F2FE; font-size: 12px;">[मूळ पोस्ट / व्हिडिओ पहा ↗]</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==================== दृश्य २: व्हॉट्सॲप / टेलिग्राम इन्जेशन ====================
elif view_mode == "📲 व्हॉट्सॲप / टेलिग्राम व्हायरल इन्जेशन":
    st.markdown("<h3 style='color: #00F2FE;'>📲 व्हॉट्सॲप व टेलिग्राम गुप्तवार्ता इन्जेशन कन्सोल</h3>", unsafe_allow_html=True)
    st.write("व्हॉट्सॲपच्या बंद ग्रुप्समध्ये किंवा टेलिग्राम चॅनेल्सवर फिरणारे फॉरवर्डेड मेसेज, ऑडिओचा मजकूर किंवा रील्सचे कॅप्शन येथे दाखल करा:")

    wa_text = st.text_area("व्हाट्सॲप / टेलिग्राम मेसेज पेस्ट करा:", height=120, 
                           placeholder="उदा. उद्या सकाळी ९ वाजता सर्व कार्यकर्त्यांनी लोहा तहसीलवर जमा व्हा, मोठा राडा होणार आहे...")
    source_channel = st.selectbox("माहितीचा स्रोत निवडा:", ["व्हॉट्सॲप ग्रुप फॉरवर्ड", "टेलिग्राम चॅनेल", "नागरिक सायबर टिप", "गोपनीय खबरी"])

    if st.button("🚨 तात्काळ सायबर फॉरेन्सिक तपासणी करा", type="primary"):
        sc, lv, tr, loc, stn, pr, lw = parse_threat_payload(wa_text)
        
        st.markdown("### 📋 प्राथमिक तपासणी अहवाल:")
        ca, cb, cc = st.columns(3)
        with ca: st.metric("धोका स्कोअर", f"{sc}/१००")
        with cb: st.metric("धोका वर्गवारी", lv)
        with cc: st.metric("संबंधित हद्द", loc)

        if lv == "अतिसंवेदनशील":
            st.error(f"🚨 **अतिसंवेदनशील इशारा:** {loc} परिसरात गर्दी जमवून हिंसाचार होण्याची शक्यता. कलम १४९ अन्वये प्रतिबंधात्मक ताकीद द्यावी.")
        elif lv == "सावधगिरी":
            st.warning("⚠️ **सावधगिरी:** अफवा किंवा सामाजिक तणाव निर्माण होण्याची चिन्हे आहेत.")
        else:
            st.success("✅ **सामान्य:** शांतता भंगाचा थेट धोका आढळला नाही.")

        st.info(f"🧠 **AI प्रेडिक्शन:** {pr}")
        st.warning(f"⚖️ **लागू फौजदारी कलमे:** {lw}")

# ==================== दृश्य ३: कायदेशीर अहवाल ====================
elif view_mode == "📄 कायदेशीर प्रतिबंधात्मक अहवाल":
    st.markdown("<h3 style='color: #00F2FE;'>📄 कायदेशीर कारवाई अहवाल</h3>", unsafe_allow_html=True)
    if df_omni.empty:
        st.info("अहवाल तयार करण्यासाठी सध्या कोणतीही नोंद उपलब्ध नाही.")
    else:
        selected_case = st.selectbox("घटना निवडा:", df_omni['headline'].tolist())
        c_data = df_omni[df_omni['headline'] == selected_case].iloc[0]

        report_txt = f"""
======================================================================
               महाराष्ट्र पोलीस - सायबर सेल, नांदेड जिल्हा
             गोपनीय कायदेशीर प्रतिबंधात्मक अहवाल (CONFIDENTIAL)
======================================================================
तारीख व वेळ      : {datetime.now().strftime('%d-%m-%Y // %H:%M:%S')}
प्लॅटफॉर्म        : {c_data['platform']}
संबंधित कार्यक्षेत्र: {c_data['zone']}
हद्दीतील ठाणे    : {c_data['station']}
धोका पातळी       : {c_data['level']} (स्कोअर: {c_data['risk']}/१००)
----------------------------------------------------------------------
१. मूळ डिजिटल मेसेज / शीर्षक:
"{c_data['headline']}"

२. तपशील:
"{c_data['summary']}"

३. सायबर सेल प्रेडिक्शन (संभाव्य धोका):
{c_data['prediction']}

४. शिफारस केलेली कायदेशीर कलमे (BNS):
{c_data['laws']}

५. प्रतिबंधात्मक सूचना:
संबंधित ठाणे प्रभारींनी कलम १४९ अन्वये संबंधितांना नोटीस बजावून 
संवेदनशील चौकात अतिरिक्त पोलीस बंदोबस्त तैनात करावा.
======================================================================
        """
        st.code(report_txt, language="text")
        st.download_button(
            label="📥 अहवाल डाउनलोड करा (.TXT)",
            data=report_txt,
            file_name=f"नांदेड_सोशल_अहवाल_{datetime.now().strftime('%d%m%Y_%H%M')}.txt",
            mime="text/plain"
        )

# ऑटो-रिफ्रेश लूप
if auto_refresh and view_mode == "🛰️ मल्टि-सोशल मीडिया लाइव्ह कन्सोल":
    time.sleep(30)
    st.rerun()