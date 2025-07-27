import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Camera not accessible.")
else:
    print("✅ Camera opened.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Frame not read properly.")
            break

        cv2.imshow("Webcam Test - Press Q to Quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
