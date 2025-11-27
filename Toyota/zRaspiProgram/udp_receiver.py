import socket
import json
import threading
import queue
import os
import sys

# --- การตั้งค่า ---
HOST = "0.0.0.0"
PORT = 6201

# คิวสำหรับเก็บข้อมูล JSON เพื่อนำไปประมวลผลในเธรดอื่น
json_queue = queue.Queue() 

# --- ฟังก์ชันจัดการไฟล์และส่ง UDP ---

def save_single_json_to_file(filename, data):
    """บันทึก JSON Object เดี่ยวลงในไฟล์ โดยอยู่ในรูปแบบ List"""
    # ข้อมูลที่บันทึกจะต้องเป็น List ที่มี Object เดียว
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump([data], f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"[ERROR] Cannot save file {filename}: {e}")

def send_udp_response(data):  
    ip = data.get("sender_ip", "")
    port_str = data.get("sender_port")

    # ถ้าหา IP/Port จากคีย์ใหม่ไม่ได้ ให้ลองหาจากคีย์เก่า
    if not ip or not port_str:
        sender_addr = data.get("sender_address", "")
        try:
            ip, port_str = sender_addr.split(":")
        except ValueError:
            print(f"[ERROR] Invalid or missing address info in data: {data}")
            return

    # พยายามแปลง Port เป็นตัวเลข
    try:
        port = int(port_str)
    except (ValueError, TypeError):
        print(f"[ERROR] Invalid sender port: {port_str}")
        return

    # เตรียมข้อความตอบกลับ (ดึงค่าจาก 'arguments' หรือ 'parameter')
    response_message = {
        "running_id": data.get("running_id"),
        "command": data.get("command"),
        "send_datetime": data.get("send_datetime"),
        # ใช้ 'arguments' ก่อน หากไม่มีจึงใช้ 'parameter'
        "parameter": data.get("arguments") if data.get("arguments") is not None else data.get("parameter"), 
        "duration_seconds": data.get("duration_seconds"),
        "status": data.get("status", "processed")
    }

    json_str = json.dumps(response_message, ensure_ascii=False)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

    try:
        sock.sendto(json_str.encode("utf-8"), (ip, port))
        print(f"[SENT] UDP Response → {ip}:{port}")
    except Exception as e:
        print(f"[ERROR] UDP send failed to {ip}:{port}: {e}")
    finally:
        sock.close()

# --- ฟังก์ชันประมวลผลข้อมูลในเธรดแยก ---

def process_json():
    """ดึงข้อมูลจากคิวและประมวลผลตามคำสั่ง"""
    print("[INFO] JSON Processor Thread started.")
    while True:
        data = None
        try:
            data = json_queue.get(timeout=1) # รอข้อมูล
            cmd = data.get("command", "").strip().lower()
            
            # ดึงค่า Parameter/Arguments
            param_value = data.get('arguments')
            if param_value is None:
                 param_value = data.get('parameter')

            if cmd == "sound":
                save_single_json_to_file("sound_config.txt", data)
                print(f"[OVERWRITE] sound_config.txt with command: {param_value}")
                data["status"] = "success"

            elif cmd == "display":
                save_single_json_to_file("tv_config.txt", data)
                print(f"[OVERWRITE] tv_config.txt with command: {param_value}")
                data["status"] = "success"

            elif cmd == "url":
                save_single_json_to_file("url_config.txt", data)
                print(f"[OVERWRITE] url_config.txt with command: {param_value}")
                data["status"] = "success"

            else:
                print("[WARNING] Unknown command:", cmd)
                data["status"] = "failed: unknown command" 

            send_udp_response(data) 
            json_queue.task_done()
        
        except queue.Empty:
            continue
        
        except Exception as e:
            print(f"[FATAL ERROR] in process_json thread: {e}", file=sys.stderr)
            if data is not None:
                 # พยายามส่ง response กลับ แม้จะเกิด error ในการประมวลผล
                 error_data = {
                    "sender_ip": data.get("sender_ip"),
                    "sender_port": data.get("sender_port"),
                    "sender_address": data.get("sender_address"), # รูปแบบเดิม
                    "status": f"processing_error: {e}"
                 }
                 send_udp_response(error_data)
            json_queue.task_done() 

# --- ฟังก์ชันรับข้อมูลหลัก (UDP Receiver) ---

def start_udp_receiver():
    """ตั้งค่าและเริ่มรับแพ็กเก็ต UDP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        s.bind((HOST, PORT))
        print(f"UDP Receiver started on {HOST}:{PORT}")
    except OSError as e:
        print(f"[FATAL ERROR] Cannot bind to {HOST}:{PORT}. {e}", file=sys.stderr)
        return

    while True:
        raw_json = ""
        try:
            # รับข้อมูลและที่อยู่ของผู้ส่ง (addr)
            data, addr = s.recvfrom(1024) 
            raw_json = data.decode("utf-8").strip()
            
            # โหลดข้อมูล JSON
            obj = json.loads(raw_json) 

            if not isinstance(obj, dict):
                print(f"[WARNING] Data is not a JSON object from {addr}: {raw_json[:30]}...")
                continue 

            # *** การตั้งค่า IP/Port สำหรับการตอบกลับ (สำคัญมากสำหรับ UDP) ***
            
            # ถ้า JSON ใหม่ไม่ได้ระบุ 'sender_ip' หรือ 'sender_port'
            if not obj.get("sender_ip") or not obj.get("sender_port"):
                # ใช้ IP และ Port จริงที่รับมา (addr) เป็นค่าเริ่มต้น
                obj["sender_ip"] = addr[0]
                obj["sender_port"] = str(addr[1])
                print(f"[RECV] JSON from {addr}. Auto-set sender_ip/port to {addr[0]}:{addr[1]}")
            else:
                # ใช้ค่าที่ระบุใน JSON ใหม่
                print(f"[RECV] JSON from {addr}. Using sender_ip/port: {obj['sender_ip']}:{obj['sender_port']}")

            json_queue.put(obj) 

        except json.JSONDecodeError:
            print(f"[ERROR] Invalid JSON from {addr}: {raw_json}")
        except Exception as e:
            # ต้องมั่นใจว่ามีการกำหนดค่า addr ก่อนจะใช้
            sender_info = f"{addr[0]}:{addr[1]}" if 'addr' in locals() else "Unknown Address"
            print(f"[ERROR] Processing UDP data from {sender_info}: {e}")

# --- การรันโปรแกรมหลัก ---

if __name__ == "__main__":
    # เริ่มเธรดสำหรับรับข้อมูล UDP
    udp_thread = threading.Thread(target=start_udp_receiver, daemon=True)
    udp_thread.start() 
    
    # รันเธรดประมวลผล JSON ในเธรดหลัก
    process_json()