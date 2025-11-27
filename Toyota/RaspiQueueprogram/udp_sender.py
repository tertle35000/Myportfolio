import socket
import json

def send_udp_response(data):
    """
    data: dict ที่มี sender_address, message_code, command, parameter, duration_seconds
    """
    sender_addr = data.get("sender_address", "")
    try:
        ip, port = sender_addr.split(":")
        port = int(port)
    except ValueError:
        print(f"[ERROR] Invalid sender_address: {sender_addr}")
        return

    message = {
        "message_code": data.get("message_code"),
        "command": data.get("command"),
        "parameter": data.get("parameter"),
        "duration_seconds": data.get("duration_seconds")
    }

    # แปลงเป็น JSON แล้วส่งออก
    json_str = json.dumps(message)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.sendto(json_str.encode("utf-8"), (ip, port))
        print(f"[SENT] UDP → {ip}:{port}")
        print(json.dumps(message, indent=4))
    except Exception as e:
        print(f"[ERROR] UDP send failed: {e}")
    finally:
        sock.close()


# ตัวอย่างการทดสอบ (ลบออกได้เมื่อใช้งานจริง)
if __name__ == "__main__":
    sample_data = {
        "sender_address": "192.168.1.100:1234",
        "message_code": "a34fgasdf",
        "command": "Sound",
        "parameter": 1,
        "duration_seconds": 10
    }

    send_udp_response(sample_data)
