import sys
import cv2
import time
import mediapipe as mp
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, pyqtSignal

mp_face_detection = mp.solutions.face_detection

class FaceDetectorApp(QWidget):
    status_changed = pyqtSignal(int)  # ✅ Signal als Klassenattribut

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Detection")
        self.setGeometry(100, 100, 800, 600)

        # Verwende zuerst die integrierte Kamera (Index 0)
        self.kamera_index = 0
        self.cap = cv2.VideoCapture(self.kamera_index, cv2.CAP_ANY)
        
        # Prüfen, ob die Kamera geöffnet und funktionsfähig ist
        if not self.cap.isOpened():
            print(f"⚠️ Integrierte Kamera (Index {self.kamera_index}) konnte nicht geöffnet werden.")
            use_integrated = False
        else:
            # Teste, ob tatsächlich ein Frame gelesen werden kann
            ret, frame = self.cap.read()
            if not ret:
                print("⚠️ Integrierte Kamera konnte geöffnet werden, aber liefert keine Bilder.")
                use_integrated = False
            else:
                print("✅ Integrierte Kamera funktioniert vollständig!")
                use_integrated = True
        
        # Wenn die integrierte Kamera nicht funktioniert, versuche die externe Webcam
        if not use_integrated:
            # Aufräumen und externe Webcam versuchen
            self.cap.release()
            print("⚠️ Versuche stattdessen die externe Webcam...")
            self.kamera_index = 1
            self.cap = cv2.VideoCapture(self.kamera_index, cv2.CAP_ANY)
        
        # Setze Kamera-Parameter für bessere Leistung
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not self.cap.isOpened():
            print("⚠️ Fehler: Keine Kamera konnte geöffnet werden!")
        else:
            # Überprüfe nochmals, ob Frames gelesen werden können
            ret, frame = self.cap.read()
            if not ret:
                print(f"⚠️ Kamera {self.kamera_index} liefert keine Bilder!")
            else:
                print(f"✅ Kamera mit Index {self.kamera_index} erfolgreich initialisiert und liefert Bilder.")

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

        self.status = 0  # 0 = Kein Gesicht erkannt, 1 = Gesicht erkannt

    def update_frame(self):
        ret, frame = self.cap.read()
        
        # Wenn kein Frame gelesen werden konnte, versuche die Kamera neu zu öffnen
        if not ret:
            print(f"❌ Kein Kamerabild erhalten von Kamera {self.kamera_index}.")
            
            # Zähle fehlgeschlagene Versuche
            if not hasattr(self, 'retry_count'):
                self.retry_count = 0
            
            self.retry_count += 1
            
            # Nach 5 Fehlversuchen versuche die Kamera neu zu initialisieren
            if self.retry_count >= 5:
                print(f"🔄 Versuche Kamera {self.kamera_index} neu zu initialisieren...")
                self.retry_count = 0
                
                # Aufräumen und neu öffnen
                self.cap.release()
                self.cap = cv2.VideoCapture(self.kamera_index, cv2.CAP_ANY)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                
                # Erneut versuchen, einen Frame zu lesen
                ret, frame = self.cap.read()
                if not ret:
                    # Wenn immer noch kein Frame, versuche die andere Kamera
                    # Wenn wir aktuell die integrierte Kamera verwenden, wechsle zur externen
                    if self.kamera_index == 0:
                        alt_index = 1
                        print(f"🔄 Integrierte Kamera funktioniert nicht. Versuche externe Webcam (Index {alt_index})...")
                    # Wenn wir aktuell die externe Webcam verwenden, gehe zurück zur integrierten
                    else:
                        alt_index = 0
                        print(f"🔄 Externe Webcam funktioniert nicht. Versuche erneut integrierte Kamera (Index {alt_index})...")
                    
                    self.cap.release()
                    self.kamera_index = alt_index
                    self.cap = cv2.VideoCapture(self.kamera_index, cv2.CAP_ANY)
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    
                    ret, frame = self.cap.read()
                    if not ret:
                        return  # Wenn immer noch kein Frame, abbrechen
            else:
                return  # Bei normalem Fehler einfach abbrechen
        else:
            # Reset retry counter on successful frame capture
            if hasattr(self, 'retry_count'):
                self.retry_count = 0
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(frame_rgb)

        face_detected = False

        if results.detections:
            for detection in results.detections:
                confidence = detection.score[0]
                if confidence >= 0.5:
                    face_detected = True
                    self.last_face_detected_time = time.time()
                    self.no_face_logged = False

                    if self.face_was_missing:
                        self.status = 1  # Status auf 1 setzen
                        self.status_changed.emit(self.status)  # ✅ Signal senden
                        #print(f"✅ Face detected | Status: {self.status}")
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
                self.status = 0  # Status auf 0 setzen
                self.status_changed.emit(self.status)  # ✅ Signal senden
                #print(f"❌ No face detected | Status: {self.status}")
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
