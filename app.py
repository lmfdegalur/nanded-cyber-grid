import streamlit as st
import pandas as pd

# --- १. पेज कॉन्फिगरेशन ---
st.set_page_config(
    page_title="सायबर सेल नांदेड - पूर्वसूचना नियंत्रण कक्ष",
    page_icon="🚨",
    layout="wide"
)

# --- २. नांदेड जिल्हा पोलीस ठाणी व वायरलेस ऑटो-मॅपिंग ---
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
    "नांदेड": {"ps": "नांदेड नियंत्रण कक्ष (मुख्यालय)", "wireless": "वजिराबाद / इतवारा / भाग्यनगर"}
}

SENSITIVE_KEYWORDS = [
    "रास्ता रोको", "चक्काजाम", "आंदोलन", "मोर्चा", "धरणे", "बंद", 
    "तोडफोड", "दगडफेक", "राडा", "घेराव", "आत्मदहन", "तणाव", 
    "बाजारपेठ बंद", "हायवे रोखणे", "बहिष्कार"
]

def scan_post_details(text):
    """मजकुरावरून संवेदनशील शब्द आणि पोलीस ठाणे शोधणे"""
    flagged_words = [kw for kw in SENSITIVE_KEYWORDS if kw in text]
    for place, info in POLICE_JURISDICTION_MAP.items():
        if place in text:
            return flagged_words, info["ps"], info["wireless"]
    return flagged_words, "नांदेड नियंत्रण कक्ष", "वजिराबाद / इतवारा / भाग्यनगर"

# --- ३. रिअल-टाइम इंटेलिजन्स डेटाबेस ---
LIVE_INTEL_DATA = [
    {
        "id": "NND-091",
        "time": "१० मिनिटांपूर्वी",
        "source": "Instagram Reel",
        "source_icon": "📸",
        "author": "@nanded_news_express",
        "text": "हायवेच्या रखडलेल्या कामा विरोधात माहूरमध्ये रास्ता रोको आंदोलन आणि बाजारपेठ बंद चे आवाहन ! #news #nanded #viral",
        "forward_velocity": 85,
        "total_forwards": 1850,
        "reaction_velocity": 190,
        "total_reactions": 4200,
        "is_red_alert": True,
        "risk": "वाहतूक कोंडी, महामार्ग रोखणे व बाजारपेठ बंद पाडण्याचे नियोजन.",
        "sample_comments": [
            "सर्व गाड्या थांबवून रस्ता पूर्ण जाम करा तेव्हाच प्रशासन जागे होईल!",
            "उद्या सकाळी ९ वाजताच चौकात जमायचे आहे सर्वांनी.",
            "प्रवाशांचे हाल करू नका, शांततेत निवेदन द्या."
        ],
        "key_figures": [
            {"नाव / हँडल": "अमोल देशमुख (@amol_nanded_youth)", "भूमिका": "मूळ रील निर्माता (Originator)", "प्लॅटफॉर्म": "Instagram", "कृती": "रास्ता रोकोची वेळ व तारीख जाहीर केली.", "जोखीम": "🔴 उच्च"},
            {"नाव / हँडल": "राजेश पवार (मो. ९८२२०XXXXX)", "भूमिका": "व्हॉट्सअ‍ॅप ॲडमिन (Mobilizer)", "प्लॅटफॉर्म": "WhatsApp Group", "कृती": "ट्रॅक्टर आणण्याचे ऑडिओ मेसेज पाठवले.", "जोखीम": "🔴 उच्च"}
        ]
    },
    {
        "id": "NND-092",
        "time": "२५ मिनिटांपूर्वी",
        "source": "WhatsApp Forward",
        "source_icon": "💬",
        "author": "शेतकरी विकास मंच (ग्रुप)",
        "text": "लोहा बाजार समितीत सोयाबीन दरावरून उद्या सकाळी ११ वाजता ठिय्या मोर्चा व चक्काजाम इशारा.",
        "forward_velocity": 34,
        "total_forwards": 710,
        "reaction_velocity": 55,
        "total_reactions": 1200,
        "is_red_alert": True,
        "risk": "बाजार समिती कामकाज बंद पाडणे व ट्रॅक्टर रस्त्यावर उभे करणे.",
        "sample_comments": [
            "भाव मिळालाच पाहिजे, गेट बंद करून टाका.",
            "पोलीस बंदोबस्त येण्याआधीच गर्दी गोळा करा."
        ],
        "key_figures": [
            {"नाव / हँडल": "गजानन कदम (मो. ९४२३०XXXXX)", "भूमिका": "मुख्य आयोजक (Leader)", "प्लॅटफॉर्म": "WhatsApp", "कृती": "शेतकऱ्यांना जमा होण्याचे आवाहन केले.", "जोखीम": "🔴 उच्च"}
        ]
    },
    {
        "id": "NND-093",
        "time": "४५ मिनिटांपूर्वी",
        "source": "Telegram Broadcast",
        "source_icon": "📢",
        "author": "मराठवाडा व्हॉइस",
        "text": "किनवट परिसरातील जंगलात संशयित हालचाली बाबत व्हायरल ऑडिओ क्लिप फिरत आहे.",
        "forward_velocity": 8,
        "total_forwards": 190,
        "reaction_velocity": 12,
        "total_reactions": 310,
        "is_red_alert": False,
        "risk": "अफवा पसरवणे व नागरिकांमध्ये भीतीचे वातावरण.",
        "sample_comments": [
            "ही क्लिप जुनी आहे का खरी आहे?",
            "सायबर सेलने याची चौकशी करावी."
        ],
        "key_figures": [
            {"नाव / हँडल": "@kinwat_updates_channel", "भूमिका": "माहिती प्रसारक (Broadcaster)", "प्लॅटफॉर्म": "Telegram", "कृती": "सत्यता न तपासता ऑडिओ फॉरवर्ड केला.", "जोखीम": "🟡 मध्यम"}
        ]
    },
    {
        "id": "NND-094",
        "time": "१ तासापूर्वी",
        "source": "Facebook Public Post",
        "source_icon": "🌐",
        "author": "नांदेड युवा मंच",
        "text": "देगलूर नाका परिसरात तरुणांच्या दोन गटात वाद; नागरिकांनी शांतता बाळगावी.",
        "forward_velocity": 12,
        "total_forwards": 320,
        "reaction_velocity": 24,
        "total_reactions": 450,
        "is_red_alert": False,
        "risk": "नागरी भागात अफवा व किरकोळ तणाव निर्माण होण्याची शक्यता.",
        "sample_comments": [
            "अफवांवर विश्वास ठेवू नका, पोलीस घटनास्थळी आहेत.",
            "शांतता राखा."
        ],
        "key_figures": []
    }
]

# --- ४. सेशन स्टेट (क्लिक फिल्टर्स) ---
if "view_filter" not in st.session_state:
    st.session_state["view_filter"] = "all"

# --- ५. डावीकडील साइडबार ---
with st.sidebar:
    st.markdown("## 🚨 सायबर सेल नांदेड")
    st.caption("स्वयंचलित सोशल मीडिया पूर्वसूचना कमांड सेंटर")
    st.markdown("---")
    
    menu_selection = st.radio(
        "कार्यकारी विभाग:",
        ["📡 लाइव्ह रडार (Live Radar)", "🗄️ ऐतिहासिक डेटाबेस (Historical Database)"]
    )
    
    st.markdown("---")
    siren_mode = st.toggle("🔔 सायरन मोड (ऑडिओ पूर्वसूचना)", value=True)
    if siren_mode:
        st.success("सायरन सक्रिय: रेड अलर्ट आल्यास बीप वाजेल.")
    else:
        st.warning("सायरन म्यूट मोडवर आहे.")
        
    st.checkbox("स्वयंचलित रिफ्रेश (३० सेकंद)", value=True)

# --- ६. विभाग १: लाइव्ह रडार ---
if menu_selection == "📡 लाइव्ह रडार (Live Radar)":
    st.subheader("🚨 नांदेड जिल्हा : २४×७ स्वयंचलित सोशल मीडिया पूर्वसूचना कमांड सेंटर")
    st.caption("WhatsApp, Instagram, Telegram व Facebook वरील मेसेज फॉरवर्ड गती, जनप्रतिक्रिया व सूत्रधारांचे थेट ट्रॅकिंग")

    # सायरन वाजवणे (रेड अलर्ट असल्यास)
    red_alerts_count = sum(1 for p in LIVE_INTEL_DATA if p["is_red_alert"])
    if siren_mode and red_alerts_count > 0:
        st.markdown(
            """
            <audio autoplay loop style="display:none;">
                <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
            </audio>
            """,
            unsafe_allow_html=True
        )

    # १. क्लिक करता येणारे स्थिती सारांश कार्ड्स
    st.markdown("##### 📌 स्थिती सारांश (तपशील पाहण्यासाठी खालील बटनांवर क्लिक करा):")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button(f"📋 एकूण संशयित नोंदी : {len(LIVE_INTEL_DATA)}", use_container_width=True):
            st.session_state["view_filter"] = "all"
    with c2:
        if st.button(f"🚨 रेड अलर्ट्स : {red_alerts_count} (सक्रिय)", use_container_width=True):
            st.session_state["view_filter"] = "red_alert"
    with c3:
        max_fwd = max(p["forward_velocity"] for p in LIVE_INTEL_DATA)
        st.metric(label="⚡ सर्वाधिक फॉरवर्ड गती", value=f"{max_fwd} / मिनिट")
    with c4:
        st.metric(label="जिल्हा शांतता स्थिती", value="सतर्क (Alert)")

    st.markdown("---")

    # २. फॉरवर्ड गतीचा स्वतंत्र तुलना तक्ता
    st.markdown("### 📤 मेसेज फॉरवर्ड गती तुलना तक्ता (Forward Speed Monitoring)")
    fwd_summary = []
    for item in LIVE_INTEL_DATA:
        _, stn, _ = scan_post_details(item["text"])
        fwd_summary.append({
            "आयडी": item["id"],
            "स्त्रोत": f"{item['source_icon']} {item['source']}",
            "पोलीस ठाणे": stn,
            "फॉरवर्ड गती (प्रति मिनिट)": f"⚡ {item['forward_velocity']} / मि.",
            "एकूण शेअर्स": f"{item['total_forwards']:,}",
            "प्रतिक्रिया गती": f"{item['reaction_velocity']} / मि.",
            "अलर्ट स्थिती": "🔴 रेड अलर्ट" if item["is_red_alert"] else "🟡 सर्वसाधारण"
        })
    st.table(pd.DataFrame(fwd_summary))

    st.markdown("---")

    # ३. अलर्ट्स यादी (फिल्टरनुसार)
    if st.session_state["view_filter"] == "red_alert":
        st.markdown("### 🚨 फक्त सक्रिय रेड अलर्ट्सची यादी (Filtered)")
        filtered_data = [p for p in LIVE_INTEL_DATA if p["is_red_alert"]]
    else:
        st.markdown("### 📋 सर्व संशयित नोंदींची यादी (All Records)")
        filtered_data = LIVE_INTEL_DATA

    for post in filtered_data:
        flagged_words, station, wireless_target = scan_post_details(post["text"])

        with st.container():
            top1, top2 = st.columns([3, 1])
            with top1:
                if post["is_red_alert"]:
                    st.error(f"🚨 **अतिसंवेदनशील रेड अलर्ट (तीव्र व्हायरल: {post['forward_velocity']} फॉरवर्ड्स/मि.)**")
                else:
                    st.warning("⚠️ **सर्वसाधारण देखरेख (Normal Watch)**")
            with top2:
                st.markdown(f"**स्त्रोत:** `{post['source_icon']} {post['source']}`")
                st.caption(f"{post['author']} | {post['time']}")

            st.markdown(f"#### {post['text']}")

            # संवेदनशील शब्द टॅग्स
            if flagged_words:
                tags = " ".join([f"`🚩 {w}`" for w in flagged_words])
                st.markdown(f"**डिटेक्ट झालेले संवेदनशील कीवर्ड्स:** {tags}")

            # हद्द आणि वायरलेस
            info1, info2 = st.columns(2)
            with info1:
                st.markdown(f"📍 **अचूक पोलीस ठाणे हद्द:** `{station}`")
                st.markdown(f"⚠️ **संभाव्य धोका:** {post['risk']}")
            with info2:
                st.markdown(f"📻 **वायरलेस निर्देश:** `{wireless_target} ला तात्काळ सतर्क करावे.`")
                st.markdown(f"📊 **एकूण फॉरवर्ड्स:** `{post['total_forwards']:,}` | प्रतिक्रिया: `{post['total_reactions']:,}`")

            # थोडक्यात प्रतिक्रिया वाचन
            with st.expander("💬 या मेसेजवरील लोकांच्या थेट प्रतिक्रिया वाचा (Public Sentiment)", expanded=False):
                st.caption("सोशल मीडियावरील प्रमुख कॉमेंट्स:")
                for comment in post["sample_comments"]:
                    st.markdown(f"- 🗣️ *\"{comment}\"*")

            # पडद्यामागील प्रमुख सूत्रधार व आयोजक
            with st.expander("👤 पडद्यामागील प्रमुख व्यक्ती व आयोजकांची यादी (Key Mobilizers & Profiles)", expanded=post["is_red_alert"]):
                if post["key_figures"]:
                    st.table(pd.DataFrame(post["key_figures"]))
                else:
                    st.info("या अलर्टशी संबंधित व्यक्तींचे डिजिटल प्रोफाइलिंग सुरू आहे...")

            st.markdown("---")

# --- ७. विभाग २: ऐतिहासिक डेटाबेस ---
elif menu_selection == "🗄️ ऐतिहासिक डेटाबेस (Historical Database)":
    st.subheader("🗄️ ऐतिहासिक डेटाबेस व ट्रेंड ॲनालिसिस")
    st.caption("मागील सर्व घटना, फॉरवर्ड गती आणि नोंदवलेल्या सूत्रधारांचा शोध घ्या.")

    s1, s2 = st.columns([3, 1])
    with s1:
        search = st.text_input("🔍 शब्द, तारीख किंवा पोलीस ठाण्यावरून शोधा:")
    with s2:
        filter_status = st.selectbox("अलर्ट प्रकार:", ["सर्व", "रेड अलर्ट", "सर्वसाधारण"])

    history_records = [
        {"तारीख व वेळ": "01-10-2026 18:55", "स्त्रोत": "Instagram Reel", "पोलीस ठाणे": "माहूर पोलीस ठाणे", "घटना": "रास्ता रोको आंदोलन", "फॉरवर्ड गती": "85/मि.", "प्रतिक्रिया": "4,200", "अलर्ट": "रेड अलर्ट", "प्रमुख सूत्रधार": "अमोल देशमुख"},
        {"तारीख व वेळ": "01-10-2026 17:30", "स्त्रोत": "WhatsApp Forward", "पोलीस ठाणे": "लोहा पोलीस ठाणे", "घटना": "सोयाबीन दर ठिय्या मोर्चा", "फॉरवर्ड गती": "34/मि.", "प्रतिक्रिया": "1,200", "अलर्ट": "रेड अलर्ट", "प्रमुख सूत्रधार": "गजानन कदम"},
        {"तारीख व वेळ": "01-10-2026 15:10", "स्त्रोत": "Telegram Broadcast", "पोलीस ठाणे": "किनवट पोलीस ठाणे", "घटना": "जंगलातील संशयित क्लिप", "फॉरवर्ड गती": "8/मि.", "प्रतिक्रिया": "310", "अलर्ट": "सर्वसाधारण", "प्रमुख सूत्रधार": "तपास सुरू"}
    ]

    df = pd.DataFrame(history_records)
    st.dataframe(df, use_container_width=True)

    st.download_button(
        label="📥 ऐतिहासिक डेटा एक्सेल/CSV मध्ये डाऊनलोड करा",
        data=df.to_csv(index=False).encode('utf-8-sig'),
        file_name="Nanded_Cyber_Archive.csv",
        mime="text/csv"
    )