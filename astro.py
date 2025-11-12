import streamlit as st
import mysql.connector
from datetime import date
from google import genai
from google.genai import types

GEMINI_API_KEY = "AIzaSyAzgBSc6mWHXzlMdCq8WyYS981w64Tm8ec"
client = genai.Client(api_key=GEMINI_API_KEY)

def connect_db():
    return mysql.connector.connect(
        host="sql12.freesqldatabase.com",
        user="sql12807349",
        password="eGh4jjT1zN",
        database="sql12807349",
        port = 3306
    )

def get_zodiac_sign(day, month):
    zodiac_dates = [
        ((12, 22), (1, 19), "Capricorn"), ((1, 20), (2, 18), "Aquarius"),
        ((2, 19), (3, 20), "Pisces"), ((3, 21), (4, 19), "Aries"),
        ((4, 20), (5, 20), "Taurus"), ((5, 21), (6, 20), "Gemini"),
        ((6, 21), (7, 22), "Cancer"), ((7, 23), (8, 22), "Leo"),
        ((8, 23), (9, 22), "Virgo"), ((9, 23), (10, 22), "Libra"),
        ((10, 23), (11, 21), "Scorpio"), ((11, 22), (12, 21), "Sagittarius")
    ]
    for start, end, sign in zodiac_dates:
        if (month == start[0] and day >= start[1]) or (month == end[0] and day <= end[1]):
            return sign
    return "Capricorn"

def ai_text(prompt):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"[Error: {e}]"

def analyze_palmistry_with_api(image_bytes):
    try:
        img = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                "You are a professional palm reader. Describe this person's personality, strengths, and future with positivity.",
                img
            ]
        )
        return response.text.strip()
    except Exception as e:
        return f"[Palmistry Error] {e}"

def register_user(name, email, password, dob, place, zodiac, phone):
    conn = connect_db()
    cur = conn.cursor()
    sql = ("INSERT INTO users (name, email, password, dob, place, zodiac, phone) "
           "VALUES (%s, %s, %s, %s, %s, %s, %s)")
    cur.execute(sql, (name, email, password, dob, place, zodiac, phone))
    conn.commit()
    conn.close()

def verify_login(email, password):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cur.fetchone()
    conn.close()
    return user

st.set_page_config(page_title="🔮 Astro & Palmistry AI", layout="wide", page_icon="✨")

st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: white;
        font-size: 36px;
        background: linear-gradient(90deg, #ff7eb3, #ff758c, #ff7eb3);
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
    }
    .stButton>button {
        background: linear-gradient(90deg, #a855f7, #ec4899);
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 0.5em 1.5em;
        transition: 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #ec4899, #a855f7);
    }
    .sidebar .sidebar-content {
        background-color: #f9fafb;
    }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712023.png", width=120)
    st.markdown("### 🔮 **Astro & Palmistry App**")
    if not st.session_state.logged_in:
        menu = st.selectbox("Navigation", ["Login", "Register"])
    else:
        st.sidebar.success(f"Welcome, {st.session_state.user['name']} ✨")
        menu = st.selectbox("Explore", ["Predictions", "Palmistry", "Chat Astrologer", "Compatibility", "Profile", "Logout"])

if menu == "Register":
    st.markdown('<div class="main-title">🌟 Create Your Account</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        phone = st.text_input("Phone Number", max_chars=15, placeholder="e.g. +91XXXXXXXXXX")
    with col2:
        dob = st.date_input("Date of Birth", min_value=date(1900, 1, 1), max_value=date.today())
        place = st.text_input("Place of Birth")

    if st.button("Register"):
        if name and email and password and place and phone:
            zodiac = get_zodiac_sign(dob.day, dob.month)
            try:
                register_user(name, email, password, dob, place, zodiac, phone)
                st.balloons()
                st.success(f"✅ Registration Successful! Your zodiac sign is **{zodiac}**.")
            except mysql.connector.IntegrityError:
                st.error("⚠️ Email already registered.")
            except Exception as e:
                st.error(f"Registration failed: {e}")
        else:
            st.warning("Please fill all fields.")

elif menu == "Login":
    st.markdown('<div class="main-title">🔑 Login to Continue</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <style>
                div[data-testid="stTextInput"] > div > div > input {
                    width: 80% !important;
                    margin: 0 auto !important;
                    display: block;
                    border-radius: 8px;
                    height: 2.2em;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        st.markdown("<br>", unsafe_allow_html=True)
        login_col1, login_col2, login_col3 = st.columns([1, 1, 1])
        with login_col2:
            if st.button("Login", use_container_width=True):
                user = verify_login(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.toast(f"🌟 Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password ❌")

elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

elif menu == "Predictions" and st.session_state.logged_in:
    user = st.session_state.user
    st.markdown(f'<div class="main-title">🔮 {user["zodiac"]} Horoscope</div>', unsafe_allow_html=True)
    period = st.radio("Choose Prediction Period:", ["Today", "Next Month", "Whole Year"], horizontal=True)
    if st.button("✨ Get My Prediction"):
        with st.spinner("Consulting the stars... 🔭"):
            prediction = ai_text(f"Give a {period} horoscope for zodiac {user['zodiac']}.")
        st.success(prediction)

elif menu == "Palmistry" and st.session_state.logged_in:
    st.markdown('<div class="main-title">✋ AI Palm Reading</div>', unsafe_allow_html=True)
    st.info("Capture or upload your palm image for AI-based reading.")
    img = st.camera_input("📸 Capture Your Palm")
    if img:
        st.image(img, caption="Your Palm", use_container_width=True)
        with st.spinner("Analyzing your palm lines... 🔮"):
            result = analyze_palmistry_with_api(img.getvalue())
        st.success(result)

elif menu == "Chat Astrologer" and st.session_state.logged_in:
    st.markdown('<div class="main-title">💬 Ask the AI Astrologer</div>', unsafe_allow_html=True)
    st.caption("Ask about your zodiac, love, or future ✨")

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask something about your future...")
    if user_input:
        st.session_state.chat.append({"role": "user", "content": user_input})
        reply = ai_text(f"You are an astrologer. Answer this: {user_input}")
        st.session_state.chat.append({"role": "assistant", "content": reply})
        st.rerun()

elif menu == "Compatibility" and st.session_state.logged_in:
    st.markdown('<div class="main-title">💞 Zodiac Compatibility</div>', unsafe_allow_html=True)
    name1 = st.text_input("Your Name", st.session_state.user["name"])
    zodiac1 = st.session_state.user["zodiac"]
    name2 = st.text_input("Partner Name")
    zodiac2 = st.selectbox("Partner Zodiac", [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ])
    if st.button("💘 Check Compatibility"):
        with st.spinner("Reading your stars together... 💫"):
            result = ai_text(f"Compare love compatibility between {zodiac1} and {zodiac2}. Give a score out of 10 with a brief explanation.")
        st.progress(100)
        st.success(result)

elif menu == "Profile" and st.session_state.logged_in:
    u = st.session_state.user
    st.markdown('<div class="main-title">👤 My Profile</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {u['name']}")
        st.write(f"**Email:** {u['email']}")
        st.write(f"**Phone:** {u['phone']}")
        st.write(f"**Zodiac:** {u['zodiac']}")
    with col2:
        st.write(f"**Date of Birth:** {u['dob']}")
        st.write(f"**Place of Birth:** {u['place']}")
    st.info("✨ More exciting profile insights coming soon!")



