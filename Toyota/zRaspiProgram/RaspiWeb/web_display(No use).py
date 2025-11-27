import os
import gi
# เพิ่มโมดูล json เพื่อจัดการกับข้อมูล JSON
import json 
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.1') 
from gi.repository import Gtk, WebKit2, GLib

# บังคับใช้ Software Rendering และ X11 Backend (ถ้ายังจำเป็น)
os.environ["WEBVIEW_GTK_USE_SOFTWARE"] = "1"
os.environ["GDK_BACKEND"] = "x11" 
os.environ["WEBKIT_DISABLE_COMPOSITING_MODE"] = "1" 

# --- ฟังก์ชันสำหรับอ่าน URL จากไฟล์ JSON ---
def get_url_from_config(filename="/home/iiot/Desktop/Toyota/url_config.txt"):
    """อ่าน URL จาก 'parameter' ในไฟล์ JSON config."""
    try:
        with open(filename, 'r') as f:
            # ใช้ json.load เพื่ออ่านและแยกวิเคราะห์ไฟล์ JSON
            data = json.load(f)
            
            # ตรวจสอบว่าเป็น list และมี object อย่างน้อยหนึ่งตัว
            if isinstance(data, list) and len(data) > 0:
                # ดึงค่าจากคีย์ 'parameter' ใน object แรก
                url = data[0].get('parameter', '').strip() 
                if url:
                    return url
            
            # ถ้าโครงสร้างไม่ถูกต้องหรือไม่พบ URL
            print(f"คำเตือน: โครงสร้างไฟล์ JSON '{filename}' ไม่ถูกต้องหรือไม่พบ 'parameter'")
            return "about:blank"
            
    except FileNotFoundError:
        print(f"ข้อผิดพลาด: ไม่พบไฟล์ '{filename}'")
        return "about:blank" 
    except json.JSONDecodeError:
        # ดักจับข้อผิดพลาดหากไฟล์ไม่ใช่ JSON ที่ถูกต้อง
        print(f"ข้อผิดพลาด: ไฟล์ '{filename}' ไม่ใช่ JSON ที่ถูกต้อง")
        return "about:blank"
    except Exception as e:
        print(f"ข้อผิดพลาดในการอ่านไฟล์: {e}")
        return "about:blank" 

# --- คลาส WebDisplay พร้อมฟังก์ชันตรวจสอบอัตโนมัติ ---
class WebDisplay(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Toyota Web Monitor")
        
        # 1. อ่านและเก็บ URL เริ่มต้น
        self.current_url = get_url_from_config() 
        print(f"โหลด URL เริ่มต้น: {self.current_url}")
        
        self.fullscreen() 
        
        # สร้าง Web View
        self.webview = WebKit2.WebView()
        
        # 2. โหลด URL เริ่มต้น
        self.webview.load_uri(self.current_url)
        
        self.add(self.webview)
        self.connect("destroy", Gtk.main_quit)
        
        # 3. เริ่มฟังก์ชันตรวจสอบ URL (ตรวจสอบทุก 1000 มิลลิวินาที = 1 วินาที)
        self.start_url_monitor(interval_ms=2000)

    def start_url_monitor(self, interval_ms):
        """เริ่มการตรวจสอบ URL ทุกๆ 'interval_ms' มิลลิวินาที"""
        GLib.timeout_add(interval_ms, self.check_and_reload_url)
        print(f"เริ่มตรวจสอบไฟล์ URL ทุกๆ {interval_ms/1000} วินาที")

    def check_and_reload_url(self):
        """อ่าน URL จากไฟล์และรีโหลดหน้าถ้ามีการเปลี่ยนแปลง"""
        new_url = get_url_from_config()
        
        # ตรวจสอบว่า URL ใหม่แตกต่างจาก URL ปัจจุบันหรือไม่
        if new_url != self.current_url:
            print(f"ตรวจพบ URL เปลี่ยนแปลง: จาก {self.current_url} เป็น {new_url}")
            self.current_url = new_url # อัปเดต URL ปัจจุบัน
            self.webview.load_uri(new_url) # โหลด URL ใหม่
        
        return True 

if __name__ == '__main__':
    win = WebDisplay()
    win.show_all()
    Gtk.main()