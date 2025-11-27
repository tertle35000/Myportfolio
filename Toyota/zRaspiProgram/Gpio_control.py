import time
import RPi.GPIO as GPIO
import json
import os

# GPIO setup
GPIO.setmode(GPIO.BCM)
pins = [4, 18, 22, 24, 17, 27, 23, 25]
for pin in pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

CONFIG_FILE = "sound_config.txt"

# --- Global State Variables ---
# ใช้สำหรับจำสถานะ Parameter ล่าสุดที่ถูกสั่งไป
LAST_APPLIED_PARAM = -1 
# เวลาที่คำสั่งปัจจุบันจะหมดอายุ (0 หมายถึงรันค้างถาวร)
CURRENT_COMMAND_END_TIME = 0
# ค่า Parameter ของคำสั่งปัจจุบันที่กำลังรันอยู่ (ใช้ในการ Reset)
CURRENT_ACTIVE_PARAM = 0

def load_first_command():
    """ โหลดเฉพาะคำสั่งแรกจากไฟล์ config และคืนค่า (command, raw_file_data) """
    if not os.path.exists(CONFIG_FILE):
        return None, None
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            if not data:
                return None, None
            
            queue = json.loads(data)
            return queue[0] if queue else None, data
            
    except json.JSONDecodeError:
        print("[ERROR] Invalid JSON in sound_config.txt. Skipping current read.")
        return None, None

def clear_config_file():
    """ ล้างข้อมูลในไฟล์ config ทั้งหมด (เพื่อ Reset สถานะ) """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write("[]") # เขียน List ว่าง
        print(f"[FILE] Configuration file cleared: {CONFIG_FILE}.")
    except Exception as e:
        print(f"[ERROR] Failed to clear config file: {e}")

def apply_gpio(parameter):
    """ ปล่อย GPIO ตาม bitmask ของ parameter """
    bitmask = [int(x) for x in f"{parameter:06b}"[::-1]]
    for i, pin in enumerate(pins):
        if i < len(bitmask):
            GPIO.output(pin, GPIO.HIGH if bitmask[i] else GPIO.LOW)
        else:
            GPIO.output(pin, GPIO.LOW)

try:
    while True:
        # 1. โหลดข้อมูลทุกรอบเพื่อรองรับการ Override ทันที
        current_command, raw_file_data = load_first_command()
        param = 0 # กำหนดค่า default เป็น 0 (Idle)
        duration = None

        # 2. ตรวจสอบว่าคำสั่งปัจจุบันหมดเวลาแล้วหรือไม่
        if CURRENT_COMMAND_END_TIME != 0 and time.time() >= CURRENT_COMMAND_END_TIME:
            print(f"[GPIO] Duration elapsed for command: {CURRENT_ACTIVE_PARAM}. Resetting.")
            
            # สั่ง Reset GPIO (0) และล้างไฟล์
            apply_gpio(0)
            LAST_APPLIED_PARAM = 0
            CURRENT_COMMAND_END_TIME = 0
            CURRENT_ACTIVE_PARAM = 0
            clear_config_file()
            
            # รอสั้นๆ ก่อนวนลูปใหม่
            time.sleep(0.2)
            continue

        # 3. ถ้ามีคำสั่งใหม่ในไฟล์
        if current_command:
            raw_param = current_command.get("arguments")
            duration = current_command.get("duration_seconds")
            
            try:
                param = int(raw_param) if raw_param is not None else 0
            except ValueError:
                param = 0
        
        # 4. ตรวจสอบค่าสูงสุด
        if param > 63:
            print(f"[ERROR] Parameter {param} exceeds 63. Reverting to 0.")
            param = 0

        # 5. สั่ง GPIO ถ้า parameter ใหม่ต่างจากสถานะล่าสุด (OVERRIDE LOGIC)
        if param != LAST_APPLIED_PARAM:
            
            # A. สั่ง GPIO ใหม่
            apply_gpio(param)
            print(f"[GPIO] Applying command (OVERRIDE): {param}")
            LAST_APPLIED_PARAM = param 
            CURRENT_ACTIVE_PARAM = param
            
            # B. จัดการ Timer สำหรับคำสั่งใหม่
            if duration is not None and duration > 0:
                # ถ้ามี Duration ให้ตั้งเวลาสิ้นสุด
                CURRENT_COMMAND_END_TIME = time.time() + duration
                print(f"[TIMER] Set {duration}s duration for {param}. Ends at {time.ctime(CURRENT_COMMAND_END_TIME)}.")
            else:
                # ถ้าไม่มี Duration (หรือเป็น 0) ให้รันค้างถาวร
                CURRENT_COMMAND_END_TIME = 0
                print(f"[TIMER] Running {param} permanently (no duration set).")
        
        # 6. รอ 0.2 วินาที ก่อนวนซ้ำเพื่อตรวจสอบไฟล์/เวลา
        time.sleep(0.2)

except KeyboardInterrupt:
    print("Exit GPIO loop")
finally:
    # ปิด GPIO ทุกขาและล้างค่าเมื่อสคริปต์จบการทำงาน
    for pin in pins:
        GPIO.output(pin, GPIO.LOW)
    GPIO.cleanup()