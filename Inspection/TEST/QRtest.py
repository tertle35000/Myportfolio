import cv2
import pytesseract
from pyzbar import pyzbar
import os
import time

# ---------------- Detect QR/Barcode ----------------
def detect_qrcode(img):
    decoded_objects = pyzbar.decode(img)
    results = {"QRdata": [], "Bardata": []}
    for obj in decoded_objects:
        code_type = obj.type
        code_data = obj.data.decode("utf-8")

        if code_type == "QRCODE":
            results["QRdata"].append(code_data)
        else:
            results["Bardata"].append(code_data)

    return results

# ---------------- OCR (อ่านข้อความ) ----------------
def detect_text(img):
    # ถ้า tesseract.exe ไม่อยู่ใน PATH ให้ uncomment บรรทัดด้านล่าง
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang="eng")  # หรือ "tha+eng" ถ้ามีข้อความภาษาไทย
    return text.strip()

# ---------------- Main ----------------
if __name__ == "__main__":
    folder_path = r"D:\Picture\QRtest"

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".png", ".jpeg")):
            img_path = os.path.join(folder_path, filename)
            img = cv2.imread(img_path)
            if img is None:
                print("ไม่พบไฟล์ภาพ:", img_path)
                continue

            # ตรวจจับ QR/Barcode
            qr_results = detect_qrcode(img)
            qr_text = ", ".join(qr_results["QRdata"]) if qr_results["QRdata"] else "None"
            bar_text = ", ".join(qr_results["Bardata"]) if qr_results["Bardata"] else "None"

            # ตรวจจับข้อความ OCR
            ocr_text = detect_text(img) or "None"

            print(f"{filename}: QRdata={qr_text}, Bardata={bar_text}, OcrText={ocr_text}")

            time.sleep(1)
