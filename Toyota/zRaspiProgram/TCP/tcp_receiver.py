import socket
import json
import threading
import queue
import os
import sys

# --- การตั้งค่า ---
HOST = "0.0.0.0"
PORT = 6200 # ตั้งค่าพอร์ตสำหรับ TCP Receiver

# คิวสำหรับเก็บข้อมูล JSON เพื่อนำไปประมวลผลในเธรดอื่น
json_queue = queue.Queue() 

# --- ฟังก์ชันจัดการไฟล์ ---

def save_single_json_to_file(filename, data):
    """บันทึก JSON Object เดี่ยวลงในไฟล์ โดยอยู่ในรูปแบบ List"""
    try:
        # ลบข้อมูลที่ใช้ในการสื่อสารออกไปก่อนบันทึก (ถ้ามี)
        data_to_save = data.copy()
        data_to_save.pop("status", None)
        
        with open(filename, "w", encoding="utf-8") as f:
            # บันทึกเป็น List ที่มี Object เดียว
            json.dump([data_to_save], f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"[ERROR] Cannot save file {filename}: {e}")

# --- ฟังก์ชันประมวลผลข้อมูลในเธรดแยก ---

def process_json():
    """ดึงข้อมูลจากคิวและประมวลผลตามคำสั่ง (เขียนไฟล์เท่านั้น)"""
    print("[INFO] JSON Processor Thread started.")
    while True:
        data = None
        try:
            data = json_queue.get() # รอข้อมูล
            cmd = data.get("command", "").strip().lower()
            
            # ดึงค่า Parameter/Arguments
            param_value = data.get('arguments')
            if param_value is None:
                 param_value = data.get('parameter')

            # --- ส่วนการเขียนไฟล์ตามคำสั่ง ---
            if cmd == "sound":
                save_single_json_to_file("sound_config.txt", data)
                print(f"[OVERWRITE] sound_config.txt with command: {param_value}")

            elif cmd == "display":
                save_single_json_to_file("tv_config.txt", data)
                print(f"[OVERWRITE] tv_config.txt with command: {param_value}")

            elif cmd == "url":
                save_single_json_to_file("url_config.txt", data)
                print(f"[OVERWRITE] url_config.txt with command: {param_value}")

            else:
                print(f"[WARNING] Unknown command: {cmd}. Data discarded.")
            # --------------------------------

            json_queue.task_done()
        
        except Exception as e:
            print(f"[FATAL ERROR] in process_json thread: {e}", file=sys.stderr)
            if data is not None:
                json_queue.task_done()

# --- ฟังก์ชันจัดการ Client (TCP) ---

def handle_tcp_client(conn, addr):
    """จัดการการเชื่อมต่อ TCP: รับข้อมูล, แยก JSON, และส่งเข้าคิว"""
    print(f"[TCP] Connected by {addr}")
    buffer = ""
    try:
        while True:
            # รับข้อมูล (Blocking call)
            data = conn.recv(1024) 
            if not data:
                break

            buffer += data.decode("utf-8")

            # แยก JSON ทีละก้อน (เผื่อกรณีได้รับหลาย Object ในครั้งเดียว)
            while True:
                start = buffer.find("{")
                end = buffer.find("}", start + 1)
                if start != -1 and end != -1:
                    raw_json = buffer[start:end + 1]
                    buffer = buffer[end + 1:]
                    try:
                        obj = json.loads(raw_json)
                        
                        # ส่งเข้าคิวเพื่อประมวลผลการเขียนไฟล์
                        json_queue.put(obj)
                        print(f"[TCP] JSON received from {addr}")
                    except json.JSONDecodeError:
                        print(f"[TCP WARNING] Invalid JSON skipped from {addr}: {raw_json[:50]}...")
                else:
                    break
    except Exception as e:
        print(f"[TCP ERROR] Error with {addr}: {e}")
    finally:
        conn.close()
        print(f"[TCP] Disconnected from {addr}")

# --- ฟังก์ชันเริ่มต้น TCP Server หลัก ---

def start_tcp_server():
    """ตั้งค่าและเริ่มรับการเชื่อมต่อ TCP"""
    try:
        # ใช้ SOCK_STREAM สำหรับ TCP
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: 
            s.bind((HOST, PORT))
            s.listen()
            print(f"[TCP] Server started on {HOST}:{PORT}")
            while True:
                # รอรับการเชื่อมต่อใหม่
                conn, addr = s.accept()
                # เริ่มเธรดสำหรับจัดการไคลเอนต์แต่ละราย
                threading.Thread(target=handle_tcp_client, args=(conn, addr), daemon=True).start()
    except OSError as e:
        print(f"[FATAL ERROR] Cannot bind TCP to {HOST}:{PORT}. {e}", file=sys.stderr)

# --- การรันโปรแกรมหลัก ---

if __name__ == "__main__":
    # เริ่มเธรดสำหรับรับข้อมูล TCP
    threading.Thread(target=start_tcp_server, daemon=True).start() 
    
    # รันเธรดประมวลผล JSON ในเธรดหลัก
    process_json()