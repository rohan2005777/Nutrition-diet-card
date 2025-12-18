import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import google.generativeai as genai
from PIL import Image
import os
import uuid
import pandas as pd
import re

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="NutriCare+ AI Health Assistant",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- GEMINI AI SETUP --------------------
GEMINI_API_KEY = "YOUR_API_KEY_HERE"  # 🔑 Replace with your actual Gemini API key
try:
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_API_KEY_HERE":
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
    else:
        model = None
except Exception as e:
    model = None
    st.warning(f"⚠️ Gemini init warning: {e}")

# -------------------- FIREBASE INITIALIZATION --------------------
firebase_ready = False
try:
    if os.path.exists("firebase_credentials.json"):
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://nutricare-planner-default-rtdb.firebaseio.com/'
            })
        firebase_ready = True
    else:
        firebase_ready = False
except Exception as e:
    firebase_ready = False
    st.error(f"❌ Firebase initialization failed: {e}")

# -------------------- CUSTOM STYLES --------------------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #e3f2fd 0%, #fff9c4 100%); }
.main-header {
    background: linear-gradient(90deg, #4CAF50, #2196F3);
    padding: 20px; border-radius: 10px; color: white;
    text-align: center; margin-bottom: 20px;
}
.card {
    background: white; padding: 20px; border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 10px 0;
}
.bmi-result {
    font-size: 24px; font-weight: bold; padding: 15px;
    border-radius: 10px; text-align: center; margin: 10px 0;
}
.healthy { background-color: #4CAF50; color: white; }
.underweight { background-color: #FF9800; color: white; }
.overweight { background-color: #F44336; color: white; }
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4712/4712109.png", width=100)
st.sidebar.title("🍎 NutriCare+")
page = st.sidebar.radio("Navigate", [
    "🏠 Home",
    "📊 BMI & Health Analysis",
    "🥗 Weekly Diet Planner",
    "🧘 Health Activities",
    "💪 Exercise Ideas",
    "💬 AI Chatbot"
])

# -------------------- HELPERS --------------------
def calculate_bmi(weight, height):
    try:
        bmi = weight / ((height / 100) ** 2)
    except Exception:
        return None, "Invalid input", ""
    if bmi < 18.5:
        return round(bmi, 1), "Underweight", "underweight"
    elif bmi < 25:
        return round(bmi, 1), "Normal Weight", "healthy"
    elif bmi < 30:
        return round(bmi, 1), "Overweight", "overweight"
    else:
        return round(bmi, 1), "Obese", "overweight"

def get_ai_response(question):
    if model is None:
        return "AI not configured. Set GEMINI_API_KEY to use the AI features."
    try:
        prompt = f"You are NutriCare+, a friendly AI nutritionist for children. Answer simply: {question}"
        response = model.generate_content(prompt)
        text = getattr(response, "text", None) or getattr(response, "output", None)
        if isinstance(text, list):
            text = " ".join([t.get("content", "") for t in text])
        return text or str(response)
    except Exception as e:
        return f"Error calling AI: {e}"

# -------------------- PAGE 3: WEEKLY DIET PLANNER --------------------
if page == "🥗 Weekly Diet Planner":
    st.markdown('<div class="main-header"><h1>🥗 Weekly Diet Planner</h1><p>Save, view, and manage weekly meal plans!</p></div>', unsafe_allow_html=True)

    child_name = st.text_input("👶 Child's Name", key="new_child_name")
    age = st.number_input("🎂 Age (years)", 3, 18, key="new_age")
    parent_email = st.text_input("📧 Parent Email (optional)", placeholder="example@email.com", key="new_parent_email")

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekly_plan = []

    # ✅ Allow only alphabetic characters and spaces
    valid_pattern = re.compile(r'^[A-Za-z\s]+$')

    st.markdown("### ✍️ Enter Meals for Each Day")
    for day in days:
        with st.expander(f"📅 {day}"):
            breakfast = st.text_input(f"{day} Breakfast", key=f"new_{day}_breakfast")
            lunch = st.text_input(f"{day} Lunch", key=f"new_{day}_lunch")
            snack = st.text_input(f"{day} Snack", key=f"new_{day}_snack")
            dinner = st.text_input(f"{day} Dinner", key=f"new_{day}_dinner")
            weekly_plan.append({
                "Day": day,
                "Breakfast": breakfast,
                "Lunch": lunch,
                "Snack": snack,
                "Dinner": dinner
            })

    # -------------------- SAVE TO FIREBASE --------------------
    if st.button("💾 Save to Firebase"):
        if not firebase_ready:
            st.error("❌ Firebase not connected.")
        elif not child_name.strip():
            st.warning("⚠️ Please enter the child's name.")
        else:
            invalid_entries = []
            for meal in weekly_plan:
                for key, value in meal.items():
                    if key != "Day" and value.strip():
                        if not valid_pattern.fullmatch(value.strip()):
                            invalid_entries.append(f"{meal['Day']} → {key}: '{value}'")

            if invalid_entries:
                # Stop saving to database
                st.error("⚠️ Invalid entries found! Plan NOT saved to database.")
                st.warning("Please remove numbers or special characters from these fields:")
                for entry in invalid_entries:
                    st.write(f"- {entry}")
            else:
                try:
                    ref = db.reference("/weekly_plans")
                    uid = str(uuid.uuid4())[:8]
                    payload = {
                        "id": uid,
                        "child_name": child_name.strip(),
                        "age": int(age),
                        "email": parent_email.strip(),
                        "plan": weekly_plan
                    }
                    ref.child(uid).set(payload)
                    st.success(f"✅ Plan for {child_name} saved successfully! (ID: {uid})")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"⚠️ Error saving to Firebase: {e}")

    # -------------------- VIEW OR EDIT SAVED PLANS --------------------
    st.markdown("### 📖 View or Edit Saved Plans")
    if not firebase_ready:
        st.info("Firebase not connected — saved plans aren't available.")
    else:
        try:
            ref = db.reference("/weekly_plans")
            data = ref.get() or {}
            if data:
                plan_options = {f"{v.get('child_name', 'Unknown')} (ID: {k})": k for k, v in data.items()}
                selected_label = st.selectbox("Select a plan to view/edit:", ["Select..."] + list(plan_options.keys()))
                if selected_label != "Select...":
                    plan_id = plan_options[selected_label]
                    selected_data = data[plan_id]
                    st.markdown(f"### 🧾 Editing Plan for **{selected_data['child_name']}** (Age {selected_data.get('age','-')})")

                    updated_plan = []
                    for meal in selected_data.get("plan", []):
                        day = meal.get("Day", "Day")
                        with st.expander(f"📅 {day}"):
                            b = st.text_input(f"{day} Breakfast", value=meal.get("Breakfast",""), key=f"edit_{plan_id}_{day}_b")
                            l = st.text_input(f"{day} Lunch", value=meal.get("Lunch",""), key=f"edit_{plan_id}_{day}_l")
                            s = st.text_input(f"{day} Snack", value=meal.get("Snack",""), key=f"edit_{plan_id}_{day}_s")
                            d = st.text_input(f"{day} Dinner", value=meal.get("Dinner",""), key=f"edit_{plan_id}_{day}_d")
                            updated_plan.append({
                                "Day": day, "Breakfast": b, "Lunch": l, "Snack": s, "Dinner": d
                            })

                    if st.button("🔄 Update Plan", key=f"update_{plan_id}"):
                        invalid_entries = []
                        for meal in updated_plan:
                            for key, value in meal.items():
                                if key != "Day" and value.strip():
                                    if not valid_pattern.fullmatch(value.strip()):
                                        invalid_entries.append(f"{meal['Day']} → {key}: '{value}'")

                        if invalid_entries:
                            st.error("⚠️ Invalid input detected! Update cancelled — plan NOT changed.")
                            for entry in invalid_entries:
                                st.write(f"- {entry}")
                        else:
                            ref.child(plan_id).update({"plan": updated_plan})
                            st.success("✅ Plan updated successfully!")
                            st.experimental_rerun()

                    if st.button("🗑 Delete Plan", key=f"delete_{plan_id}"):
                        ref.child(plan_id).delete()
                        st.warning("🗑 Plan deleted successfully!")
                        st.experimental_rerun()

                    st.markdown("### 📅 Current Plan Overview")
                    df = pd.DataFrame(updated_plan)
                    st.dataframe(df, use_container_width=True)
            else:
                st.info("📭 No saved plans yet.")
        except Exception as e:
            st.error(f"⚠️ Error fetching plans: {e}")

# -------------------- OTHER PAGES --------------------
elif page == "🏠 Home":
    st.markdown('<div class="main-header"><h1>🍎 Welcome to NutriCare+</h1><p>Your AI-Powered Health & Nutrition Assistant for Children</p></div>', unsafe_allow_html=True)
    st.info("👈 Use the sidebar to explore BMI analysis, diet planning, and AI chat!")

elif page == "📊 BMI & Health Analysis":
    st.markdown('<div class="main-header"><h1>📊 BMI Calculator</h1></div>', unsafe_allow_html=True)
    weight = st.number_input("Weight (kg)", 1.0, 200.0, 30.0)
    height = st.number_input("Height (cm)", 30.0, 250.0, 120.0)
    if st.button("Calculate BMI"):
        bmi, category, css = calculate_bmi(weight, height)
        if bmi is None:
            st.error("Invalid input for BMI calculation.")
        else:
            st.markdown(f'<div class="bmi-result {css}">BMI: {bmi}<br>{category}</div>', unsafe_allow_html=True)
            st.write(get_ai_response(f"A child has a BMI of {bmi}. Suggest healthy diet and exercise tips."))

elif page == "🧘 Health Activities":
    st.markdown('<div class="main-header"><h1>🧘 Healthy Habits</h1></div>', unsafe_allow_html=True)
    st.write("- Stretch, drink water, and eat fruits every morning!")

elif page == "💪 Exercise Ideas":
    st.markdown('<div class="main-header"><h1>💪 Exercise Ideas</h1></div>', unsafe_allow_html=True)
    st.write("🏃 Play outdoor games or dance for 1 hour every day!")

elif page == "💬 AI Chatbot":
    st.markdown('<div class="main-header"><h1>💬 Chat with NutriCare+ AI</h1></div>', unsafe_allow_html=True)
    if "chat" not in st.session_state:
        st.session_state.chat = []
    for chat in st.session_state.chat:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])
    q = st.chat_input("Ask your question...")
    if q:
        st.session_state.chat.append({"role": "user", "content": q})
        a = get_ai_response(q)
        with st.chat_message("assistant"):
            st.write(a)
        st.session_state.chat.append({"role": "assistant", "content": a})

# -------------------- FOOTER --------------------
st.markdown("""
---
<div style='text-align:center; color:#666;'>
<p>🍎 NutriCare+ | AI & Firebase Health Assistant for Children</p>
<p>💾 Weekly Diet Plans | 🤖 AI by Gemini | 🔒 Firebase-secured</p>
<p>© 2025 NutriCare+ | Educational Use Only</p>
</div>
""", unsafe_allow_html=True)
