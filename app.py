import streamlit as st
import pandas as pd
from datetime import datetime

# --- १. पेज कॉन्फिगरेशन व ॲडव्हान्स डिजिटल सायबर थीम ---
st.set_page_config(
    page_title="सायबर सेल नांदेड - २४×७ सोशल मीडिया इंटेलिजन्स कमांड सेंटर",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# हाय-काँट्रास्ट, डिजिटल आणि डोळ्यांना स्पष्ट दिसणारी CSS रचना
st.markdown("""
<style>
    /* मुख्य बॅकग्राउंड */
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* मेट्रिक्स कार्ड्स */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 14px 18px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-weight: 600;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f0f6fc !important;
        font-size: 26px !important;
    }

    /* अलर्ट कार्ड्स रचना */
    .intel-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.4);
    }
    .intel-card-red {
        border-left: 6px solid #f85149 !important;
        background: linear-gradient(90deg, rgba(248, 81, 73, 0.08) 0%, #161b22 100%);
    }
    .intel-card-yellow {
        border-left: 6px solid #d29922 !important;
        background: linear-gradient(90deg, rgba(210, 153, 34, 0.08) 0%, #161b22 100%);
    }

    /* बॅजेस */
    .badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.3px;
        display: inline-block;
    }
    .badge-communal { background-color: #b62324; color: #ffffff; }
    .badge-speech { background-color: #8957e5; color: #ffffff; }
    .badge-protest { background-color: #d29922; color: #0d1117; }
    .badge-red { background-color: #f85149; color: #ffffff; }

    /* कीवर्ड टॅग्स */
    .kw-tag {
        background-color: #21262d;
        color: #58a6ff;
        border: 1px solid #388bfd33;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        margin-right: 6px;
        font-weight: 600;
    }

    /* डेटा बॉक्स */
    .detail-container {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 12px;
    }
    
    /* लिंक स्टाइल */
    .source-link {
        color: #58a6ff !important;
        text-decoration: underline !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- २. नांदेड जिल्हा पोलीस ठाणी व हद्द मॅपिंग ---
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
    "नांदेड शहर": {"ps": "नांदेड नियंत्रण कक्ष (मुख्यालय)", "wireless": "वजिराबाद / इतवारा / भाग्यनगर / शिवाजीनगर"}
}

# संवेदनशील कीवर्ड्स (चारही मुख्य श्रेणी)
KEYWORDS_DB = {
    "सामाजिक_राजकीय_तेढ": ["दंगल", "जातीय तेढ", "धार्मिक भावना", "पुतळ्याची विटंबना", "झेंडा काढला", "धर्माचा अपमान", "जातीचा अपमान", "गटबाजी", "धार्मिक तेढ", "राजकीय राडा"],
    "भडकाऊ_भाषण_लिखाण": ["धडा शिकवू", "उखाडून टाकू", "चुनौती", "धमकी", "बहिष्कार टाका", "रक्त सांडू", "बदला घेऊ", "उचकवणारे भाषण", "खुला इशारा"],
    "आंदोलन_मोर्चा_बंद": ["रास्ता रोको", "चक्काजाम", "मोर्चा", "धरणे", "बंद", "उपोषण", "तोडफोड", "दगडफेक", "घेराव", "आत्मदहन", "बाजारपेठ बंद", "हायवे रोखणे", "भांडण"]
}

def analyze_incident(text):
    matched_kw = []
    cat_detected = "जिल्हा कायदा-सुव्यवस्था घडामोड"
    
    for cat, kws in KEYWORDS_DB.items():
        for kw in kws:
            if kw in text:
                matched_kw.append(kw)
                if cat == "सामाजिक_राजकीय_तेढ": cat_detected = "सामाजिक व राजकीय तेढ"
                elif cat == "भडकाऊ_भाषण_लिखाण": cat_detected = "भडकाऊ भाषण व लिखाण"
                elif cat == "आंदोलन_मोर्चा_बंद": cat_detected = "आंदोलन / मोर्चा / रास्ता रोको"

    stn_info = POLICE_JURISDICTION_MAP["नांदेड शहर"]
    for place, info in POLICE_JURISDICTION_MAP.items():
        if place in text:
            stn_info = info
            break
            
    return list(set(matched_kw)), cat_detected, stn_info

# --- ३. रिअल-टाइम इंटेलिजन्स डेटाबेस ---
LIVE_INTEL_DATA = [
    {
        "id": "NND-INTEL-01",
        "time": "६ मिनिटांपूर्वी",
        "category": "सामाजिक व राजकीय तेढ",
        "source": "Instagram Reel & Story",
        "source_icon": "📸",
        "source_url": "https://instagram.com/reel/C8xNandedLive01",
        "author": "@nanded_news_bulletin",
        "text": "देगलूर नाका भागात धार्मिक झेंडा काढल्याच्या संशयावरून दोन गटांत जोरदार घोषणाबाजी; जातीय तेढ निर्माण करणारा व्हिडिओ व्हायरल, तरुणांना एकत्र येण्याचे आवाहन.",
        "forward_velocity": 135,
        "total_forwards": 3850,
        "active_amplifiers": 420,  # प्रसार करणारे लोक (Count)
        "total_reactions": 7200,
        "reaction_velocity": 280,
        "is_red_alert": True,
        "threat_score": 96,
        "sentiment_stats": {
            "angry": 78,
            "provocative": 14,
            "neutral_peace": 8
        },
        "sample_comments": [
            "सर्व भावांनी रात्री ८:३० वाजता चौकात जमायचे आहे, शांत बसायचे नाही!",
            "हा जुना व्हिडिओ टाकून शहरात दंगल घडवण्याचा डाव आहे, पोलिसांनी तात्काळ अटक करावी.",
            "प्रशासनाने लगेच इंटरनेट बंद करावे किंवा कठोर पावले उचलावीत.",
            "शांतता राखा, अफवांवर विश्वास ठेवून आपलेच नुकसान करू नका."
        ],
        "key_figures": [
            {"नाव": "सचिन कदम (@sachin_yuva)", "रोल": "मूळ व्हिडिओ पोस्टकर्ता (Originator)", "हँडल / संपर्क": "X: @sachin_yuva | Insta: 45K फॉलोअर्स", "कृती": "जुना व्हिडिओ एडिट करून 'नांदेड आज' असा खोटा मजकूर लिहून व्हायरल केला.", "जोखीम पातळी": "🔴 अतिसंवेदनशील"},
            {"नाव": "सय्यद आरिफ (मो. ९९२१०XXXXX)", "रोल": "मुख्य व्हॉट्सअ‍ॅप मोबिलायझर", "हँडल / संपर्क": "ॲडमिन: नांदेड युथ वॉरियर्स ग्रुप", "कृती": "चौकात गर्दी जमवण्यासाठी ३ मिनिटांची भडकावू व्हॉइस नोट पाठवली.", "जोखीम पातळी": "🔴 अतिसंवेदनशील"},
            {"नाव": "राहुल वानखेडे (@rahul_vlogs)", "रोल": "डिजिटल अँप्लिफायर", "हँडल / संपर्क": "YouTube: २०K सब्सक्राइबर्स", "कृती": "सत्यता न तपासता लाईव्ह स्ट्रीमिंग सुरू करून तणाव वाढवला.", "जोखीम पातळी": "🟡 मध्यम"},
            {"नाव": "अज्ञात ॲडमिन (मो. ९८२३४XXXXX)", "रोल": "फॉरवर्ड स्प्रेडर", "हँडल / संपर्क": "देगलूर नाका बॉईज ग्रुप", "कृती": "एकाच वेळी २५ स्थानिक ग्रुप्समध्ये मेसेज फॉरवर्ड केला.", "जोखीम पातळी": "🔴 अतिसंवेदनशील"}
        ]
    },
    {
        "id": "NND-INTEL-02",
        "time": "१८ मिनिटांपूर्वी",
        "category": "भडकाऊ भाषण व लिखाण",
        "source": "Facebook Public Video & X",
        "source_icon": "🌐",
        "source_url": "https://facebook.com/watch/?v=9823471029",
        "author": "मराठवाडा क्रांती मोर्चा (पेज)",
        "text": "लोहा येथे आयोजित मेळाव्यात नेत्याचे भडकाऊ भाषण; 'आमच्या मागण्या मान्य न झाल्यास शासकीय कार्यालये पेटवून देऊ आणि रस्ता रोको करू' अशी उघड धमकी.",
        "forward_velocity": 82,
        "total_forwards": 2100,
        "active_amplifiers": 215,
        "total_reactions": 4300,
        "reaction_velocity": 140,
        "is_red_alert": True,
        "threat_score": 88,
        "sentiment_stats": {
            "angry": 62,
            "provocative": 28,
            "neutral_peace": 10
        },
        "sample_comments": [
            "आता माघार नाही, थेट तहसीलदारांच्या गाडीला घेराव घालणार.",
            "नेत्यांनी अशी बेताल वक्तव्ये करून तरुणांची माथी भडकवू नयेत.",
            "उद्या लोहा बंद १००% यशस्वी होणार."
        ],
        "key_figures": [
            {"नाव": "ॲड. विलास सूर्यवंशी", "रोल": "भाषणकर्ता / प्रमुख आयोजक", "हँडल / संपर्क": "मो. ९४२००XXXXX | FB पेज", "कृती": "माईकवरून थेट कायदा हातात घेण्याची चिथावणी दिली.", "जोखीम पातळी": "🔴 अतिसंवेदनशील"},
            {"नाव": "दिगंबर पाटील", "रोल": "सोशल मीडिया मॅनेजर", "हँडल / संपर्क": "@patil_loha_official", "कृती": "भाषणातील सर्वात भडकावू ३० सेकंदांची क्लिप काढून रील्सवर व्हायरल केली.", "जोखीम पातळी": "🔴 अतिसंवेदनशील"},
            {"नाव": "अमित जाधव", "रोल": "स्थानिक कार्यकर्ता", "हँडल / संपर्क": "लोहा तालुका व्हॉट्सअ‍ॅप नेटवर्क", "कृती": "गावोगावच्या तरुणांना मोर्चासाठी वाहने घेऊन येण्याचे मेसेज केले.", "जोखीम पातळी": "🟡 मध्यम"}
        ]
    },
    {
        "id": "NND-INTEL-03",
        "time": "३५ मिनिटांपूर्वी",
        "category": "आंदोलन / मोर्चा / रास्ता रोको",
        "source": "स्थानिक वेब न्यूज व YouTube",
        "source_icon": "📺",
        "source_url": "https://nandednews24.in/article/mahur-highway-block",
        "author": "नांदेड एक्सप्रेस डिजिटल",
        "text": "माहूर-नांदेड हायवेच्या रखडलेल्या कामा विरोधात उद्या सकाळी ९ वाजता चक्काजाम व उपोषण; एसटी बसेस रोखण्याचा इशारा.",
        "forward_velocity": 46,
        "total_forwards": 1420,
        "active_amplifiers": 98,
        "total_reactions": 2900,
        "reaction_velocity": 75,
        "is_red_alert": False,
        "threat_score": 72,
        "sentiment_stats": {
            "angry": 45,
            "provocative": 15,
            "neutral_peace": 40
        },
        "sample_comments": [
            "हायवेची अवस्था खूप वाईट आहे, आंदोलन योग्यच आहे.",
            "रुग्णवाहिका आणि प्रवाशांना अडवू नका, शांततेत आंदोलन करा.",
            "माहूर बस स्टँडवर सकाळीच पोलीस तैनात करावेत."
        ],
        "key_figures": [
            {"नाव": "अमोल देशमुख", "रोल": "आंदोलन निमंत्रक", "हँडल / संपर्क": "@amol_mahur | मो. ९७६३०XXXXX", "कृती": "चक्काजाम आंदोलनाचे अधिकृत पत्रक सोशल मीडियावर प्रसिद्ध केले.", "जोखीम पातळी": "🟡 मध्यम"},
            {"नाव": "संदीप पवार", "रोल": "प्रचारक (Amplifier)", "हँडल / संपर्क": "Instagram: @mahur_youth_club", "कृती": "हायवेवरील खड्ड्यांचे जुने फोटो टाकून आवाहन केले.", "जोखीम पातळी": "🟢 सामान्य"}
        ]
    }
]

# सेशन स्टेट फिल्टर
if "active_view" not in st.session_state:
    st.session_state["active_view"] = "all"

# --- ४. साइडबार ---
with st.sidebar:
    st.markdown("## 🛡️ सायबर सेल नांदेड")
    st.caption("जिल्हा कायदा व सुव्यवस्था पूर्वसूचना नियंत्रण कक्ष")
    st.markdown("---")
    
    nav_mode = st.radio(
        "कमांड मोड निवडा:",
        ["📡 लाइव्ह रडार (Live Intelligence)", "🗄️ ऐतिहासिक डेटाबेस (Intelligence Archive)"]
    )
    st.markdown("---")
    siren_on = st.toggle("🔔 ऑटो-सायरन मोड (Audio Siren)", value=True)
    st.checkbox("स्वयंचलित रिफ्रेश (३० सेकंद)", value=True)
    st.caption(f"सिस्टीम वेळ: {datetime.now().strftime('%d-%m-%Y | %H:%M:%S')}")

# --- ५. मुख्य स्क्रीन: लाइव्ह रडार ---
if nav_mode == "📡 लाइव्ह रडार (Live Intelligence)":
    
    st.markdown("## 🚨 नांदेड जिल्हा : २४×७ सोशल मीडिया व घडामोडी पूर्वसूचना केंद्र")
    st.caption("राजकीय-सामाजिक तेढ, भडकाऊ भाषणे, आंदोलने, मोर्चे व कायदा-सुव्यवस्था बाधक संदेशांचे स्वयंचलित पडताळणी तंत्र")

    # सायरन वाजवणे (रेड अलर्ट असल्यास)
    red_items = [x for x in LIVE_INTEL_DATA if x["is_red_alert"]]
    if siren_on and len(red_items) > 0:
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
                    gain.gain.setValueAtTime(0.16, audioCtx.currentTime);
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

    # १. त्वरित मेट्रिक्स व फिल्टर्स
    st.markdown("##### 📌 परिस्थिती सारांश (तपशील पाहण्यासाठी बटनावर क्लिक करा):")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        if st.button(f"📋 एकूण संशयित नोंदी : {len(LIVE_INTEL_DATA)}", use_container_width=True):
            st.session_state["active_view"] = "all"
    with m2:
        if st.button(f"🚨 अतिसंवेदनशील रेड अलर्ट्स : {len(red_items)}", use_container_width=True):
            st.session_state["active_view"] = "red"
    with m3:
        max_vel = max(x["forward_velocity"] for x in LIVE_INTEL_DATA)
        st.metric("⚡ सर्वाधिक प्रसार वेग", f"{max_vel} / मिनिट", "अतिजलद व्हायरल 🚀")
    with m4:
        total_amp = sum(x["active_amplifiers"] for x in LIVE_INTEL_DATA)
        st.metric("👥 एकूण सक्रिय प्रसारक", f"{total_amp:,} युजर्स", "निगराणीखाली")

    st.markdown("---")

    # २. फॉरवर्ड गती व प्रसारक संख्या तुलना तक्ता
    st.markdown("### 📤 सोशल मीडिया फॉरवर्ड वेग, स्त्रोत व प्रसारक संख्या तक्ता")
    grid_rows = []
    for item in LIVE_INTEL_DATA:
        _, _, stn = analyze_incident(item["text"])
        grid_rows.append({
            "आयडी": item["id"],
            "घडामोडीचा प्रकार": item["category"],
            "मूळ स्त्रोत": f"{item['source_icon']} {item['source']}",
            "पोलीस ठाणे": stn["ps"],
            "फॉरवर्ड वेग": f"⚡ {item['forward_velocity']} / मिनिट",
            "एकूण शेअर्स": f"{item['total_forwards']:,}",
            "प्रसार करणारे लोक": f"👥 {item['active_amplifiers']} सक्रिय",
            "थ्रेट स्कोअर": f"🎯 {item['threat_score']}/१००",
            "स्थिती": "🔴 रेड अलर्ट" if item["is_red_alert"] else "🟡 सर्वसाधारण"
        })
    st.dataframe(pd.DataFrame(grid_rows), use_container_width=True, hide_index=True)

    st.markdown("---")

    # ३. अलर्ट कार्ड्स (फिल्टरनुसार)
    if st.session_state["active_view"] == "red":
        st.markdown("### 🚨 फक्त अतिसंवेदनशील रेड अलर्ट्स (Immediate Action Required)")
        filtered_posts = red_items
    else:
        st.markdown("### 📋 सर्व सक्रिय पूर्वसूचना नोंदी")
        filtered_posts = LIVE_INTEL_DATA

    for post in filtered_posts:
        kw_list, category_name, stn_info = analyze_incident(post["text"])
        
        # कार्ड स्टाइल
        card_class = "intel-card-red" if post["is_red_alert"] else "intel-card-yellow"
        
        if "तेढ" in post["category"]:
            badge_html = "<span class='badge badge-communal'>🔥 राजकीय व सामाजिक तेढ</span>"
        elif "भाषण" in post["category"]:
            badge_html = "<span class='badge badge-speech'>⚠️ भडकाऊ भाषण व लिखाण</span>"
        else:
            badge_html = "<span class='badge badge-protest'>📢 आंदोलन / मोर्चा / रास्ता रोको</span>"

        # कार्डचा मुख्य भाग
        st.markdown(f"""
        <div class="intel-card {card_class}">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>
                    {badge_html} 
                    <span style="margin-left:10px; font-weight:700; color:#58a6ff;">{post['id']}</span>
                    <span style="margin-left:10px; color:#8b949e; font-size:13px;">({post['time']})</span>
                </div>
                <div style="font-size:14px; color:#c9d1d9;">
                    <strong>स्त्रोत:</strong> {post['source_icon']} {post['source']} | 
                    <strong>हँडल/पेज:</strong> {post['author']}
                </div>
            </div>
            <h3 style="margin-top:0; color:#f0f6fc; line-height:1.5;">{post['text']}</h3>
            <div style="margin-top:8px;">
                🔗 <strong>थोडक्यात स्त्रोत लिंक:</strong> <a href="{post['source_url']}" target="_blank" class="source-link">{post['source_url']}</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # डिटेक्ट झालेले संवेदनशील शब्द
        if kw_list:
            tags_html = " ".join([f"<span class='kw-tag'>🚩 {w}</span>" for w in kw_list])
            st.markdown(f"**डिटेक्ट झालेले संवेदनशील शब्द:** {tags_html}", unsafe_allow_html=True)

        # ठाणे, वायरलेस आणि प्रसार मेट्रिक्स
        c_info1, c_info2 = st.columns(2)
        with c_info1:
            st.markdown(f"""
            <div class="detail-container">
                📍 <strong>अचूक पोलीस ठाणे हद्द:</strong> <code>{stn_info['ps']}</code><br>
                📻 <strong>वायरलेस निर्देश:</strong> <code>{stn_info['wireless']} ला तात्काळ सतर्क करावे.</code>
            </div>
            """, unsafe_allow_html=True)
            
        with c_info2:
            st.markdown(f"""
            <div class="detail-container">
                📤 <strong>प्रसार वेग:</strong> <code>{post['forward_velocity']} फॉरवर्ड्स/मि.</code> (एकूण शेअर्स: <strong>{post['total_forwards']:,}</strong>)<br>
                👥 <strong>प्रसार करणारे लोक (Amplifiers):</strong> <code style="color:#f85149;">{post['active_amplifiers']} सक्रिय युजर्स/हँडल्स</code>
            </div>
            """, unsafe_allow_html=True)

        # ४. जनभावना व प्रतिक्रियांचे सखोल विश्लेषण (Deep Sentiment Matrix)
        with st.expander("📊 जनभावना व थेट प्रतिक्रियांचे सखोल विश्लेषण (Public Sentiment Breakdown)", expanded=post["is_red_alert"]):
            st.markdown("##### 👥 लोकांच्या प्रतिक्रियांचा कल (Audience Reaction Mood):")
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("😡 संताप / आक्रमक विरोध", f"{post['sentiment_stats']['angry']}%")
            sc2.metric("⚡ भडकावू / एकत्र येणारे", f"{post['sentiment_stats']['provocative']}%")
            sc3.metric("🕊️ शांतता / तटस्थ आवाहन", f"{post['sentiment_stats']['neutral_peace']}%")
            
            st.caption("प्रतिक्रिया विश्लेषण प्रोग्रेस बार (लाल = संताप, पिवळा = चिथावणी, हिरवा = शांतता):")
            st.progress(post['sentiment_stats']['angry'] / 100)

            st.markdown("##### 💬 सोशल मीडियावर सर्वात जास्त लाईक झालेल्या व व्हायरल कॉमेंट्स:")
            for comment in post["sample_comments"]:
                st.markdown(f"- 🗣️️ *\"{comment}\"*")

        # ५. पडद्यामागील प्रमुख सूत्रधार व प्रसारकांची सविस्तर यादी (Detailed Suspect Dossier)
        with st.expander("👤 पडद्यामागील प्रमुख सूत्रधार, आयोजक व प्रसारक (Key Suspects & Amplifiers Dossier)", expanded=True):
            st.caption("सायबर ट्रॅकिंगनुसार मूळ पोस्ट करणारे, मोबिलायझर्स आणि मेसेज वेगाने फॉरवर्ड करणाऱ्यांची पडताळणी यादी:")
            df_suspects = pd.DataFrame(post["key_figures"])
            st.dataframe(df_suspects, use_container_width=True, hide_index=True)

        st.markdown("<hr style='border:1px solid #30363d;'>", unsafe_allow_html=True)

# --- ६. मुख्य स्क्रीन: ऐतिहासिक डेटाबेस ---
elif nav_mode == "🗄️ ऐतिहासिक डेटाबेस (Intelligence Archive)":
    st.subheader("🗄️ ऐतिहासिक डेटाबेस व घडामोडी शोध")
    st.caption("मागील सर्व घडामोडी, भडकावू पोस्ट्स, आंदोलने आणि सूत्रधारांचा डिजिटल रेकॉर्ड.")

    s1, s2 = st.columns([3, 1])
    with s1:
        search_kw = st.text_input("🔍 शब्द, तारीख, व्यक्तीचे नाव किंवा पोलीस ठाण्यावरून शोधा:")
    with s2:
        cat_filter = st.selectbox("श्रेणी निवडा:", ["सर्व", "सामाजिक व राजकीय तेढ", "भडकाऊ भाषण व लिखाण", "आंदोलन / मोर्चा"])

    archive_data = [
        {"तारीख व वेळ": "02-10-2026 01:20", "प्रकार": "सामाजिक व राजकीय तेढ", "पोलीस ठाणे": "नांदेड नियंत्रण कक्ष", "स्त्रोत व लिंक": "Instagram Reel (bit.ly/3x8Nnd)", "फॉरवर्ड वेग": "135/मि.", "प्रसारक संख्या": "420", "प्रमुख सूत्रधार": "सचिन कदम, सय्यद आरिफ", "थ्रेट स्कोअर": "96/100"},
        {"तारीख व वेळ": "01-10-2026 23:45", "प्रकार": "भडकाऊ भाषण व लिखाण", "पोलीस ठाणे": "लोहा पोलीस ठाणे", "स्त्रोत व लिंक": "Facebook Video (fb.watch/982)", "फॉरवर्ड वेग": "82/मि.", "प्रसारक संख्या": "215", "प्रमुख सूत्रधार": "ॲड. विलास सूर्यवंशी", "थ्रेट स्कोअर": "88/100"},
        {"तारीख व वेळ": "01-10-2026 18:55", "प्रकार": "आंदोलन / मोर्चा", "पोलीस ठाणे": "माहूर पोलीस ठाणे", "स्त्रोत व लिंक": "स्थानिक वेब न्यूज (nanded24.in)", "फॉरवर्ड वेग": "46/मि.", "प्रसारक संख्या": "98", "प्रमुख सूत्रधार": "अमोल देशमुख", "थ्रेट स्कोअर": "72/100"}[cite: 1]
    ]

    df_archive = pd.DataFrame(archive_data)
    st.dataframe(df_archive, use_container_width=True, hide_index=True)

    st.download_button(
        label="📥 संपूर्ण इंटेलिजन्स रेकॉर्ड एक्सेल/CSV मध्ये डाउनलोड करा",
        data=df_archive.to_csv(index=False).encode('utf-8-sig'),
        file_name="Nanded_Police_Cyber_Intelligence_Archive.csv",
        mime="text/csv"
    )