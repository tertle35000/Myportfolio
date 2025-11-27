import requests

# เปลี่ยนเป็น IP ของ Pi
url = "http://192.168.128.124:5000/tv"


# 1 = เปิด, 0 = ปิด
data = {"power": 0}

response = requests.post(url, json=data)

print(response.json())
