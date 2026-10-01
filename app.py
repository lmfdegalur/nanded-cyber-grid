import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

# --- १. पेज कॉन्फिगरेशन व हाय-टेक स्टाइलिंग ---
st.set_page_config(
    page_title="सायबर सेल नांदेड - पूर्वसूचना व फील्ड कमांड सेंटर",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main { background-color: #0b0f19; color: #e2e8f0; }
    .stMetric { background-color: #161e2e; padding: 12px; border-radius: 8px; border: 1px solid #2d3748; }
    .alert-card-communal {
        background: linear-gradient(135deg, rgba(185, 28, 28, 0.25) 0%, rgba(15, 23, 42, 0.95) 100%);
        border-left: 6px solid #b91c1c;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(185, 28, 28, 0.3);
    }
    .alert-card-red {
        background: linear-gradient(135deg, rgba(220, 38, 38, 0.15) 0%, rgba(15, 23, 42, 0.9) 100%);
        border-left: 5px solid #ef4444;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .alert-card-normal {
        background: #1e293b;
        border-left: 5px solid #eab308;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 20px;
    }
    .badge-communal { background-color: #991b1b; color: white; padding: 4px 10px; border-radius: 4px; font-weight: bold; font-size: 12px; border: 1px solid #f87171; }
    .badge-red { background-color: #ef4444; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .badge-yellow { background-color: #eab308; color: black; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px; }
    .tag-communal { background-color: #450a0a; color: #fca5a5; padding: 2px 6px; border-radius: 4px; font-size: 12px; margin-right: 5px; border: 1px solid #991b1b; }
    .tag-kw { background-color: #1e3a8a; color: #bfdbfe; padding: 2px 6px; border-radius: 4px; font-size: 12px; margin-right: 5px; }
    .intel-box { background-color: #0f172a; padding: 12px; border-radius: 6px; border: 1px solid #334155; margin-top: 10px; }
    .field-box { background-color: #1e1b4b; padding: 10px; border-radius: 6px; border: 1px solid #4338ca; margin-top: 8px; }
</style>
""", unsafe_allow_html=True)

# --- २. नांदेड जिल्हा पोलीस ठाणी व बीट मार्शल नेटवर्क ---
POLICE_JURISDICTION_MAP = {
    "माहूर": {"ps": "माहूर पोलीस ठाणे", "wireless": "माहूर व सिंदखेड ठाणे", "beat_unit": "डायल ११२ व्हॅन-०४ (माहूर बीट)"},
    "किनवट": {"ps": "किनवट पोलीस ठाणे", "wireless": "किनवट व इस्लापूर ठाणे", "beat_unit": "डायल ११२ व्हॅन-०७ (किनवट शहर)"},
    "हदगाव": {"ps": "हदगाव पोलीस ठाणे", "wireless": "हदगाव ठाणे व मनाठा बीट", "beat_unit": "बीट मार्शल-०२ (हदगाव)"},
    "भोकर": {"ps": "भोकर पोलीस ठाणे", "wireless": "भोकर ठाणे", "beat_unit": "डायल ११२ व्हॅन-०३ (भोकर)"},
    "लोहा": {"ps": "लोहा पोलीस ठाणे", "wireless": "लोहा ठाणे", "beat_unit": "बीट मार्शल-०१ (लोहा बाजार)"},
    "कंधार": {"ps": "कंधार पोलीस ठाणे", "wireless": "कंधार ठाणे", "beat_unit": "डायल ११२ व्हॅन-०५ (कंधार)"},
    "मुखेड": {"ps": "मुखेड पोलीस ठाणे", "wireless": "मुखेड ठाणे", "beat_unit": "बीट मार्शल-०३ (मुखेड)"},
    "देगलूर": {"ps": "देगलूर पोलीस ठाणे", "wireless": "देगलूर ठाणे", "beat_unit": "डायल ११२ व्हॅन-०२ (देगलूर नाका)"},
    "बिलोली": {"ps": "बिलोली पोलीस ठाणे", "wireless": "बिलोली व कुंडलवाडी ठाणे", "beat_unit": "बीट मार्शल-०१ (बिलोली)"},
    "धर्माबाद": {"ps": "धर्माबाद पोलीस ठाणे", "wireless": "धर्माबाद ठाणे", "beat_unit": "डायल ११२ व्हॅन-०६ (धर्माबाद)"},
    "नायगाव": {"ps": "नायगाव पोलीस ठाणे", "wireless": "नायगाव ठाणे", "beat_unit": "बीट मार्शल-०२ (नायगाव)"},
    "उमरी": {"ps": "उमरी पोलीस ठाणे", "wireless": "उमरी ठाणे", "beat_unit": "डायल ११२ व्हॅन-०८ (उमरी)"},
    "मुदखेड": {"ps": "मुदखेड पोलीस ठाणे", "wireless": "मुदखेड ठाणे", "beat_unit": "बीट मार्शल-०१ (मुदखेड)"},
    "अर्धापूर": {"ps": "अर्धापूर पोलीस ठाणे", "wireless": "अर्धापूर ठाणे", "beat_unit": "डायल ११२ व्हॅन-०१ (अर्धापूर हायवे)"},
    "नांदेड": {"ps": "नांदेड नियंत्रण कक्ष (मुख्यालय)", "wireless": "वजिराबाद / इतवारा / भाग्यनगर", "beat_unit": "कंट्रोल रूम क्यूआरटी (QRT Strike Team)"}
}

LAW_ORDER_KEYWORDS = ["रास्ता रोको", "चक्काजाम", "आंदोलन", "मोर्चा", "धरणे", "बंद", "तोडफोड", "दगडफेक", "राडा", "घेराव", "आत्मदहन", "बाजारपेठ बंद", "हायवे रोखणे"]
COMMUNAL_POLITICAL_KEYWORDS = ["दंगल", "जातीय तेढ", "धार्मिक भावना", "पुतळ्याची विटंबना", "झेंडा काढला", "धर्माचा अपमान", "जातीचा अपमान", "गटबाजी", "मारहाण", "बहिष्कार", "धमकी", "चुनौती", "धार्मिक तेढ", "राजकीय राडा", "कार्यकर्ते आमनेसामने"]

def scan_text_intel(text):
    law_flagged = [kw for kw in LAW_ORDER_KEYWORDS if kw in text]
    communal_flagged = [kw for kw in COMMUNAL_POLITICAL_KEYWORDS if kw in text]
    matched_info = POLICE_JURISDICTION_MAP["नांदेड"]
    for place, info in POLICE_JURISDICTION_MAP.items():
        if place in text:
            matched_info = info
            break
    return law_flagged, communal_flagged, matched_info

# --- ३. रिअल-टाइम इंटेलिजन्स डेटाबेस ---
LIVE_INTEL_DATA = [
    {
        "id": "NND-COM-201",
        "time": "५ मिनिटांपूर्वी",
        "type": "व्हिडिओ व मजकूर पोस्ट",
        "category": "सामाजिक / धार्मिक तेढ",
        "source": "स्थानिक न्यूज पोर्टल (Web News)",
        "source_icon": "📺",
        "author": "नांदेड लाइव्ह २४ न्यूज",
        "text": "देगलूर नाका परिसरात धार्मिक झेंडा काढल्याच्या संशयावरून दोन गटांत तणाव; आज रात्री ८:३० वाजता चौकात जमा होण्याचे आवाहन, जातीय तेढ निर्माण करणारा व्हिडिओ व्हायरल.",
        "forward_velocity": 125,
        "total_forwards": 3400,
        "reaction_velocity": 240,
        "total_reactions": 6100,
        "is_communal": True,
        "is_red_alert": True,
        "threat_score": 94,
        "risk_desc": "जातीय/धार्मिक तणाव पसरणे, जमाव एकत्र येणे आणि दगडफेकीची दाट शक्यता.",
        "angry_percent": 82,
        "predicted_spot": "देगलूर नाका मुख्य चौक, नांदेड",
        "predicted_time": "आज रात्री ०८:३० PM",
        "fact_check_status": "⚠️ संशयित फेक व्हिडिओ (हा व्हिडिओ २०२१ मधील परराज्यातील घटनेचा आहे)",
        "network_threat": "🚨 संशयित बॉट नेटवर्क ॲक्टिव्हिटी (एकाच वेळी ३५ ग्रुप्समध्ये फॉरवर्ड)",
        "audio_transcription": None,
        "field_status": "🚨 बीट मार्शल रवाना (डायल ११२ पोहोचत आहे)",
        "sample_comments": ["त्या भागात आपले लोक पाठवा, गप्प बसायचे नाही!", "अफवा पसरवू नका, शांतता राखा."],
        "key_figures": [
            {"नाव": "सचिन कदम (@sachin_yuva)", "हँडल": "X (Twitter) & FB", "रोल": "भडकावू पोस्टकर्ता", "प्लॅटफॉर्म": "X (Twitter)", "कृती": "जुना व्हिडिओ जोडून तेढ निर्माण करण्याचा प्रयत्न.", "जोखीम": "🔴 अतिसंवेदनशील"},
            {"नाव": "सय्यद आरिफ (मो. ९९२१०XXXXX)", "हँडल": "WhatsApp Group Admin", "रोल": "ग्रुप मोबिलायझर", "प्लॅटफॉर्म": "स्थानिक वॉट्सअ‍ॅप ग्रुप", "कृती": "चौकात एकत्र येण्यासाठी ऑडिओ कॉल फॉरवर्ड केला.", "जोखीम": "🔴 अतिसंवेदनशील"}
        ]
    },
    {
        "id": "NND-AUDIO-205",
        "time": "१२ मिनिटांपूर्वी",
        "type": "व्हायरल ऑडिओ क्लिप (Voice Note)",
        "category": "कायदा व सुव्यवस्था / जमाव",
        "source": "WhatsApp Audio Note",
        "source_icon": "🎙️",
        "author": "अज्ञात फॉरवर्ड (Forwarded Many Times)",
        "text": "किनवट तालुक्यातील जंगलात तोडफोड आणि उद्या सकाळी सर्व युवकांनी तहसीलवर मोर्चा नेण्याबाबत ऑडिओ क्लिप.",
        "forward_velocity": 78,
        "total_forwards": 1950,
        "reaction_velocity": 130,
        "total_reactions": 2400,
        "is_communal": False,
        "is_red_alert": True,
        "threat_score": 86,
        "risk_desc": "नागरिकांची दिशाभूल करून बेकायदेशीर मोर्चा व जमाव जमवणे.",
        "angry_percent": 65,
        "predicted_spot": "किनवट तहसील कार्यालय चौक",
        "predicted_time": "उद्या सकाळी ०९:३० AM",
        "fact_check_status": "🔍 स्थानिक ऑडिओ (सत्यता पडताळणी सायबर सेलकडे)",
        "network_threat": "⚡ तीव्र फॉरवर्ड गती (डार्क ग्रुप्समधून प्रसार)",
        # ऑडिओ ट्रान्सक्रिप्शन विभाग
        "audio_transcription": "“सर्व भावांना विनंती आहे, किनवट भागात जो प्रकार घडलाय त्याचा निषेध करण्यासाठी उद्या सकाळी ९:३० वाजता तहसीलवर मोर्चा काढायचा आहे. प्रत्येकाने येताना गाड्या घेऊन या, रस्ता रोको करायचा आहे.”",
        "field_status": "🟡 किनवट बीट अंमलदार सतर्क (पडताळणी सुरू)",
        "sample_comments": ["आम्ही सकाळी ९ वाजताच पोहोचू.", "कोणत्या संघटनेचा मोर्चा आहे?"],
        "key_figures": [
            {"नाव": "ऑडिओ स्पीकर (व्हॉइस मॅचिंग सुरू)", "हँडल": "मोबाईल नंबर ट्रॅकिंग", "रोल": "ऑडिओ रेकॉर्डर", "प्लॅटफॉर्म": "WhatsApp Audio", "कृती": "जमावाला भडकावणारी व्हॉइस नोट तयार केली.", "जोखीम": "🔴 अतिसंवेदनशील"}
        ]
    },
    {
        "id": "NND-ALERT-101",
        "time": "२५ मिनिटांपूर्वी",
        "type": "सोशल रील",
        "category": "आंदोलन / वाहतूक रोखणे",
        "source": "Instagram Reel",
        "source_icon": "📸",
        "author": "@nanded_news_express",
        "text": "हायवेच्या रखडलेल्या कामा विरोधात माहूरमध्ये रास्ता रोको आंदोलन आणि बाजारपेठ बंद चे आवाहन ! उद्या सकाळी १० वाजता तहसील कार्यालयासमोर जमा ! #news #nanded",
        "forward_velocity": 45,
        "total_forwards": 1850,
        "reaction_velocity": 90,
        "total_reactions": 3200,
        "is_communal": False,
        "is_red_alert": True,
        "threat_score": 74,
        "risk_desc": "महामार्ग रोखणे व वाहतूक कोंडी निर्माण करणे.",
        "angry_percent": 48,
        "predicted_spot": "तहसील कार्यालय परिसर, माहूर",
        "predicted_time": "उद्या सकाळी १०:०० AM",
        "fact_check_status": "✅ मूळ स्थानिक व्हिडिओ (सत्यता पडताळणी झाली)",
        "network_threat": "👥 सेंद्रिय प्रसार (Organic Local Sharing)",
        "audio_transcription": None,
        "field_status": "🟢 पोलीस बंदोबस्त नियोजन पूर्ण",
        "sample_comments": ["सर्व गाड्या अडवा तेव्हाच प्रश्न सुटेल.", "शांततेने आंदोलन करा."],
        "key_figures": [
            {"नाव": "अमोल देशमुख", "हँडल": "@amol_nanded_youth", "रोल": "रील निर्माता", "प्लॅटफॉर्म": "Instagram", "कृती": "रास्ता रोकोची तारीख जाहीर केली.", "जोखीम": "🟡 मध्यम"}
        ]
    }
]

# --- ४. साइडबार ---
with st.sidebar:
    st.markdown("### 🚨 सायबर सेल नांदेड")
    st.caption("इंटेलिजन्स व पूर्वसूचना कमांड सेंटर")
    st.markdown("---")
    
    view_mode = st.radio(
        "कार्यकारी विभाग:",
        ["📡 लाइव्ह रडार (Live Operations)", "🗄️ ऐतिहासिक डेटाबेस (Intelligence Archive)"]
    )
    st.markdown("---")
    siren_active = st.toggle("🔔 ऑटो-सायरन मोड (Audio Siren)", value=True)
    st.checkbox("स्वयंचलित रिफ्रेश (३० सेकंद)", value=True)
    st.info("२४×७ ऑडिओ ट्रान्सक्रिप्टर, एआय प्रेडिक्टर व फील्ड युनिट्स सक्रिय")

# --- ५. मुख्य विभाग १: लाइव्ह रडार ---
if view_mode == "📡 लाइव्ह रडार (Live Operations)":
    st.markdown("## 🚨 नांदेड जिल्हा : २४×७ सोशल मीडिया व न्यूज पूर्वसूचना कमांड सेंटर")
    st.caption("ऑडिओ ट्रान्सक्रिप्शन, फील्ड पेट्रोलिंग ट्रॅकर, एआय जमाव प्रेडिक्टर व डिजिटल पुरावा यंत्रणा")

    # सायरन वाजवणे
    communal_count = sum(1 for x in LIVE_INTEL_DATA if x["is_communal"])
    red_count = sum(1 for x in LIVE_INTEL_DATA if x["is_red_alert"])
    if siren_active and (communal_count > 0 or red_count > 0):
        st.components.v1.html(
            """
            <script>
            try {
                var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                function playBeep() {
                    var osc = audioCtx.createOscillator();
                    var gain = audioCtx.createGain();
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(900, audioCtx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(350, audioCtx.currentTime + 0.35);
                    gain.gain.setValueAtTime(0.18, audioCtx.currentTime);
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

    # १. सारांश फिल्टर्स
    st.markdown("##### ⚡ नियंत्रण कक्ष सारांश (क्लिक करून यादी फिल्टर करा):")
    b1, b2, b3, b4 = st.columns(4)
    with b1:
        if st.button(f"📋 सर्व नोंदी ({len(LIVE_INTEL_DATA)})", use_container_width=True):
            st.session_state["filter_type"] = "all"
    with b2:
        if st.button(f"🔥 सामाजिक तेढ ({communal_count})", use_container_width=True):
            st.session_state["filter_type"] = "communal"
    with b3:
        if st.button(f"🚨 रेड अलर्ट्स ({red_count})", use_container_width=True):
            st.session_state["filter_type"] = "red"
    with b4:
        max_speed = max(x["forward_velocity"] for x in LIVE_INTEL_DATA)
        st.metric("⚡ सर्वाधिक फॉरवर्ड गती", f"{max_speed} / मिनिट", "अतिजलद प्रसार 🚀")

    st.markdown("---")

    # २. फॉरवर्ड गती व थ्रेट स्कोअर तुलना तक्ता
    st.markdown("### 📤 सोशल मीडिया फॉरवर्ड गती व वैज्ञानिक थ्रेट स्कोअर (Live Intelligence Grid)")
    table_rows = []
    for item in LIVE_INTEL_DATA:
        _, _, stn_info = scan_text_intel(item["text"])
        status_tag = "🔥 सामाजिक तेढ" if item["is_communal"] else ("🔴 रेड अलर्ट" if item["is_red_alert"] else "🟡 सर्वसाधारण")
        table_rows.append({
            "आयडी": item["id"],
            "माध्यम": item["type"],
            "पोलीस ठाणे": stn_info["ps"],
            "फॉरवर्ड गती": f"⚡ {item['forward_velocity']} / मिनिट",
            "थ्रेट स्कोअर (०-१००)": f"🎯 {item['threat_score']}/१००",
            "फील्ड स्थिती": item["field_status"],
            "धोका पातळी": status_tag
        })
    st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ३. अलर्ट कार्ड्स
    filter_val = st.session_state.get("filter_type", "all")
    if filter_val == "communal":
        display_posts = [p for p in LIVE_INTEL_DATA if p["is_communal"]]
    elif filter_val == "red":
        display_posts = [p for p in LIVE_INTEL_DATA if p["is_red_alert"]]
    else:
        display_posts = LIVE_INTEL_DATA

    for post in display_posts:
        law_words, com_words, stn_info = scan_text_intel(post["text"])
        card_class = "alert-card-communal" if post["is_communal"] else ("alert-card-red" if post["is_red_alert"] else "alert-card-normal")
        badge_html = "<span class='badge-communal'>🔥 सामाजिक/धार्मिक तेढ अलर्ट</span>" if post["is_communal"] else "<span class='badge-red'>🚨 अतिसंवेदनशील रेड अलर्ट</span>"

        st.markdown(f"""
        <div class="{card_class}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div>{badge_html} <span style="margin-left:10px; font-weight:bold; color:#94a3b8;">{post['id']}</span> <span style="color:#f87171; margin-left:10px;">[{post['category']}]</span></div>
                <div style="color:#cbd5e1; font-size:14px;"><strong>माध्यम:</strong> {post['type']} | <strong>स्त्रोत:</strong> {post['source_icon']} {post['source']} ({post['time']})</div>
            </div>
            <h3 style="margin-top:0; color:#ffffff;">{post['text']}</h3>
        </div>
        """, unsafe_allow_html=True)

        # ऑडिओ ट्रान्सक्रिप्शन विभाग (जर ऑडिओ क्लिप असेल तर)
        if post["audio_transcription"]:
            st.warning(f"🎙️ **ऑटोमॅटिक मराठी स्पीच-टू-टेक्स्ट ट्रान्सक्रिप्शन:**\n\n{post['audio_transcription']}")

        # एआय प्रेडिक्टर व फील्ड स्थिती
        st.markdown(f"""
        <div class="intel-box">
            <div style="display:flex; justify-content:space-between;">
                <div>📍 <strong>एआय जमाव अंदाज:</strong> <code>{post['predicted_spot']}</code></div>
                <div>⏰ <strong>अपेक्षित वेळ:</strong> <code>{post['predicted_time']}</code></div>
                <div>🎯 <strong>थ्रेट स्कोअर:</strong> <code>{post['threat_score']}/100</code></div>
            </div>
            <div style="margin-top:8px;">
                🔍 <strong>फॅक्ट-चेक स्थिती:</strong> <code>{post['fact_check_status']}</code> | 
                🤖 <strong>प्रसार पद्धत:</strong> <code>{post['network_threat']}</code>
            </div>
        </div>
        <div class="field-box">
            🚔 <strong>फील्ड युनिट व पेट्रोलिंग स्थिती:</strong> <code>{post['field_status']}</code> | 
            🎯 <strong>नियुक्त बीट वाहन:</strong> <code>{stn_info['beat_unit']}</code>
        </div>
        """, unsafe_allow_html=True)

        # ठाणे व वायरलेस निर्देश
        c_i1, c_i2 = st.columns(2)
        with c_i1:
            st.info(f"📍 **अचूक पोलीस ठाणे हद्द:** `{stn_info['ps']}`\n\n⚠️ **संभाव्य धोका:** {post['risk_desc']}")
        with c_i2:
            st.error(f"📻 **वायरलेस फ्लॅश संदेश:** `{stn_info['wireless']} ला तात्काळ सतर्क करावे.`\n\n📊 **प्रसार गती:** `{post['forward_velocity']} फॉरवर्ड्स/मि.` (एकूण: `{post['total_forwards']:,}`)")

        # पडद्यामागील प्रमुख सूत्रधार
        with st.expander("👤 पडद्यामागील प्रमुख सूत्रधार व आयोजक (Key Mobilizers)", expanded=post["is_communal"]):
            if post["key_figures"]:
                st.table(pd.DataFrame(post["key_figures"]))

        # जनभावना व कॉमेंट्स
        with st.expander("💬 जनभावना विश्लेषण व थेट प्रतिक्रिया (Public Sentiment)", expanded=False):
            st.write(f"**आक्रमक/संतापजनक प्रतिक्रिया प्रमाण:** {post['angry_percent']}%")
            st.progress(post["angry_percent"] / 100)
            for comment in post["sample_comments"]:
                st.markdown(f"- 🗣️ *\"{comment}\"*")

        # ॲक्शन बटणे
        act_col1, act_col2, act_col3 = st.columns(3)
        with act_col1:
            if st.button("📢 अधिकृत पोलीस खंडन तयार करा", key=f"btn_fc_{post['id']}", use_container_width=True):
                st.info(f"""
                **📌 नांदेड जिल्हा पोलीस अधिकृत प्रसिद्धीपत्रक:**  
                "सोशल मीडियावर {post['author']} द्वारे फिरत असलेला मेसेज/व्हिडिओ दिशाभूल करणारा व शांतता भंग करणारा आहे. नागरिकांनी अफवांवर विश्वास ठेवू नये. कायदा हातात घेणाऱ्यांवर कठोर कायदेशीर कारवाई करण्यात येईल."
                """)

        with act_col2:
            if st.button("⚖️ डिजिटल कोर्ट पुरावा (SHA-256) नोंदवा", key=f"btn_hash_{post['id']}", use_container_width=True):
                raw_intel = f"{post['id']}-{post['text']}-{post['author']}-{datetime.now()}"
                hash_signature = hashlib.sha256(raw_intel.encode()).hexdigest()
                st.success(f"""
                **डिजिटल फॉरेन्सिक पुरावा सुरक्षित झाला!**  
                - पुरावा हॅश: `{hash_signature}`  
                - टाईमस्टॅम्प: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`
                """)

        with act_col3:
            if st.button(f"🚔 {stn_info['beat_unit']} ला थेट अलर्ट पाठवा", key=f"btn_w_{post['id']}", use_container_width=True):
                st.success(f"{stn_info['ps']} आणि {stn_info['beat_unit']} ला GPS लोकेशनसह अलर्ट पाठवला!")

        st.markdown("<hr style='border:1px solid #1e293b;'>", unsafe_allow_html=True)

# --- ६. मुख्य विभाग २: ऐतिहासिक डेटाबेस ---
elif view_mode == "🗄️ ऐतिहासिक डेटाबेस (Intelligence Archive)":
    st.subheader("🗄️ ऐतिहासिक डेटाबेस व इंटेलिजन्स ट्रेंड्स")
    st.caption("मागील ऑडिओ क्लिप्स, घटना, फॉरवर्ड गती आणि फील्ड ॲक्शन रेकॉर्ड शोधा.")

    s1, s2 = st.columns([3, 1])
    with s1:
        search_txt = st.text_input("🔍 शब्द, तारीख, चॅनेल किंवा पोलीस ठाण्यावरून शोधा:")
    with s2:
        filter_status = st.selectbox("श्रेणी निवडा:", ["सर्व", "सामाजिक तेढ", "ऑडिओ क्लिप", "रेड अलर्ट"])

    archive_data = [
        {"तारीख व वेळ": "02-10-2026 01:20", "माध्यम": "वेब न्यूज पोर्टल", "पोलीस ठाणे": "नांदेड नियंत्रण कक्ष", "घटना": "धार्मिक झेंडा संशयावरून तणाव", "फॉरवर्ड गती": "125/मि.", "थ्रेट स्कोअर": "94/100", "कारवाई": "डायल ११२ तैनात"},
        {"तारीख व वेळ": "02-10-2026 01:05", "माध्यम": "WhatsApp ऑडिओ", "पोलीस ठाणे": "किनवट पोलीस ठाणे", "घटना": "जंगलातील तोडफोड ऑडिओ", "फॉरवर्ड गती": "78/मि.", "थ्रेट स्कोअर": "86/100", "कारवाई": "बीट मार्शल तपासणी"},
        {"तारीख व वेळ": "01-10-2026 18:55", "माध्यम": "Instagram Reel", "पोलीस ठाणे": "माहूर पोलीस ठाणे", "घटना": "रास्ता रोको आंदोलन", "फॉरवर्ड गती": "45/मि.", "थ्रेट स्कोअर": "74/100", "कारवाई": "बंदोबस्त तैनात"}[cite: 1]
    ]

    df_arch = pd.DataFrame(archive_data)
    st.dataframe(df_arch, use_container_width=True, hide_index=True)

    st.download_button(
        label="📥 इंटेलिजन्स रेकॉर्ड एक्सेल/CSV मध्ये डाउनलोड करा",
        data=df_arch.to_csv(index=False).encode('utf-8-sig'),
        file_name="Nanded_Cyber_Police_Intelligence_Archive.csv",
        mime="text/csv"
    )