import socket
import json

class ColorSender:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def send_data(self, color_name, qr_list=None, bar_list=None):
        """ส่งข้อมูล color + QR + Barcode ไป C#"""
        if self.sock is None:
            raise Exception("Socket ยังไม่ได้เชื่อมต่อ")

        qr_list = qr_list or []
        bar_list = bar_list or []

        data = {
            "color": color_name,
            "QRdata": qr_list,
            "Bardata": bar_list
        }
        message = json.dumps(data).encode('utf-8')
        self.sock.sendall(message)
        print("ส่งข้อมูลไปยัง C# สำเร็จ:", data)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None
            print("ปิดการเชื่อมต่อกับ C# แล้ว")