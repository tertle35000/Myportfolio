import RPi.GPIO as GPIO
import time

# กำหนดพิน
STEP_PIN = 12
DIR_PIN = 13

# ตั้งค่า GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(STEP_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

def rotate(steps, direction=1, step_delay=0.001):
    """
    steps: จำนวนสเต็ป
    direction: 1 หมุนตามเข็ม, 0 หมุนทวนเข็ม
    step_delay: เวลา delay ต่อสเต็ป
    """
    GPIO.output(DIR_PIN, direction)
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(step_delay)

try:
    while True:
        rotate(200, direction=1)  # หมุนตามเข็ม 200 steps
        time.sleep(1)
        rotate(200, direction=0)  # หมุนทวนเข็ม 200 steps
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
