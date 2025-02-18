#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
import cv2
import time
import mediapipe as mp
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

mp_face_detection = mp.solutions.face_detection

class FaceDetectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Detection")
        self.setGeometry(100, 100, 800, 600)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("⚠️ Fehler: Kamera kann nicht geöffnet werden!")

        self.label = QLabel(self)
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.8)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

        self.last_face_detected_time = time.time()
        self.no_face_logged = False
        self.face_was_missing = True

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("❌ Kein Kamerabild erhalten.")
            return
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(frame_rgb)

        face_detected = False

        if results.detections:
            for detection in results.detections:
                confidence = detection.score[0]
                if confidence >= 0.8:
                    face_detected = True
                    self.last_face_detected_time = time.time()
                    self.no_face_logged = False

                    if self.face_was_missing:
                        print("✅ Face detected")
                        self.face_was_missing = False

                    bboxC = detection.location_data.relative_bounding_box
                    h, w, _ = frame.shape
                    bbox = (
                        int(bboxC.xmin * w),
                        int(bboxC.ymin * h),
                        int(bboxC.width * w),
                        int(bboxC.height * h)
                    )

                    cv2.rectangle(frame_rgb, bbox, (0, 255, 0), 2)
                    cv2.putText(frame_rgb, f"{confidence:.2f}", (bbox[0], bbox[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        if not face_detected and time.time() - self.last_face_detected_time > 2:
            if not self.no_face_logged:
                print("❌ No face detected")
                self.no_face_logged = True
                self.face_was_missing = True

        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)
        self.label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceDetectorApp()
    window.show()
    sys.exit(app.exec_())


# In[ ]:




