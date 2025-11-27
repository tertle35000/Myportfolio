import socket
import json
import sys

# --- การตั้งค่าเซิร์ฟเวอร์ผู้รับ (TCP Receiver) ---
RECEIVER_HOST = "10.234.198.245"  # 💡 เปลี่ยนเป็น IP ของเครื่องที่รัน tcp_receiver.py
RECEIVER_PORT = 6200       # พอร์ตเดียวกับที่กำหนดใน tcp_receiver.py

# --- ข้อมูล JSON ที่จะส่ง ---
JSON_DATA = {
	"running_id": "ABCDEFGH",
	"send_datetime" : "2025-11-27 09:30:xxxx",
	"sender_ip": "192.168.128.90",
    "sender_port": "6201",
    "command": "Sound",
    "arguments": "0",
    "duration_seconds": None
}

def send_json_command(host, port, data):
    """ฟังก์ชันสร้างการเชื่อมต่อและส่งข้อมูล JSON"""
    try:
        # 1. สร้าง Socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            
            print(f"Connecting to {host}:{port}...")
            # 2. เชื่อมต่อไปยังเซิร์ฟเวอร์
            client_socket.connect((host, port))
            print("Connection successful.")

            # 3. แปลง Python Dictionary เป็น JSON String
            # ใช้ ensure_ascii=False เพื่อรองรับภาษาไทยหากมี
            json_string = json.dumps(data, ensure_ascii=False)
            
            # 4. เข้ารหัสเป็นไบต์และส่งข้อมูล
            message = json_string.encode('utf-8')
            client_socket.sendall(message)
            print(f"\n--- Sent Command ---")
            print(json_string)
            print("-" * 20)
            print("Data sent successfully.")

    except ConnectionRefusedError:
        print(f"[ERROR] Connection Refused. Ensure tcp_receiver.py is running on {host}:{port}.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")

if __name__ == "__main__":
    
    JSON_DATA["command"] = "url"
    JSON_DATA["arguments"] = "http://202.44.229.93:8018/TMT_BP/monitoring/group1"
    JSON_DATA["duration_seconds"] = None
    
    # ถ้า tcp_receiver.py รันอยู่บนเครื่องเดียวกัน (localhost) ใช้ค่า 127.0.0.1
    send_json_command(RECEIVER_HOST, RECEIVER_PORT, JSON_DATA)