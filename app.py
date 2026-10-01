import streamlit as st
import pandas as pd
from datetime import datetime

# --- १. पेज कॉन्फिगरेशन ---
st.set_page_config(
    page_title="नांदेड सायबर सेल - सोशल मीडिया पूर्वसूचना केंद्र",
    page_icon="🚨",
    layout="wide"
)

# --- २. नांदेड जिल्हा पोलीस ठाणी, वायरलेस व नकाशाचे अचूक GPS निर्देशक ---
POLICE_JURISDICTION_MAP = {
    "माहूर": {
        "ps": "माहूर पोलीस ठाणे", 
        "wireless": "माहूर व सिंदखेड ठाणे",
        "lat": 19.8363, "lon": 77.9157
    },
    "किनवट": {
        "ps": "किनवट पोलीस ठाणे", 
        "wireless": "किनवट व इस्लापूर ठाणे",
        "lat": 19.6333, "lon": 78.2000
    },
    "हदगाव": {
        "ps": "हदगाव पोलीस ठाणे", 
        "wireless": "हदगाव ठाणे व मनाठा बीट",
        "lat": 19.5000, "lon": 77.6667
    },
    "भोकर": {
        "ps": "भोकर पोलीस ठाणे", 
        "wireless": "भोकर ठाणे",
        "lat": 19.2167, "lon": 77.6833
    },
    "लोहा": {
        "ps": "लोहा पोलीस ठाणे", 
        "wireless": "लोहा ठाणे",
        "lat": 18.9500, "lon": 77.1167
    },
    "कंधार": {
        "ps": "कंधार पोलीस ठाणे", 
        "wireless": "कंधार ठाणे",
        "lat": 18.8833, "lon": 77.2000
    },
    "मुखेड": {
        "ps": "मुखेड पोलीस ठाणे", 
        "wireless": "मुखेड ठाणे",
        "lat": 18.7167, "lon": 77.3667
    },
    "देगलूर": {
        "ps": "देगलूर पोलीस ठाणे", 
        "wireless": "देगलूर ठाणे",
        "lat": 18.5500, "lon": 77.5833
    },
    "बिलोली": {
        "ps": "बिलोली पोलीस ठाणे", 
        "wireless": "बिलोली व कुंडलवाडी ठाणे",
        "lat": 18.7667, "lon": 77.7333
    },
    "धर्माबाद": {
        "ps": "धर्माबाद पोलीस ठाणे", 
        "wireless": "धर्माबाद ठाणे",
        "lat": 18.8833, "lon": 77.8500
    },
    "नायगाव": {
        "ps": "नायगाव पोलीस ठाणे", 
        "wireless": "नायगाव ठाणे",
        "lat": 18.8500, "lon": 77.5333
    },
    "उमरी": {
        "ps": "उमरी पोलीस ठाणे", 
        "wireless": "उमरी ठाणे",
        "lat": 19.0667, "lon": 77.7000
    },
    "मुदखेड": {
        "ps": "मुदखेड पोलीस ठाणे", 
        "wireless": "मुदखेड ठाणे",
        "lat": 19.1667, "lon": 77.5167
    },
    "अर्धापूर": {
        "ps": "अर्धापूर पोलीस ठाणे", 
        "wireless": "अर्धापूर ठाणे",
        "lat": 19.2667, "lon": 77.3833
    },
    "नांदेड शहर": {
        "ps": "नांदेड नियंत्रण कक्ष", 
        "wireless": "वजिराबाद / इतवारा / भाग्यनगर",
        "lat": 19.1383, "lon": 77.3210
    }
}

# --- ३. कायदा व सुव्यवस्था धोक्याची पूर्वसूचना देणारे संवेदनशील शब्द (Watchlist) ---
SENSITIVE_KEYWORDS = [
    "रास्ता रोको", "चक्काजाम", "आंदोलन", "मोर्चा", "धरणे", "बंद", 
    "तोडफोड", "दगडफेक", "राडा", "घेराव", "आत्मदहन", "तणाव", 
    "बाजारपेठ बंद", "हायवे रोखणे", "पुतळा जाळणे", "बहिष्कार"
]

def scan_text_intelligence(text):
    """मजकूर, रील किंवा बातमीतून संवेदनशील शब्द आणि पोलीस ठाणे स्वयंचलित ओळखणे"""
    detected_words = [kw for kw in SENSITIVE_KEYWORDS if kw in text]
    
    # ठाणे मॅपिंग
    matched_station = POLICE_JURISDICTION_MAP["नांदेड शहर"]
    location_name = "नांदेड शहर"
    
    for place, info in POLICE_JURISDICTION_MAP.items():
        if place in text:
            matched_station = info
            location_name = place
            break
            
    return detected_words, location_name, matched_station

# --- ४. थेट सोशल मीडिया व रील/बातमी डेटा ---
LIVE_INTEL_DATA = [
    {
        "id": "NND-2026-091",
        "time": "१० मिनिटांपूर्वी",
        "source": "Instagram Reel",
        "source_icon": "📸",
        "author": "@nanded_news_express",
        "text": "हायवेच्या रखडलेल्या कामा विरोधात माहूरमध्ये रास्ता रोको आंदोलन आणि बाजारपेठ बंद चे आवाहन ! #news #nanded #viral",
        "forward_velocity": 85,
        "total_forwards": 1850,
        "reaction_velocity": 190,
        "total_reactions": 4200,
        "angry_reactions": "६२%",
        "support_reactions": "२८%",
        "risk": "वाहतूक रोखणे, महामार्ग रोखणे व बाजारपेठ बंद पाडण्याचे नियोजन."
    },
    {
        "id": "NND-2026-092",
        "time": "२५ मिनिटांपूर्वी",
        "source": "WhatsApp Forward",
        "source_icon": "💬",
        "author": "नांदेड शेतकरी विकास मंच (ग्रुप)",
        "text": "लोहा बाजार समितीत सोयाबीन दरावरून उद्या सकाळी ११ वाजता ठिय्या मोर्चा व चक्काजाम इशारा.",
        "forward_velocity": 28,
        "total_forwards": 620,
        "reaction_velocity": 45,
        "total_reactions": 1150,
        "angry_reactions": "४५%",
        "support_reactions": "४०%",
        "risk": "बाजार समिती कामकाज बंद पाडणे व वाहने रोखणे."
    },
    {
        "id": "NND-2026-093",
        "time": "४० मिनिटांपूर्वी",
        "source": "Telegram Broadcast",
        "source_icon": "📢",
        "author": "मराठवाडा व्हॉइस",
        "text": "किनवट परिसरातील जंगलात संशयित हालचाली बाबत व्हायरल क्लिप फिरत आहे.",
        "forward_velocity": 6,
        "total_forwards": 190,
        "reaction_velocity": 12,
        "total_reactions": 310,
        "angry_reactions": "१५%",
        "support_reactions": "१२%",
        "risk": "अफवा पसरवणे व नागरिकांमध्ये संभ्रम निर्माण करणे."
    }
]

# --- ५. साइडबार (फक्त २ मुख्य पर्याय) ---
with st.sidebar:
    st.markdown("## 🚨 सायबर सेल नांदेड")
    st.caption("स्वयंचलित सोशल मीडिया पूर्वसूचना केंद्र v2.2")
    st.markdown("---")
    
    menu_selection = st.radio(
        "कार्यकारी नियंत्रण:",
        ["📡 लाइव्ह रडार (Live Radar)", "🗄️ ऐतिहासिक डेटाबेस (Historical Database)"]
    )
    st.markdown("---")
    st.checkbox("स्वयंचलित रिफ्रेश (३० सेकंद)", value=True)
    st.info("२४×७ कीवर्ड स्कॅनर व हॉटस्पॉट मॅप सक्रिय")

# --- ६. मुख्य स्क्रीन : लाइव्ह रडार ---
if menu_selection == "📡 लाइव्ह रडार (Live Radar)":
    st.subheader("🚨 नांदेड जिल्हा : २४×७ स्वयंचलित सोशल मीडिया पूर्वसूचना कमांड सेंटर")
    st.caption("मेसेज, व्हिडिओ, रील आणि बातम्यांमधील कायदा-सुव्यवस्था बाधक शब्द व हॉटस्पॉटचे थेट ट्रॅकिंग")
    
    # सारांश मेट्रिक्स
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("एकूण संशयित नोंदी", "१४")
    m2.metric("रेड अलर्ट्स (अतिसंवेदनशील)", "२", "+२")
    m3.metric("सर्वाधिक फॉरवर्ड गती", "८५ / मिनिट", "वाढता कल ⚡")
    m4.metric("जिल्हा शांतता स्थिती", "सतर्क (Alert)")
    
    st.markdown("---")

    # ४ नंबर फिचर: नांदेड जिल्हा हॉटस्पॉट नकाशा (Live Heatmap)
    st.markdown("### 🗺️ नांदेड जिल्हा : सक्रिय कायदा व सुव्यवस्था हॉटस्पॉट नकाशा")
    map_points = []
    for item in LIVE_INTEL_DATA:
        _, _, st_data = scan_text_intelligence(item["text"])
        map_points.append({"lat": st_data["lat"], "lon": st_data["lon"]})
    
    map_df = pd.DataFrame(map_points)
    # स्ट्रीमलिटचा इनबिल्ट मॅप
    st.map(map_df, zoom=9)
    st.caption("🔴 वरील नकाशातील बिंदू ज्या भागात आंदोलने/तणावपूर्ण मेसेज व्हायरल होत आहेत ती पोलीस ठाणे हद्द दर्शवतात.")
    st.markdown("---")

    # मेसेज आणि बातम्यांचे कार्ड्स
    for post in LIVE_INTEL_DATA:
        flagged_words, loc_name, st_info = scan_text_intelligence(post["text"])
        is_threat = len(flagged_words) > 0
        is_viral = post["forward_velocity"] > 30

        with st.container():
            col_alert, col_source = st.columns([3, 1])
            
            with col_alert:
                if is_viral and is_threat:
                    st.error(f"🚨 **अतिसंवेदनशील रेड अलर्ट (कायदा-सुव्यवस्था धोका + तीव्र व्हायरल: {post['forward_velocity']} फॉरवर्ड्स/मि.)**")
                elif is_threat:
                    st.warning("⚠️ **कायदा व सुव्यवस्था पूर्वसूचना (संवेदनशील शब्द आढळले)**")
                else:
                    st.info("ℹ️ **सर्वसाधारण देखरेख (Normal Watch)**")
            
            with col_source:
                st.markdown(f"**मूळ स्त्रोत:** `{post['source_icon']} {post['source']}`")
                st.caption(f"हँडल/ग्रुप: {post['author']} | {post['time']}")

            st.markdown(f"### {post['text']}")

            # ३ नंबर फिचर: स्वयंचलित डिटेक्ट झालेले संवेदनशील शब्द (कीवर्ड टॅग्स)
            if flagged_words:
                tags_display = " ".join([f"`🚩 {w}`" for w in flagged_words])
                st.markdown(f"**डिटेक्ट झालेले संवेदनशील कीवर्ड्स:** {tags_display}")

            # फॉरवर्ड आणि प्रतिक्रियेचा वेग आणि काउंट
            met1, met2, met3, met4 = st.columns(4)
            met1.metric(label="📤 फॉरवर्ड गती", value=f"{post['forward_velocity']} प्रति मिनिट", delta="गती तीव्र" if post['forward_velocity'] > 30 else "मंद")
            met2.metric(label="📊 एकूण फॉरवर्ड्स", value=f"{post['total_forwards']:,}")
            met3.metric(label="⚡ प्रतिक्रिया गती", value=f"{post['reaction_velocity']} प्रति मिनिट", delta=f"संतप्त: {post['angry_reactions']}")
            met4.metric(label="💬 एकूण प्रतिक्रिया", value=f"{post['total_reactions']:,}")

            # हद्द आणि वायरलेस निर्देश
            c_info1, c_info2 = st.columns(2)
            with c_info1:
                st.markdown(f"📍 **अचूक हद्द (पोलीस ठाणे):** `{st_info['ps']}`")
                st.markdown(f"⚠️ **संभाव्य धोका:** {post['risk']}")
            
            with c_info2:
                st.markdown(f"📻 **वायरलेस निर्देश:** `{st_info['wireless']} ला तात्काळ सतर्क करावे.`")
                st.markdown(f"👥 **जनभावना कल:** संताप: `{post['angry_reactions']}` | समर्थन: `{post['support_reactions']}`")

            st.markdown("---")

# --- ७. मुख्य स्क्रीन : ऐतिहासिक डेटाबेस ---
elif menu_selection == "🗄️ ऐतिहासिक डेटाबेस (Historical Database)":
    st.subheader("🗄️ ऐतिहासिक डेटाबेस व ट्रेंड ॲनालिसिस")
    st.caption("मागील घटना, मेसेज फॉरवर्ड काउंट्स आणि संवेदनशील घटनांचे रेकॉर्ड.")

    f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
    with f_col1:
        search_query = st.text_input("🔍 शब्द किंवा पोलीस ठाण्यावरून शोधा:")
    with f_col2:
        source_filter = st.selectbox("प्लॅटफॉर्म निवडा:", ["सर्व", "Instagram Reel", "WhatsApp Forward", "Telegram Broadcast"])
    with f_col3:
        status_filter = st.selectbox("स्थिती निवडा:", ["सर्व", "रेड अलर्ट", "पूर्वसूचना"])

    history_records = [
        {"तारीख व वेळ": "01-10-2026 18:55", "स्त्रोत": "Instagram Reel", "पोलीस ठाणे": "माहूर पोलीस ठाणे", "घटना": "रास्ता रोको आंदोलन", "डिटेक्ट कीवर्ड": "रास्ता रोको, बंद", "एकूण फॉरवर्ड": "1,850", "फॉरवर्ड गती": "85/मि.", "अलर्ट": "रेड अलर्ट"},
        {"तारीख व वेळ": "01-10-2026 17:30", "स्त्रोत": "WhatsApp Forward", "पोलीस ठाणे": "लोहा पोलीस ठाणे", "घटना": "सोयाबीन दर ठिय्या मोर्चा", "डिटेक्ट कीवर्ड": "मोर्चा, चक्काजाम", "एकूण फॉरवर्ड": "620", "फॉरवर्ड गती": "28/मि.", "अलर्ट": "पूर्वसूचना"},
        {"तारीख व वेळ": "01-10-2026 15:10", "स्त्रोत": "Telegram Broadcast", "पोलीस ठाणे": "किनवट पोलीस ठाणे", "घटना": "जंगलातील संशयित क्लिप", "डिटेक्ट कीवर्ड": "तणाव", "एकूण फॉरवर्ड": "190", "फॉरवर्ड गती": "6/मि.", "अलर्ट": "सर्वसाधारण"}
    ]

    df = pd.DataFrame(history_records)
    st.dataframe(df, use_container_width=True)

    st.download_button(
        label="📥 ऐतिहासिक डेटा एक्सेल/CSV मध्ये डाऊनलोड करा",
        data=df.to_csv(index=False).encode('utf-8-sig'),
        file_name="Nanded_Cyber_Intel_Archive.csv",
        mime="text/csv"
    )