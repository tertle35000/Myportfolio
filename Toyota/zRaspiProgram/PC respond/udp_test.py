import socket
import json
import time

# --- การตั้งค่า ---
SERVER_HOST = "10.234.198.245" 
SERVER_PORT = 6201 

# --- ข้อมูล JSON ที่จะส่ง (กำหนด sender_address เอง) ---
JSON_DATA = {
	"running_id": "ABCDEFGH",
	"send_datetime" : "2025-11-27 09:30:xxxx",
	"sender_ip": "10.234.198.111",
    "sender_port": "8001",
    "command": "url",
    "arguments": "https://gemini.google.com/app/ec9d1993231c11a2",
    "duration_seconds": None
}

# --- ฟังก์ชันส่ง UDP (ไม่มีการรอรับ Response) ---

def send_udp_command(command_data, server_host, server_port):
    
    # ใช้ SOCK_DGRAM สำหรับ UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            # ไม่ต้อง s.bind() ทำให้ใช้งานง่ายขึ้นมาก

            json_str = json.dumps(command_data)
            message = json_str.encode("utf-8")
            
            # 1. ส่งข้อมูล
            s.sendto(message, (server_host, server_port))
            
            print(f"[SENT] Command: {command_data.get('command')} sent to {server_host}:{server_port}")
            print(f"       Told Server to respond to: {command_data.get('sender_address')}")

        except Exception as e:
            print(f"[ERROR] UDP send failed: {e}")


# --- การเรียกใช้งาน ---

if __name__ == "__main__":
    
    send_udp_command(JSON_DATA, SERVER_HOST, SERVER_PORT)