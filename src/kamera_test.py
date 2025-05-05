import cv2
import time

def list_kameras():
    """Listet alle verfügbaren Kameras auf, die OpenCV erkennen kann"""
    print("Suche nach verfügbaren Kameras...")
    
    # Versuchen, verschiedene Kamera-Indizes zu öffnen
    index = 0
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            break
            
        # Versuche, Kamera-Eigenschaften zu lesen
        vendor = cap.get(cv2.CAP_PROP_BACKEND)
        
        print(f"Kamera {index} gefunden:")
        print(f"  - Backend: {vendor}")
        
        # Frame-Größe lesen
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        print(f"  - Auflösung: {width}x{height}")
        
        # Testframe lesen
        ret, frame = cap.read()
        if ret:
            print(f"  - Erfolgreich Frame gelesen: {frame.shape}")
        else:
            print(f"  - Konnte keinen Frame lesen")
            
        cap.release()
        index += 1
    
    if index == 0:
        print("Keine Kameras gefunden!")
    else:
        print(f"{index} Kamera(s) gefunden.")
    
    return index

def test_kamera(kamera_index=0):  # Standardmäßig die integrierte Kamera (Index 0) verwenden
    print(f"Kamera-Test wird gestartet für Kamera-Index {kamera_index}...")
    
    # Kamera öffnen
    cap = cv2.VideoCapture(kamera_index)
    
    # Prüfen, ob die Kamera erfolgreich geöffnet wurde
    if not cap.isOpened():
        print(f"❌ Fehler: Konnte Kamera mit Index {kamera_index} nicht öffnen!")
        return
    
    print(f"✅ Kamera mit Index {kamera_index} erfolgreich geöffnet!")
    
    # Einige Frames erfassen und anzeigen
    for i in range(100):  # 100 Frames oder ca. 10 Sekunden
        # Frame von der Kamera lesen
        ret, frame = cap.read()
        
        # Prüfen, ob Frame erfolgreich gelesen wurde
        if not ret:
            print("❌ Fehler: Konnte keinen Frame von der Kamera lesen!")
            break
        
        # Frame anzeigen
        cv2.imshow(f"Kamera-Test (Index {kamera_index})", frame)
        
        # Zum Beenden 'q' drücken
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
        
        time.sleep(0.1)  # Kurze Pause zwischen den Frames
    
    # Aufräumen
    cap.release()
    cv2.destroyAllWindows()
    print("Kamera-Test abgeschlossen.")

def test_kamera_mit_fallback():
    """Testet zuerst die integrierte Kamera, fällt bei Bedarf auf externe zurück"""
    anzahl_kameras = list_kameras()
    
    if anzahl_kameras == 0:
        print("Keine Kameras gefunden. Test kann nicht durchgeführt werden.")
        return
    
    # Versuche zuerst die integrierte Kamera (Index 0)
    print("\nVersuche zuerst die integrierte Kamera (Index 0)...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Integrierte Kamera konnte nicht geöffnet werden.")
        use_integrated = False
    else:
        # Teste, ob tatsächlich ein Frame gelesen werden kann
        ret, frame = cap.read()
        if not ret:
            print("❌ Integrierte Kamera konnte geöffnet werden, aber liefert keine Bilder.")
            use_integrated = False
        else:
            print("✅ Integrierte Kamera funktioniert vollständig!")
            use_integrated = True
    
    cap.release()
    
    # Wähle die passende Kamera
    if not use_integrated:
        # Falls es eine externe Kamera gibt, versuche diese
        if anzahl_kameras > 1:
            print("Versuche stattdessen externe Webcam (Index 1)...")
            test_kamera(1)
        else:
            print("Keine alternative Kamera verfügbar.")
    else:
        # Integrierte Kamera funktioniert, verwende sie
        test_kamera(0)

if __name__ == "__main__":
    # Verwende die neue Funktion mit Fallback-Logik
    test_kamera_mit_fallback()