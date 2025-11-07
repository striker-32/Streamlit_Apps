import requests
import streamlit as st
from streamlit_js_eval import get_geolocation
import google.genai as genai

WEATHER_API_KEY = "8f1b2bb4e9921443522d43cc36a8a719"
GEMINI_API_KEY = "AIzaSyAz3zC_aGMXlZWY31tBBJfZoEeQRVw0MX4"

st.set_page_config(page_title="🌦️ Weather & Safety Assistant", page_icon="☁️")
st.title("🌦️ Weather & Safety Assistant")

def get_weather(lat, lon):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
    res = requests.get(url).json()
    return res if "main" in res else None

def get_coordinates(city):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={WEATHER_API_KEY}"
    res = requests.get(url).json()
    if res: return res[0]["lat"], res[0]["lon"]
    return None, None

def get_city(lat, lon):
    url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={WEATHER_API_KEY}"
    res = requests.get(url).json()
    return res[0].get("name", "Unknown") if res else "Unknown"

def get_precautions(temp, city, desc, humidity):
    query = (
        f"The current temperature is {temp}°C in {city} with {desc} "
        f"and {humidity}% humidity. Give short safety precautions for this weather."
    )
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(model="gemini-2.5-flash", contents=query)
    return response.text

st.subheader("📍 Detecting your location...")
loc = get_geolocation()

if loc and "coords" in loc:
    lat, lon = loc["coords"]["latitude"], loc["coords"]["longitude"]
    city = get_city(lat, lon)
    st.success(f"📍 Location: **{city}**")

    data = get_weather(lat, lon)
    if data:
        temp = round(data["main"]["temp"] - 273.15, 2)
        desc = data["weather"][0]["description"].capitalize()
        humidity = data["main"]["humidity"]

        st.write(f"🌡️ Temperature: **{temp}°C**")
        st.write(f"☁️ Weather: **{desc}**")
        st.write(f"💧 Humidity: **{humidity}%**")
        st.map([{"lat": lat, "lon": lon}], zoom=13)

        if st.button("💡 Show Precautions"):
            st.write(get_precautions(temp, city, desc, humidity))
else:
    st.warning("⚠️ Please allow location access in your browser.")

st.markdown("---")
st.subheader("🔍 Check Another City")
city_input = st.text_input("Enter city name:")

if st.button("Get Weather"):
    if not city_input:
        st.warning("⚠️ Enter a valid city name.")
    else:
        lat, lon = get_coordinates(city_input)
        if lat:
            data = get_weather(lat, lon)
            if data:
                temp = round(data["main"]["temp"] - 273.15, 2)
                desc = data["weather"][0]["description"].capitalize()
                humidity = data["main"]["humidity"]

                st.success(f"🌍 City: **{city_input}**")
                st.write(f"🌡️ Temperature: **{temp}°C**")
                st.write(f"☁️ Weather: **{desc}**")
                st.write(f"💧 Humidity: **{humidity}%**")
                st.map([{"lat": lat, "lon": lon}], zoom=13)

                st.subheader("🌤️ Precautionary Advice:")
                st.write(get_precautions(temp, city_input, desc, humidity))
            else:
                st.error("⚠️ Could not fetch weather data.")
        else:
            st.error("❌ City not found.")



