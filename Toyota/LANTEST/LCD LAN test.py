import asyncio
import base64
import os
from samsungtvws import SamsungTVWS

# ****************************************************
# แก้ไขข้อมูลตรงนี้:
TV_IP_ADDRESS = "192.168.128.241"
# ****************************************************

# กำหนดค่าตัวแปร HOME ให้ตรงกับ Home Directory ใน Windows ของคุณ (เพื่อแก้ปัญหา NoneType ที่เคยเจอ)
os.environ['HOME'] = r'C:\Users\Nanawin' 


# ชื่อที่ใช้ในการเชื่อมต่อ
APP_NAME = "PythonTVController"

async def power_off_tv():
    try:
        print(f"กำลังเชื่อมต่อกับทีวีที่ IP: {TV_IP_ADDRESS}...")
        
        # 1. สร้าง Object
        tv = SamsungTVWS(
            host=TV_IP_ADDRESS, 
            port=8001,             # ลองพอร์ต 8002 เป็นอันดับแรก
            token_file="./tv-token.txt", # ไฟล์สำหรับเก็บรหัสยืนยัน (Token)
            name=APP_NAME
        )
        
        # 2. ใช้เมธอดเก่า: connect() (เพื่อให้ตรงกับเวอร์ชันไลบรารีของคุณ)
        await tv.connect()
        print("เชื่อมต่อสำเร็จ!")

        # **** สำคัญ: การอนุญาต ****
        # เมื่อรันโค้ดครั้งแรก หน้าจอทีวีจะแสดงข้อความให้ "อนุญาต"

        # 3. ส่งคำสั่งปิดเครื่อง
        print("กำลังส่งคำสั่ง KEY_POWER...")
        await tv.send_key("KEY_POWER")
        print("ส่งคำสั่งปิดเครื่องเรียบร้อย!")

        # 4. ใช้เมธอดเก่า: close()
        await tv.close()

    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        print("โปรดตรวจสอบ IP Address และเปิดทีวีไว้เพื่ออนุญาตการเชื่อมต่อครั้งแรก")

if __name__ == "__main__":
    asyncio.run(power_off_tv())