import socket
import json
import os
import RPi.GPIO as GPIO
import time
import signal
import sys
import threading

def signal_handler(sig, frame):
    print('Signal received, cleaning up and exiting...')
    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

UDP_LISTEN_IP = "0.0.0.0"
UDP_LISTEN_PORT = 8000
IP_SAVE_PATH = "IP_Address"  

LED_NOTIFY_PIN = 6  

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LED_NOTIFY_PIN, GPIO.OUT)
    GPIO.output(LED_NOTIFY_PIN, GPIO.LOW)

def blink_led(duration=2.0):
    print("Blinking LED to notify config received.")
    GPIO.output(LED_NOTIFY_PIN, GPIO.HIGH)
    time.sleep(duration)
    GPIO.output(LED_NOTIFY_PIN, GPIO.LOW)

def validate_ip_format(ip):
    parts = ip.strip().split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except Exception:
        return False

def save_config_to_file(config_obj):
    try:
        with open(IP_SAVE_PATH, "w") as file:
            json.dump(config_obj, file, indent=2)
        print(f"Saved config: {config_obj}")
        threading.Thread(target=blink_led).start()
    except Exception as e:
        print(f"Failed to write config: {e}")

def start_udp_receiver():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass  

    sock.bind((UDP_LISTEN_IP, UDP_LISTEN_PORT))
    print(f"Listening for config on UDP {UDP_LISTEN_IP}:{UDP_LISTEN_PORT}...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8').strip()
            print(f"Received from {addr}: '{message}'")

            try:
                obj = json.loads(message)
                pc_ip = obj.get("PcIpAddress")
                amqp = obj.get("AmqpPath")
                machine_code = obj.get("MachineCode")  

                if pc_ip and validate_ip_format(pc_ip):
                    save_config_to_file({
                        "PcIpAddress": pc_ip,
                        "AmqpPath": amqp or "",
                        "MachineCode": machine_code or ""  
                    })
                else:
                    print("Invalid or missing PcIpAddress in JSON.")
            except json.JSONDecodeError:
                print("Invalid JSON format")

        except Exception as e:
            print(f"Error receiving UDP: {e}")
        print("Waiting for next packet...")


if __name__ == "__main__":
    try:
        setup_gpio()
        start_udp_receiver()
    except KeyboardInterrupt:
        print("Exiting by user interrupt...")
    finally:
        GPIO.cleanup()

