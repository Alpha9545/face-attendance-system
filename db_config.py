import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",         # your phpMyAdmin username
        password="",         # leave blank if using XAMPP default
        database="face_attendance"
    )
