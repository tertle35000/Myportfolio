import socket
import json
import threading
import queue
import os

HOST = "0.0.0.0"
PORT = 5000

json_queue = queue.Queue()

# อ่านไฟล์เก่า ถ้าไม่มีให้คืน list ว่าง
def load_json_list(filename):
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except json.JSONDecodeError:
        return []

# เขียนไฟล์ใหม่ทั้งหมด (append queue)
def append_json_to_file(filename, new_data):
    all_data = load_json_list(filename)
    all_data.append(new_data)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    buffer = ""
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            buffer += data.decode("utf-8")

            # แยก JSON ทีละก้อน (ตามเครื่องหมาย { ... })
            while True:
                start = buffer.find("{")
                end = buffer.find("}", start + 1)
                if start != -1 and end != -1:
                    raw_json = buffer[start:end + 1]
                    buffer = buffer[end + 1:]
                    try:
                        obj = json.loads(raw_json)
                        json_queue.put(obj)
                    except json.JSONDecodeError:
                        print("Invalid JSON skipped:", raw_json)
                else:
                    break
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
        print(f"Disconnected from {addr}")

def process_json():
    while True:
        data = json_queue.get()
        cmd = data.get("command", "").strip().lower()

        if cmd == "sound":
            append_json_to_file("sound_config.txt", data)
            print("[APPEND] sound_config.txt")

        elif cmd == "display":
            append_json_to_file("tv_config.txt", data)
            print("[APPEND] tv_config.txt")

        else:
            print("[WARNING] Unknown command:", cmd)

        json_queue.task_done()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"TCP Receiver started on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    process_json()
