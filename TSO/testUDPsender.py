import socket
import json
import time

target_ip = "192.168.128.124"  # IP ของ Raspberry Pi
target_port = 8000

# เพิ่ม MachineCode
config = {
    "PcIpAddress": "192.168.128.240",
    "AmqpPath": "amqp://guest:guest@localhost:5672/",
    "MachineCode": "MCH002" 
}

message = json.dumps(config)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

repeat_count = 5
delay_between_sends = 0.2

for i in range(repeat_count):
    sock.sendto(message.encode('utf-8'), (target_ip, target_port))
    print(f"[{i+1}/{repeat_count}] Sent to {target_ip}:{target_port}")
    time.sleep(delay_between_sends)

print("Done sending.")
sock.close()


