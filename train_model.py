import cv2
import os
import numpy as np

data_dir = 'static/faces'
faces = []
ids = []

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

for student_folder in os.listdir(data_dir):
    student_path = os.path.join(data_dir, student_folder)
    if not os.path.isdir(student_path):
        continue

    for img_name in os.listdir(student_path):
        img_path = os.path.join(student_path, img_name)
        img = cv2.imread(img_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces_rect = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        for (x, y, w, h) in faces_rect:
            face = gray[y:y + h, x:x + w]
            faces.append(face)
            ids.append(int(student_folder))

# Train the recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, np.array(ids))
recognizer.save('trainer/trainer.yml')
print("✅ Training Complete")
