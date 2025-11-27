import os
import json
import time
import os.path

CONFIG_FILE = "tv_config.txt"

def load_queue():
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON in tv_config.txt")
        return []

def save_queue(queue):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

def control_tv(action):
    if action:  # เปิด
        os.system("echo 'on 0' | cec-client -s -d 1")
        print("[TV] Turned ON")
    else:       # ปิด / standby
        os.system("echo 'standby 0' | cec-client -s -d 1")
        print("[TV] Turned OFF / Standby")

def normalize_parameter(param):
    if param in (None, 0, "0", "00"):
        return 0
    elif param in (1, "1", "01"):
        return 1
    else:
        return None

# จำค่าพื้นฐาน TV ปัจจุบัน
current_state = 0  # 0 = standby, 1 = on

try:
    while True:
        queue = load_queue()
        if not queue:
            time.sleep(0.2)
            continue

        current = queue[0]
        param = current.get("parameter")
        duration = current.get("duration_seconds")

        action = normalize_parameter(param)
        if action is None:
            print(f"[ERROR] Invalid parameter {param}, removing from queue")
            queue.pop(0)
            save_queue(queue)
            continue

        # สั่ง TV ตาม parameter
        control_tv(action)

        # duration
        if duration in (None, 0):
            # ปล่อยค้างจนกว่าจะมีการลบคิว
            while True:
                queue = load_queue()
                if not queue or queue[0] != current:
                    break
                time.sleep(0.2)
        else:
            time.sleep(duration)
            # กลับไปโหมดเดิม
            control_tv(current_state)
            queue = load_queue()
            if queue and queue[0] == current:
                queue.pop(0)
                save_queue(queue)

except KeyboardInterrupt:
    print("Exit TV control loop")
    control_tv(current_state)
