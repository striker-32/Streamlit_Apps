import streamlit as st
import mysql.connector
from datetime import date, timedelta
from google import genai
from google.genai import types

GEMINI_API_KEY = "AIzaSyAzgBSc6mWHXzlMdCq8WyYS981w64Tm8ec" 
client = genai.Client(api_key=GEMINI_API_KEY)

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Charan@1567",
        database="astro"
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
    """Generic Gemini text generator"""
    try:
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        return resp.text.strip()
    except Exception as e:
        return f"[Error: {e}]"

def analyze_palmistry_with_api(image_bytes):
    """Gemini multimodal palm analysis"""
    try:
        img = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                "You are a professional palm reader. Describe this person's personality, emotions, and future with positivity.",
                img
            ]
        )
        return resp.text.strip()
    except Exception as e:
        return f"[Palmistry Error] {e}"

def register_user(name, email, password, dob, place, zodiac, role="user"):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name,email,password,dob,place,zodiac,role) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (name,email,password,dob,place,zodiac,role)
    )
    conn.commit()
    conn.close()

def verify_login(email, password):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE email=%s AND password=%s",(email,password))
    user = cur.fetchone()
    conn.close()
    return user

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
if "user" not in st.session_state:
    st.session_state.user=None

st.set_page_config(page_title="🔮 Astrology & Palmistry", layout="wide")

if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("Menu", ["Login","Register"])
else:
    user = st.session_state.user
    st.sidebar.success(f"Welcome, {user['name']}!")
    menu = st.sidebar.selectbox(
        "Select Feature",
        ["Predictions","Palmistry","Chat Astrologer","Compatibility","Profile","Logout"]
    )

if menu=="Register":
    st.title("🌟 Register for Astrology App")
    name=st.text_input("Full Name")
    email=st.text_input("Email")
    password=st.text_input("Password",type="password")
    dob=st.date_input("Date of Birth",min_value=date(1900,1,1),max_value=date.today())
    place=st.text_input("Place of Birth")

    if st.button("Register"):
        if all([name,email,password,place]):
            zodiac=get_zodiac_sign(dob.day,dob.month)
            try:
                register_user(name,email,password,dob,place,zodiac)
                st.success("✅ Registration complete! You can now log in.")
            except Exception as e:
                st.error(f"Registration failed: {e}")
        else:
            st.warning("Fill all fields!")

# -------------------- LOGIN --------------------
elif menu=="Login":
    st.title("🔑 Login")
    email=st.text_input("Email")
    password=st.text_input("Password",type="password")

    if st.button("Login"):
        u=verify_login(email,password)
        if u:
            st.session_state.logged_in=True
            st.session_state.user=u
            st.rerun()
        else:
            st.error("Invalid credentials!")

elif menu=="Logout":
    st.session_state.logged_in=False
    st.session_state.user=None
    st.rerun()

elif menu=="Predictions" and st.session_state.logged_in:
    user=st.session_state.user
    st.title(f"🔮 Astrology Predictions for {user['zodiac']}")
    period=st.selectbox("Select Prediction Period",["Today","Next Month","Whole Year"])
    if st.button("Get Prediction"):
        pred=ai_text(f"Give a {period} horoscope for zodiac {user['zodiac']}.")
        st.success(pred)

elif menu=="Palmistry" and st.session_state.logged_in:
    st.title("✋ Palmistry (AI-Powered)")
    st.write("Place your hand in front of the camera and capture your palm.")
    img=st.camera_input("Capture Palm Image")

    if img:
        st.image(img,use_column_width=True)
        with st.spinner("Analyzing your palm..."):
            result=analyze_palmistry_with_api(img.getvalue())
        st.success(result)

elif menu=="Chat Astrologer" and st.session_state.logged_in:
    st.title("💬 Chat with Your AI Astrologer")
    st.write("Ask anything about your zodiac, career, or future.")
    
    if "chat" not in st.session_state:
        st.session_state.chat=[]
        
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    user_input=st.chat_input("Ask your astrologer...")
    if user_input:
        st.session_state.chat.append({"role":"user","content":user_input})
        reply=ai_text(f"You are an expert astrologer for zodiac {st.session_state.user['zodiac']}. {user_input}")
        st.session_state.chat.append({"role":"assistant","content":reply})
        st.rerun()

elif menu=="Compatibility" and st.session_state.logged_in:
    st.title("💞 Love Compatibility Checker")
    name1=st.text_input("Your Name",st.session_state.user["name"])
    zodiac1=st.session_state.user["zodiac"]
    name2=st.text_input("Partner Name")
    zodiac2=st.selectbox("Partner Zodiac",["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                                           "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"])
    if st.button("Check Compatibility"):
        result=ai_text(f"Compare love compatibility between {zodiac1} and {zodiac2}. Give a score out of 10 with an explanation.")
        st.success(result)

elif menu=="Profile" and st.session_state.logged_in:
    u=st.session_state.user
    st.title("👤 My Profile")
    st.write(f"**Name:** {u['name']}")
    st.write(f"**Email:** {u['email']}")
    st.write(f"**Zodiac:** {u['zodiac']}")
    st.write(f"**DOB:** {u['dob']}")
    st.write(f"**Place:** {u['place']}")
    st.info("✨ You can view your past predictions and palm readings in future updates!")
