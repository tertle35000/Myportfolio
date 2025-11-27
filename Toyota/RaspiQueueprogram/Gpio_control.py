import time
import RPi.GPIO as GPIO
import json
import os

# GPIO setup
GPIO.setmode(GPIO.BCM)
pins = [17, 18, 27, 22, 23, 24]  # ใช้ 6 ขา
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

CONFIG_FILE = "sound_config.txt"

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
        print("[ERROR] Invalid JSON in sound_config.txt")
        return []

def save_queue(queue):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

def apply_gpio(parameter):
    """ ปล่อย GPIO ตาม bitmask ของ parameter """
    bitmask = [int(x) for x in f"{parameter:06b}"[::-1]]  # bit 0 = pins[0]
    for i, pin in enumerate(pins):
        if i < len(bitmask):
            GPIO.output(pin, GPIO.HIGH if bitmask[i] else GPIO.LOW)
        else:
            GPIO.output(pin, GPIO.LOW)

try:
    while True:
        queue = load_queue()
        if not queue:
            time.sleep(0.2)
            continue

        current = queue[0]
        param = current.get("parameter")
        duration = current.get("duration_seconds")

        # ตรวจสอบ parameter เกินขอบเขต
        if param is None:
            param = 0
        if not isinstance(param, int):
            try:
                param = int(param)
            except:
                param = 0

        if param > 63:
            print(f"[ERROR] Parameter {param} exceeds 63. Removing from queue.")
            queue.pop(0)
            save_queue(queue)
            continue

        apply_gpio(param)

        # duration
        if duration in (None, 0):
            # ปล่อยค้าง จนกว่าจะมีการลบไฟล์/คิว
            while True:
                queue = load_queue()
                if not queue or queue[0] != current:
                    break
                time.sleep(0.2)
        else:
            # ปล่อย duration_seconds แล้วลบคิว
            time.sleep(duration)
            queue = load_queue()
            if queue and queue[0] == current:
                queue.pop(0)
                save_queue(queue)

except KeyboardInterrupt:
    print("Exit GPIO loop")
finally:
    # ปิด GPIO ทุกขา
    for pin in pins:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()
