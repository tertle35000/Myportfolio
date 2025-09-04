import socket

UDP_IP = "0.0.0.0"     # รับจากทุก IP
UDP_PORT = 9000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening for UDP packets on port {UDP_PORT}...")

while True:
    data, addr = sock.recvfrom(1024)  # รับสูงสุด 1024 ไบต์
    print(f"Received from {addr}: {data.decode('utf-8')}")