import RPi.GPIO as GPIO
import time
import signal
import sys
from datetime import datetime
import json
from communication_manager import CommunicationManager

STATE_BUTTON_PINS = [26, 23, 24, 25, 16]
COUNT_BUTTON_PIN = 13

STATE_LED_PINS = [17, 27, 22, 5, 6] 

CURRENT_ACTIVE_LED_INDEX = 0 
PRODUCT_COUNT = 1

LAST_PRESS_TIME = {pin: 0 for pin in STATE_BUTTON_PINS + [COUNT_BUTTON_PIN]}
DEBOUNCE_DELAY = 0.1 

COUNT_BUTTON_PRESS_START_TIME = 0  
LONG_PRESS_DURATION = 3.0  
COUNT_BUTTON_LONG_PRESS_ACTIVATED = False  

RUNNING = True

def load_ip_address(filepath):
    default_ip = "192.168.128.200"
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)  # โหลดเป็น dict
            ip = data.get("PcIpAddress") or default_ip
            if not data.get("PcIpAddress"):  # ถ้าค่าว่างหรือไม่มี key
                print(f"[WARNING] PcIpAddress not found or empty, using default: {default_ip}")
            else:
                print(f"[DEBUG] Loaded IP: {ip}")
            return ip
    except Exception as e:
        print(f"[ERROR] Failed to load IP address from {filepath}: {e}, using default {default_ip}")
        return default_ip  # ใช้ default ถ้า error

def load_machine_code(filepath):
    default_code = "MCH001"
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)  # โหลด JSON เป็น dict
            code = data.get("MachineCode") or default_code
            if not data.get("MachineCode"):  # ถ้าค่าว่างหรือไม่มี key
                print(f"[WARNING] MachineCode not found or empty, using default: {default_code}")
            else:
                print(f"[DEBUG] Loaded MachineCode: {code}")
            return code
    except Exception as e:
        print(f"[ERROR] Failed to load MachineCode from {filepath}: {e}, using default {default_code}")
        return default_code  # ใช้ default ถ้า error

HOST_IP = load_ip_address('IP_Address')  
MACHINE_CODE_IDENTIFIER = load_machine_code('IP_Address')

def send_state_with_dynamic_ip(state_name):
    ip = load_ip_address('IP_Address')
    machine_code = load_machine_code('IP_Address')
    temp_comm = CommunicationManager(
        protocol=COMMUNICATION_PROTOCOL,
        machine_code=machine_code,
        host=ip,
        port=9000
    )
    temp_comm.send_state_update(state_name)
    temp_comm.close()

def send_count_with_dynamic_ip(count):
    ip = load_ip_address('IP_Address')
    machine_code = load_machine_code('IP_Address')
    temp_comm = CommunicationManager(
        protocol=COMMUNICATION_PROTOCOL,
        machine_code=machine_code,
        host=ip,
        port=9000
    )
    temp_comm.send_ok_qty(count)
    temp_comm.close()


COMMUNICATION_PROTOCOL = 'udp' 
comm_manager = CommunicationManager(
    protocol=COMMUNICATION_PROTOCOL,
    machine_code=MACHINE_CODE_IDENTIFIER,
    host=HOST_IP,
    port=9000    
)

STATE_NAMES_MAP = {
    0: "Break",
    1: "Setup",
    2: "Downtime",
    3: "Idle",
    4: "Run"
}

def setup_gpio():
    global CURRENT_ACTIVE_LED_INDEX 

    print("--- Setting up GPIO ---")
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        for pin in STATE_BUTTON_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        GPIO.setup(COUNT_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        for pin in STATE_LED_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW) 
        
        CURRENT_ACTIVE_LED_INDEX = 0 
        GPIO.output(STATE_LED_PINS[CURRENT_ACTIVE_LED_INDEX], GPIO.HIGH)

        print(f"Default LED ON: Pin {STATE_LED_PINS[CURRENT_ACTIVE_LED_INDEX]}")
        print("GPIO pins configured successfully.")

    except RuntimeError as e:
        print(f"ERROR: RuntimeError during GPIO setup: {e}")
        sys.exit(1) 
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during GPIO setup: {e}")
        sys.exit(1)

def cleanup_gpio():
    print("\n--- Cleaning up GPIO ---")
    for pin in STATE_LED_PINS:
        GPIO.output(pin, GPIO.LOW)
        
    GPIO.cleanup()  
    print("GPIO cleanup complete. Exiting.")


def update_state_leds():
   
    global CURRENT_ACTIVE_LED_INDEX 

   
    for pin in STATE_LED_PINS:
        GPIO.output(pin, GPIO.LOW)

  
    if 0 <= CURRENT_ACTIVE_LED_INDEX < len(STATE_LED_PINS):
        GPIO.output(STATE_LED_PINS[CURRENT_ACTIVE_LED_INDEX], GPIO.HIGH)
        print(f"  - Active LED: {STATE_LED_PINS[CURRENT_ACTIVE_LED_INDEX]} (Index: {CURRENT_ACTIVE_LED_INDEX})")
    else:
        print(f"WARNING: Invalid CURRENT_ACTIVE_LED_INDEX: {CURRENT_ACTIVE_LED_INDEX}. No LED will be active.")

def test_leds_sequence():
  
    # print("\n--- Running LED Sequence Test ---")
    # for i, pin in enumerate(STATE_LED_PINS):
    #     print(f"  - Turning ON LED {i} on Pin {pin}")
    #     GPIO.output(pin, GPIO.HIGH)
    #     time.sleep(0.5)
    #     print(f"  - Turning OFF LED {i} on Pin {pin}")
    #     GPIO.output(pin, GPIO.LOW)
    #     time.sleep(0.2)
    # print("LED sequence test completed.")

    for round in range(3):
        if round == 0:
            #  รอบที่ 1: ซ้าย -> ขวา แล้วดับ
            for i, pin in enumerate(STATE_LED_PINS):
                GPIO.output(pin, GPIO.HIGH)
                print(f"  - LED {i} ON (Pin {pin})")
                time.sleep(0.1)

            for i, pin in enumerate(STATE_LED_PINS):
                GPIO.output(pin, GPIO.LOW)
                print(f"  - LED {i} OFF (Pin {pin})")
                time.sleep(0.1)

        elif round == 1:
            #  รอบที่ 2: ขวา -> ซ้าย แล้วดับ
            for i, pin in reversed(list(enumerate(STATE_LED_PINS))):
                GPIO.output(pin, GPIO.HIGH)
                print(f"  - LED {i} ON (Pin {pin})")
                time.sleep(0.1)

            for i, pin in reversed(list(enumerate(STATE_LED_PINS))):
                GPIO.output(pin, GPIO.LOW)
                print(f"  - LED {i} OFF (Pin {pin})")
                time.sleep(0.1)

        elif round == 2:
            #  รอบที่ 3: ติดจากกลางออก → ดับจากกลางออก
            mid = len(STATE_LED_PINS) // 2
            sequence = []

            # ขยายจากกลางไปซ้าย-ขวา
            for offset in range(mid + 1):
                left = mid - offset
                right = mid + offset
                if left >= 0:
                    sequence.append(left)
                if right != left and right < len(STATE_LED_PINS):
                    sequence.append(right)

            # เปิดไฟตามลำดับกลางออก
            for i in sequence:
                GPIO.output(STATE_LED_PINS[i], GPIO.HIGH)
                print(f"  - LED {i} ON (Pin {STATE_LED_PINS[i]})")
                time.sleep(0.1)

            # ดับไฟย้อนกลับ (กลางออกเหมือนกัน)
            for i in sequence:
                GPIO.output(STATE_LED_PINS[i], GPIO.LOW)
                print(f"  - LED {i} OFF (Pin {STATE_LED_PINS[i]})")
                time.sleep(0.1)

# เพิ่มไว้บนสุดของไฟล์ (global)
STATE_BUTTON_HELD_INDEX = None  # ติดตามปุ่มที่กดค้างอยู่

def handle_buttons():
    global CURRENT_ACTIVE_LED_INDEX, PRODUCT_COUNT
    global COUNT_BUTTON_PRESS_START_TIME, COUNT_BUTTON_LONG_PRESS_ACTIVATED
    global STATE_BUTTON_HELD_INDEX

    current_time = time.time()

    pressed_buttons = [i for i, pin in enumerate(STATE_BUTTON_PINS) if GPIO.input(pin) == GPIO.LOW]

    if STATE_BUTTON_HELD_INDEX is not None:
        # ถ้ามีปุ่มค้างไว้ → ตรวจว่าปล่อยหรือยัง
        pin = STATE_BUTTON_PINS[STATE_BUTTON_HELD_INDEX]
        if GPIO.input(pin) == GPIO.HIGH:
            print(f"  - Released button on Pin {pin} (Index {STATE_BUTTON_HELD_INDEX})")
            STATE_BUTTON_HELD_INDEX = None
    else:
        # ยังไม่มีปุ่มถูกกดค้าง → อนุญาตให้ตรวจจับใหม่
        if len(pressed_buttons) == 1:
            i = pressed_buttons[0]
            pin = STATE_BUTTON_PINS[i]

            if (current_time - LAST_PRESS_TIME[pin]) > DEBOUNCE_DELAY:
                LAST_PRESS_TIME[pin] = current_time
                STATE_BUTTON_HELD_INDEX = i  # จำว่ากดปุ่มนี้อยู่

                if CURRENT_ACTIVE_LED_INDEX != i:
                    CURRENT_ACTIVE_LED_INDEX = i
                    print(f"  - State button on Pin {pin} pressed. Setting active LED to index {i}.")
                    update_state_leds()

                    new_state_name = STATE_NAMES_MAP.get(CURRENT_ACTIVE_LED_INDEX, "UNKNOWN_STATE")
                    print(f"  - Triggering communication for state change to: {new_state_name}")
                    send_state_with_dynamic_ip(new_state_name)

        elif len(pressed_buttons) > 1:
            print("Multiple state buttons pressed simultaneously. Ignoring input.")

    
    current_count_button_state = (GPIO.input(COUNT_BUTTON_PIN) == GPIO.LOW)

    if current_count_button_state:
        if COUNT_BUTTON_PRESS_START_TIME == 0: 
            COUNT_BUTTON_PRESS_START_TIME = current_time
            COUNT_BUTTON_LONG_PRESS_ACTIVATED = False 

        
        if not COUNT_BUTTON_LONG_PRESS_ACTIVATED and \
           (current_time - COUNT_BUTTON_PRESS_START_TIME) >= LONG_PRESS_DURATION:
            PRODUCT_COUNT = 0 
            COUNT_BUTTON_LONG_PRESS_ACTIVATED = True 
            send_count_with_dynamic_ip(PRODUCT_COUNT)
            print(f"  - Count button on Pin {COUNT_BUTTON_PIN} held for {LONG_PRESS_DURATION}s. PRODUCT COUNT RESET to {PRODUCT_COUNT}.")
            LAST_PRESS_TIME[COUNT_BUTTON_PIN] = current_time 
            PRODUCT_COUNT = 1 
            
            for pin in STATE_LED_PINS:
                GPIO.output(pin, GPIO.HIGH)
            print(f"  - Count button on Pin {COUNT_BUTTON_PIN} held for {LONG_PRESS_DURATION}s. LED {STATE_LED_PINS} is on.")
            
    else:
        if COUNT_BUTTON_PRESS_START_TIME != 0: 
            press_duration = current_time - COUNT_BUTTON_PRESS_START_TIME

            
            if not COUNT_BUTTON_LONG_PRESS_ACTIVATED and press_duration >= DEBOUNCE_DELAY:
                if (current_time - LAST_PRESS_TIME[COUNT_BUTTON_PIN]) > DEBOUNCE_DELAY:
                    # PRODUCT_COUNT += 1
                    print(f"  - Count button on Pin {COUNT_BUTTON_PIN} short pressed. PRODUCT COUNT: {PRODUCT_COUNT}.")
                    LAST_PRESS_TIME[COUNT_BUTTON_PIN] = current_time
                    send_count_with_dynamic_ip(PRODUCT_COUNT) 

            if COUNT_BUTTON_LONG_PRESS_ACTIVATED:
                for pin in STATE_LED_PINS:
                    GPIO.output(pin, GPIO.LOW)
                print(f"  - Count button release Pin {COUNT_BUTTON_PIN} long pressed. LED {STATE_LED_PINS} is off.")
                CURRENT_ACTIVE_LED_INDEX = -1 
                
            COUNT_BUTTON_PRESS_START_TIME = 0
            COUNT_BUTTON_LONG_PRESS_ACTIVATED = False





def signal_handler(signum, frame):
    global RUNNING
    print(f"\nReceived signal {signum}, preparing to exit...")
    RUNNING = False

def main_loop():
    global RUNNING

    setup_gpio() 

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    #test_leds_sequence() 
    update_state_leds() 

    print("\n--- GPIO Hardware Controller Running with Communication Layer ---")
    print(f"  - Communication Protocol: {COMMUNICATION_PROTOCOL.upper()}")
    if COMMUNICATION_PROTOCOL == 'socket':
        print(f"  - Socket Server Address: {comm_manager.host}:{comm_manager.port}")
        print("  - Waiting for a PC to connect to this address.")
    print("  - Observe console output for button presses, LED changes, and communication attempts.")
    print("  - State Buttons (Pins 26, 23, 24, 25, 16): Change active LED AND trigger communication.")
    print("  - Count Button (Pin 13): Short Press -> Increment Count; Hold 3s -> Reset Count.")
    print("  - Press Ctrl+C to exit gracefully.")
    print("-----------------------------------------------------------")

    try:
        while RUNNING:
            handle_buttons() 
            time.sleep(0.01)  

    except Exception as e:
        print(f"An unexpected error occurred in the main loop: {e}")
    finally:
        cleanup_gpio() 
        comm_manager.close()

if __name__ == "__main__":
    main_loop()