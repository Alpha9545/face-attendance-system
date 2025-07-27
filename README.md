# 🎓 Face Recognition Attendance System

A web-based attendance system built with **Flask**, **OpenCV**, and **MySQL** that automatically marks student attendance through face recognition.

---

## 🚀 Features

- 🎥 Face detection and recognition (OpenCV)
- 👨‍🏫 Teacher login with class-wise access (FY/SY/TY)
- 🧑‍💼 Admin dashboard with charts and attendance stats
- 🧾 Student can view their own attendance
- 📅 Filter attendance by today's date
- 📊 Download attendance as CSV
- ✍️ New student registration with live face capture

---

## 🛠️ Tech Stack

| Layer        | Tools/Technologies            |
|--------------|-------------------------------|
| Backend      | Python, Flask                 |
| Face Engine  | OpenCV (no dlib)              |
| Database     | MySQL                         |
| Frontend     | HTML, CSS, Bootstrap, JS      |
| Charts       | Chart.js                      |

---

## 📂 Project Structure

face-attendance-system/
│
├── app.py
├── templates/
│ ├── index.html
│ ├── teacher_dashboard.html
│ └── ...
├── static/
│ ├── css/
│ └── js/
├── models/
│ └── db.py
├── mediapipe_module/
│ └── mark_attendance_mediapipe.py
├── database/
│ └── schema.sql
└── README.md


---

## 📸 How It Works

1. ✅ A face is captured using OpenCV.
2. 🧠 The face is matched against known encodings.
3. 🧾 Attendance is recorded into the MySQL database.
4. 📈 Teachers/Admins can view, filter, and download records.

---

## 📦 Setup Instructions

1. **Clone the repo:**

```bash
git clone https://github.com/yourusername/face-attendance-system.git
cd face-attendance-system


2. Create virtual environment:

bash

python -m venv venv
venv\Scripts\activate  # On Windows



3. Install requirements:

bash

pip install -r requirements.txt


4. Set up MySQL database:

Import database/schema.sql into your MySQL server.

Update DB credentials in models/db.py.




5. Run the Flask app:

bash

python app.py
Visit http://localhost:5000 in your browser.

-------------------------------------------------------

🧑‍💻 Author
Prajwal Maka

💼 BBA-CA Student

💻 Passionate about Full Stack Development