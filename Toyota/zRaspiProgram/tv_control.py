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
    # ฟังก์ชันนี้ใช้สำหรับเขียนไฟล์กลับหลังจากลบคำสั่งแล้ว
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=4, ensure_ascii=False)

def control_tv(action):

    if action:  # เปิด (1)
        os.system("echo 'on 0' | cec-client -s -d 1") 
        print("[TV] Turned ON (Action: 1)")
    else:       # ปิด / standby (0)
        os.system("echo 'standby 0' | cec-client -s -d 1")
        print("[TV] Turned OFF / Standby (Action: 0)")

def normalize_parameter(param):
    if param in (None, 0, "0", "00"):
        return 0
    elif param in (1, "1", "01"):
        return 1
    else:
        return None

try:
    while True:
        queue = load_queue()
        
        # 1. ถ้าไม่มีคำสั่ง: สั่ง Standby (0) และรอสั้นๆ
        if not queue:
            control_tv(0) 
            time.sleep(0.2)
            continue

        current_command = queue[0]
        param = current_command.get("arguments")
        duration = current_command.get("duration_seconds")
        # ใช้ message_code เป็น ID สำหรับเปรียบเทียบในระหว่างรอ
        current_id = current_command.get("message_code")
        
        action = normalize_parameter(param)
        
        # 2. จัดการคำสั่งที่ไม่ถูกต้อง
        if action is None:
            print(f"[ERROR] Invalid parameter {param}, removing from queue")
            queue.pop(0) 
            save_queue(queue)
            continue

        # 3. สั่ง TV ตาม parameter (เปิด/ปิด) ทันที
        control_tv(action)

        # 4. จัดการ Duration และการตรวจสอบ Interrupt
        if duration is not None and duration > 0:
            
            start_time = time.time()
            end_time = start_time + duration
            print(f"[TV] Duration {duration}s set. Waiting for interrupt or completion...")
            
            # วนซ้ำเพื่อรอและตรวจสอบการถูก Interrupt
            while time.time() < end_time:
                time.sleep(0.2) # หน่วงเวลาสั้นๆ เพื่อให้ CPU ว่าง
                
                # โหลดคิวมาตรวจสอบใหม่
                new_queue = load_queue() 

                is_interrupted = False
                
                if not new_queue:
                    # Case 1: ไฟล์ว่างเปล่า
                    is_interrupted = True
                else:
                    new_command = new_queue[0]
                    new_id = new_command.get("message_code")
                    new_action = normalize_parameter(new_command.get("arguments"))
                    
                    # Case 2: message_code เปลี่ยน (คำสั่งใหม่แน่นอน)
                    if new_id != current_id:
                        is_interrupted = True
                    # Case 3: message_code เหมือนเดิม แต่ Action (parameter) เปลี่ยน (Interrupt)
                    elif new_action != action: 
                        is_interrupted = True
                        
                if is_interrupted:
                    print(f"[INTERRUPT] Command was overridden or removed. Skipping remainder of duration.")
                    break 
            
            # เมื่อหลุดจากลูปการรอ:
            
            # A. ถ้าหลุดเพราะถูก Interrupt: (ตรวจสอบอีกครั้งว่าหลุดเพราะ Interrupt หรือเวลาหมด)
            new_queue = load_queue() # โหลดซ้ำเพื่อยืนยันสถานะล่าสุด
            
            is_interrupted = False
            if not new_queue:
                is_interrupted = True
            else:
                new_id = new_queue[0].get("message_code")
                new_action = normalize_parameter(new_queue[0].get("arguments"))
                # ตรวจสอบว่าคำสั่งใหม่มี ID หรือ Action ที่แตกต่างจากเดิมหรือไม่
                if new_id != current_id or new_action != action:
                    is_interrupted = True
            
            if is_interrupted:
                # ถ้าถูก Interrupt ให้ไปเริ่มลูป while True หลักใหม่ทันที เพื่อประมวลผลคำสั่งใหม่
                continue 

            # B. ถ้าหลุดเพราะเวลาครบ (time.time() >= end_time):
            print(f"[TV] Duration {duration}s elapsed.")
            
            # สั่งปิด/Standby (0)
            control_tv(0) 
            
            # โหลดคิวมาตรวจสอบสุดท้าย
            queue = load_queue() 
            if queue and queue[0].get("message_code") == current_id:
                # ถ้ายังเป็นคำสั่งเดิม ให้ลบออกจากไฟล์
                queue.pop(0) 
                save_queue(queue)
                print(f"[FILE] Command removed after duration from {CONFIG_FILE}.")
            
            continue 

        else:
            # 5. ถ้าไม่มี Duration หรือ Duration เป็น 0: คงสถานะไว้จนกว่าคำสั่งจะเปลี่ยน
            while True:
                queue = load_queue()
                
                is_changed = False
                if not queue:
                    is_changed = True
                else:
                    new_id = queue[0].get("message_code")
                    new_action = normalize_parameter(queue[0].get("arguments"))
                    # ตรวจสอบว่าคำสั่งใหม่มี ID หรือ Action ที่แตกต่างจากเดิมหรือไม่
                    if new_id != current_id or new_action != action:
                        is_changed = True
                        
                if is_changed:
                    break
                    
                time.sleep(0.2)
            
except KeyboardInterrupt:
    print("Exit TV control loop")
    control_tv(0)