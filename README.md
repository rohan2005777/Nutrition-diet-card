# 🍎 NutriCare+ – AI Health & Nutrition Assistant for Children

NutriCare+ is a Streamlit-based AI-powered health assistant designed to support children’s nutrition, BMI analysis, diet planning, and healthy habits.  
It integrates Google Gemini AI for intelligent responses and Firebase Realtime Database for storing and managing weekly diet plans.

---

## 🚀 Features

### 🏠 Home
- Simple and child-friendly interface
- Easy sidebar navigation

### 📊 BMI & Health Analysis
- Calculates BMI using height and weight
- Categorizes BMI (Underweight, Normal, Overweight, Obese)
- AI-powered diet and exercise suggestions

### 🥗 Weekly Diet Planner
- Create 7-day meal plans (Breakfast, Lunch, Snack, Dinner)
- Input validation (only alphabets and spaces allowed)
- Save plans to Firebase Realtime Database
- View, edit, update, and delete saved plans
- Display plans in a table format

### 🧘 Health Activities
- Daily healthy habit suggestions for children

### 💪 Exercise Ideas
- Simple and kid-friendly exercise ideas

### 💬 AI Chatbot
- Interactive chatbot for nutrition and health queries
- Powered by Google Gemini AI

---

## 🛠 Tech Stack

- Frontend: Streamlit  
- AI Model: Google Gemini (gemini-2.0-flash-exp)  
- Backend: Firebase Realtime Database  
- Language: Python  

---

## 📂 Project Structure

├── app2.py
├── firebase_credentials.json
├── README.md
├── requirements.txt

yaml
Copy code

---

## 🔐 Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/nutricare-plus.git
cd nutricare-plus
2️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
3️⃣ Configure Gemini AI
Get a Gemini API key from Google AI Studio

Replace in app2.py:

python
Copy code
GEMINI_API_KEY = "YOUR_API_KEY_HERE"
4️⃣ Configure Firebase
Create a Firebase project

Enable Realtime Database

Download the service account key

Rename it to firebase_credentials.json

Place it in the project root folder

5️⃣ Run the Application
bash
Copy code
streamlit run app2.py
📊 Firebase Data Structure
json
Copy code
weekly_plans: {
  "plan_id": {
    "child_name": "Name",
    "age": 10,
    "email": "parent@email.com",
    "plan": [
      {
        "Day": "Monday",
        "Breakfast": "",
        "Lunch": "",
        "Snack": "",
        "Dinner": ""
      }
    ]
  }
}
