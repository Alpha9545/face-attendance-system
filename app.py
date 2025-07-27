from flask import Flask, render_template, request, redirect, url_for, session, send_file
import cv2
import os
from datetime import datetime
from db_config import get_connection
import mysql.connector
import io
import csv
from models import db, Student, Attendance

app = Flask(__name__)

app.secret_key = 'A7f8D9s3L0x!qB1@K2mZ4rT5'

@app.route('/')
def home():
    return render_template('welcome.html')

# ------------------ Database Connection ------------------
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  
        database="face_attendance"
    )


@app.route('/make_attendance')
def make_attendance():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cap = cv2.VideoCapture(0)

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    matched_id = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face_roi = gray[y:y + h, x:x + w]
            id_, confidence = recognizer.predict(face_roi)

            if confidence < 80:  # lower is better
                matched_id = id_
                cap.release()
                cv2.destroyAllWindows()
                break

        if matched_id:
            break

        cv2.imshow("Detecting...", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if matched_id:
        cursor.execute("SELECT * FROM students WHERE rollno = %s", (str(matched_id),))
        student = cursor.fetchone()

        if student:
            now = datetime.now()
            cursor.execute("""
                INSERT INTO attendance (rollno, name, class_name, date, time)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                student['rollno'],
                student['name'],
                student['class_name'],
                now.date(),
                now.time().strftime("%H:%M:%S")
            ))
            conn.commit()
            cursor.close()
            conn.close()
            return f"<h2>Attendance Marked for {student['name']} ({student['rollno']})</h2><a href='/'>Go Back</a>"
    return redirect("/register")




@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        rollno = request.form['rollno']
        student_id = request.form['student_id']
        name = request.form['name']
        class_name = request.form['class_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate data
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register_student'))


        # Save student info to database
        conn = get_connection()
        cursor = conn.cursor()

        # Check if already exists
        cursor.execute("SELECT * FROM students WHERE rollno = %s", (rollno,))
        if cursor.fetchone():
            return f"<h3>Student with Roll No {rollno} already exists.</h3><a href='/'>Back</a>"

        # Save to students table
        cursor.execute("""
            INSERT INTO students (rollno, student_id, name, class_name, password, image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (rollno, student_id, name, class_name, password, f"static/faces/{rollno}"))
        conn.commit()

        # Create face folder for student
        face_folder = os.path.join('static/faces', rollno)
        if not os.path.exists(face_folder):
            os.makedirs(face_folder)

        # Capture 20 face images
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        count = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                count += 1
                face_img = frame[y:y + h, x:x + w]
                face_img = cv2.resize(face_img, (200, 200))
                file_path = os.path.join(face_folder, f"{count}.jpg")
                cv2.imwrite(file_path, face_img)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            cv2.imshow("Registering Face - Press Q to stop", frame)

            if cv2.waitKey(1) & 0xFF == ord('q') or count >= 20:
                break

        cap.release()
        cv2.destroyAllWindows()
        cursor.close()
        conn.close()

        return render_template('registration_success.html', name=name, student_id=student_id, rollno=rollno, class_name=class_name)

    return render_template('register.html')


# ------------------ Student Login Route ------------------
@app.route('/student', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        rollno = request.form['rollno']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM students WHERE rollno = %s AND password = %s", (rollno, password))
        student = cursor.fetchone()

        if student:
            cursor.execute("SELECT date, time FROM attendance WHERE rollno = %s ORDER BY date DESC, time DESC", (rollno,))
            records = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template("student_attendance.html", name=student['name'], rollno=rollno, student_id=student['student_id'], records=records, class_name=student['class_name'])
        else:
            return "<h3>Invalid Roll No or Password</h3><a href='/student'>Try Again</a>"

    return render_template("student_login.html")


# ------------------ Teacher Route ------------------
@app.route('/teacher', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Authenticate teacher
        cursor.execute("SELECT * FROM teachers WHERE username=%s AND password=%s", (username, password))
        teacher = cursor.fetchone()

        if teacher:
            session['teacher_username'] = username
            session['teacher_class'] = teacher['class_name']
            cursor.close()
            conn.close()
            return redirect(url_for('teacher_dashboard'))

        cursor.close()
        conn.close()
        return "<h3>Invalid credentials</h3><a href='/teacher'>Try again</a>"

    return render_template('teacher_login.html')


@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'teacher_username' not in session:
        return redirect(url_for('teacher_login'))

    username = session['teacher_username']
    class_name = session['teacher_class']
    filter_today = request.args.get('filter') == 'today'

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Total students
    cursor.execute("SELECT COUNT(*) AS total_students FROM students WHERE class_name = %s", (class_name,))
    total_students = cursor.fetchone()['total_students']

    # Student list
    cursor.execute("SELECT rollno, name FROM students WHERE class_name = %s", (class_name,))
    students = cursor.fetchall()

    # Today's count
    cursor.execute("SELECT COUNT(*) AS count FROM attendance WHERE class_name = %s AND DATE(date) = CURDATE()", (class_name,))
    count = cursor.fetchone()['count']

    # Attendance rate
    rate = round((count / total_students) * 100, 2) if total_students > 0 else 0

    # Records (filtered)
    if filter_today:
        cursor.execute("""
            SELECT a.rollno, s.name, a.date, a.time
            FROM attendance a
            JOIN students s ON a.rollno = s.rollno
            WHERE s.class_name = %s AND DATE(a.date) = CURDATE()
            ORDER BY a.date DESC, a.time DESC
        """, (class_name,))
    else:
        cursor.execute("""
            SELECT a.rollno, s.name, a.date, a.time
            FROM attendance a
            JOIN students s ON a.rollno = s.rollno
            WHERE s.class_name = %s
            ORDER BY a.date DESC, a.time DESC
        """, (class_name,))
    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('teacher_dashboard.html',
                           username=username,
                           class_name=class_name,
                           records=records,
                           total_students=total_students,
                           students=students,
                           count=count,
                           rate=rate,
                           filter_today=filter_today)
    



# ------------------ Admin Route ------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        if admin:
            return redirect(url_for('admin_dashboard'))
        return "Invalid credentials"
    return render_template('admin_login.html')


@app.route('/admin/dashboard')
def admin_dashboard():
    class_name = request.args.get('class_name')
    date = request.args.get('date')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT a.rollno, s.name, s.class_name, a.date, a.time
        FROM attendance a
        JOIN students s ON a.rollno = s.rollno
        WHERE 1=1
    """
    values = []

    if class_name:
        query += " AND s.class_name = %s"
        values.append(class_name)
    if date:
        query += " AND a.date = %s"
        values.append(date)

    query += " ORDER BY a.date DESC, a.time DESC"
    cursor.execute(query, tuple(values))
    records = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total_students FROM students")
    result = cursor.fetchone()
    total = result['total_students']

    cursor.execute("SELECT COUNT(*) AS total_teachers FROM teachers")
    res = cursor.fetchone()
    total_t = res['total_teachers']

    # Today's count
    cursor.execute("SELECT COUNT(*) AS count FROM attendance WHERE  DATE(date) = CURDATE()")
    count = cursor.fetchone()['count']

    # Count for pie
    absent = total-count


    # Count for Chart
    cursor.execute("SELECT s.class_name, COUNT(*) as total FROM attendance a JOIN students s ON a.rollno = s.rollno GROUP BY s.class_name")
    counts = cursor.fetchall()
    fy = sy = ty = 0
    for c in counts:
        if c['class_name'] == 'FY':
            fy = c['total']
        elif c['class_name'] == 'SY':
            sy = c['total']
        elif c['class_name'] == 'TY':
            ty = c['total']

    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', records=records, fy=fy, sy=sy, ty=ty, total=total, total_t=total_t, count=count, absent=absent)


# ------------------ CVS download Route ------------------
@app.route('/admin/download')
def admin_download():
    class_name = request.args.get('class_name')
    date = request.args.get('date')

    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT a.rollno, s.name, s.class_name, a.date, a.time
        FROM attendance a
        JOIN students s ON a.rollno = s.rollno
        WHERE 1=1
    """
    values = []
    if class_name:
        query += " AND s.class_name = %s"
        values.append(class_name)
    if date:
        query += " AND a.date = %s"
        values.append(date)

    cursor.execute(query, tuple(values))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create CSV
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Roll No', 'Name', 'Class', 'Date', 'Time'])
    cw.writerows(rows)
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)

    return send_file(output, mimetype='text/csv', as_attachment=True, download_name='attendance.csv')



@app.route('/admin/chart')
def admin_chart():
    conn = get_connection()
    cursor = conn.cursor()

    # Get attendance count per class
    cursor.execute("""
        SELECT s.class_name, COUNT(a.id) as attendance_count
        FROM attendance a
        JOIN students s ON a.rollno = s.rollno
        GROUP BY s.class_name
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()

    class_names = [row[0] for row in data]
    counts = [row[1] for row in data]

    return render_template("admin_chart.html", class_names=class_names, counts=counts)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))  # or 'home' or any other route


if __name__ == '__main__':
    app.run(debug=True)


