import cv2
import numpy as np
import os
import time
from pyzbar import pyzbar  # <- สำหรับสแกน QR/Barcode
from DatabaseConnector import DatabaseConnector
from CSConnector import ColorSender
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ---------------- Database & Sender ----------------
db = DatabaseConnector(
    server="localhost\\SQLEXPRESS",
    database="CSI-Inspection",
    username="sa",
    password="P@ssw0rd"
)
db.connect()

sender = ColorSender()
sender.connect()

# ---------------- Detect Color ----------------
def detect_color(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red1, upper_red1 = np.array([0,100,100]), np.array([10,255,255])
    lower_red2, upper_red2 = np.array([160,100,100]), np.array([179,255,255])
    mask_red = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

    lower_green, upper_green = np.array([40,50,50]), np.array([80,255,255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    lower_orange, upper_orange = np.array([10,100,100]), np.array([20,255,255])
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)

    lower_yellow, upper_yellow = np.array([20,100,100]), np.array([30,255,255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    colors = {
        "Red": cv2.countNonZero(mask_red),
        "Green": cv2.countNonZero(mask_green),
        "Orange": cv2.countNonZero(mask_orange),
        "Yellow": cv2.countNonZero(mask_yellow),
    }

    return max(colors, key=colors.get)

def detect_qrcode(img):
    decoded_objects = pyzbar.decode(img)
    results = {"QRdata": [], "Bardata": []}
    for obj in decoded_objects:
        code_type = obj.type
        code_data = obj.data.decode("utf-8")

        if code_type == "QRCODE":
            results["QRdata"].append(code_data)
        else:  # ถือว่าเป็น Barcode ประเภทอื่น
            results["Bardata"].append(code_data)

    return results

class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith((".jpg", ".png", ".jpeg")):
            img_path = event.src_path
            filename = os.path.basename(img_path)

            # รอจนกว่าไฟล์จะพร้อม (ลองใหม่สูงสุด 10 ครั้ง)
            img = None
            for i in range(10):
                img = cv2.imread(img_path)
                if img is not None:
                    break
                time.sleep(0.5)  # หน่วง 0.5 วิ แล้วลองใหม่

            if img is None:
                print("ไม่พบไฟล์ภาพ หรือไฟล์ยังไม่พร้อม:", img_path)
                return

            # ตรวจจับสี
            color = detect_color(img)

            # ตรวจจับ QR/Barcode
            qr_results = detect_qrcode(img)
            qr_text = ", ".join(qr_results["QRdata"]) if qr_results["QRdata"] else "None"
            bar_text = ", ".join(qr_results["Bardata"]) if qr_results["Bardata"] else "None"

            print(f"{filename}: \nColor={color}, QRdata={qr_text}, Bardata={bar_text}")

            sender.send_data(color, qr_results["QRdata"], qr_results["Bardata"])
            db.insert_detection(color, qr_results["QRdata"], qr_results["Bardata"])


folder_path = r"D:\Picture\AIPicture"
event_handler = ImageHandler()
observer = Observer()
observer.schedule(event_handler, folder_path, recursive=False)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()
