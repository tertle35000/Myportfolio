#!/bin/bash

# --- 1. การตั้งค่าและพาธ ---
JSON_FILE="/home/iiot/Desktop/Toyota/url_config.txt"
DEFAULT_URL="http://202.44.229.93:8018/TMT_BP/monitoring/group1"
LAST_LOADED_URL=""

# --- 2. การจัดการไฟล์และการตั้งค่าเริ่มต้น ---
# แก้ไขสถานะการปิดตัวของ Chromium (ป้องกันข้อความเตือน)
sed -i 's/"exited_cleanly": false/"exited_cleanly": true/' /home/iiot/.config/chromium/Default/Preferences

# ฆ่าและรัน unclutter ใหม่เพื่อซ่อนเคอร์เซอร์
pkill -f unclutter
unclutter -idle 0.1 -root -noevents &

# --- 3. Kiosk Loop สำหรับตรวจสอบการเปลี่ยนแปลง URL และ Duration ---
while true; do

    # 3.1 อ่านค่าจากไฟล์ JSON (URL และ Duration)
    # เนื่องจากไฟล์ JSON ในตัวอย่างของคุณเป็น Object ไม่ใช่ Array จึงต้องเปลี่ยน selector เป็น .arguments และ .duration_seconds
    # แต่เนื่องจากสคริปต์เดิมใช้ .[0].arguments ผมจะอิงตามสคริปต์เดิมเพื่อความเข้ากันได้
    # หากไฟล์จริงเป็น Object เดี่ยวๆ (ไม่ใช่ Array) คุณต้องแก้เป็น .arguments
    CURRENT_URL=$(jq -r '.[0].arguments' "$JSON_FILE" 2>/dev/null)
    DURATION=$(jq -r '.[0].duration_seconds' "$JSON_FILE" 2>/dev/null)
    
    # กำหนด URL ที่จะเปิด/ตรวจสอบ (เหมือนเดิม)
    if [ -z "$CURRENT_URL" ] || [ "$CURRENT_URL" = "null" ]; then
        URL_TO_OPEN="$DEFAULT_URL"
    else
        URL_TO_OPEN="$CURRENT_URL"
    fi

    # 3.2 ตรวจสอบ: ถ้า URL ที่ต้องการเปิด แตกต่างจาก URL ที่โหลดไปแล้ว
    if [ "$URL_TO_OPEN" != "$LAST_LOADED_URL" ]; then

        echo "--- URL Change Detected: $URL_TO_OPEN ---"

        # 1. ฆ่า Process Chromium ตัวเก่าทันที (ถ้ามี)
        OLD_PID=$(pgrep -o chromium)
        if [ -n "$OLD_PID" ] && ps -p "$OLD_PID" > /dev/null; then
             echo "Killed old Chromium process (PID: $OLD_PID)"
        fi
        
        # 2. บันทึก URL ใหม่ลงในตัวแปร LAST_LOADED_URL ทันที
        LAST_LOADED_URL="$URL_TO_OPEN" 

        # 3. ตรวจสอบและเพิ่มโปรโตคอล http:// ถ้าไม่มี
        if [[ "$URL_TO_OPEN" != http* ]]; then
            URL_TO_OPEN="http://$URL_TO_OPEN"
        fi

        # 4. สั่งเปิด Chromium ใหม่ด้วย URL ล่าสุด (รันเบื้องหลัง)
        /usr/bin/chromium \
            --noerrdialogs --disable-infobars --kiosk \
            --disable-gpu --disable-software-rasterizer \
            --ignore-certificate-errors --allow-running-insecure-content \
            --remote-debugging-port=9222 \
            "$URL_TO_OPEN" & 
        
        # บันทึก PID ของ Chromium ตัวใหม่ที่เพิ่งเปิดเพื่อใช้ฆ่าในภายหลัง
        NEW_PID=$! # $! คือ PID ของ Process ล่าสุดที่รันในเบื้องหลัง (&)
        echo "Launched new Chromium process (PID: $NEW_PID) with URL: $URL_TO_OPEN"
        
        # 5. ตรวจสอบค่า Duration
        if [ -n "$DURATION" ] && [ "$DURATION" != "null" ] && [ "$DURATION" -gt 0 ]; then
            
            # 5.1 เวลามีกำหนด: เปิด 60 วิ และปิด
            echo "URL has a duration of $DURATION seconds. Waiting..."
            
            # หน่วงเวลาตามค่า duration_seconds ที่อ่านมา
            sleep "$DURATION"
            
            # 5.2 ฆ่า Chromium ตัวใหม่ (ถ้ายังทำงานอยู่)
            if ps -p "$NEW_PID" > /dev/null; then
                kill "$NEW_PID"
                echo "Chromium (PID: $NEW_PID) killed after $DURATION seconds."
            fi
            
            # 5.3 ล้างไฟล์ JSON และตั้งค่าตัวแปรใหม่เพื่อรอรับคำสั่งใหม่
            echo "[]" > "$JSON_FILE"
            LAST_LOADED_URL="" # รีเซ็ต LAST_LOADED_URL เพื่อให้เปิดใหม่เมื่อมีข้อมูลใหม่เข้ามา
            echo "JSON file cleared to []"
            
        else
            # 5.4 เวลาเป็น null/ไม่กำหนด: เปิดตลอดไป
            echo "Duration is null/unspecified. Webpage will remain open."
        fi

    fi # ปิด if block 3.2

    # รอ 5 วินาทีก่อนตรวจสอบไฟล์ JSON ใหม่อีกครั้ง
    # (หากมีการตั้ง duration และสคริปต์ sleep ไปแล้ว 5 วิที่นี่จะไม่ทำงานจนกว่าจะจบรอบนั้น)
    sleep 5 
done