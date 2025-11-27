#include <SPI.h> 
#include <Ethernet2.h> 
#include <WiFi.h>
#include <Wire.h> 
#include "TCA9554.h"

#define TCA9554_ADDRESS         0x20                      // TCA9554PWR I2C address
TCA9554 gpioExpander (TCA9554_ADDRESS);
#define I2C_SCL_PIN       41
#define I2C_SDA_PIN       42

//************Configuration*************//
//Wifi name & password
#define WIFI_AP_NAME "ESP32_1" 
#define WIFI_AP_PASS "12345678" 
WiFiServer webServer1(80); 
WiFiServer webServer2(81); 

//Wifi Access point
IPAddress apIP(192, 168, 1, 1); 
IPAddress apgateway(192, 168, 1, 254); 
IPAddress apnetmask(255, 255, 255, 0);

//Ethernet IP
IPAddress ip(192,168,128,1); 

//PLC Ethernet IP
IPAddress serverIP(192,168,128,102); 
IPAddress gateway(192,168,128,254); 
IPAddress subnet(255,255,255,0); 
//**************************************//

// ---------- SPI & W5500 pins ---------- 
#define ETH_CS 16 
#define ETH_RST 39 
#define ETH_IRQ  12
#define ETH_MISO 14 
#define ETH_MOSI 13 
#define ETH_SCK 15 

// ---------- Modbus TCP ---------- 
#define serverPort 502 
EthernetClient modbusClient; 

// ---------- Wi-Fi AP ---------- 

// WiFiServer webServer3(83);  

// ---------- Modbus Data ---------- 
bool coil0 = false; 
uint16_t holdingRegs[1] = {0}; 

// ---------- Network settings ---------- 
byte mac[] = { 0xDE,0xAD,0xBE,0xEF,0xFE,0xED }; 

hw_timer_t *Timer0_Cfg = NULL; 
int caddress = -1; 
bool cvalue = false; 
bool Havedatatosend = false; 
bool currentLedStatus = false; 
unsigned long ledBlinkTimer = 0; 
unsigned long modbusSendTimer = 0; 

// ---------- Coil Queue ---------- 
struct CoilRequest { int address; bool value; }; 
#define MAX_QUEUE 5
CoilRequest coilQueue[MAX_QUEUE]; 
int queueHead = 0; int queueTail = 0; 
bool queueIsEmpty() { 
  return queueHead == queueTail; 
} 
bool queueIsFull() { 
  return ((queueTail + 1) % MAX_QUEUE) == queueHead; 
} 

void enqueueCoil(int address, bool value) { 
  if (!queueIsFull()) { 
    coilQueue[queueTail].address = address; 
    coilQueue[queueTail].value = value; 
    queueTail = (queueTail + 1) % MAX_QUEUE; 
  } else { 
    Serial.print("⚠️ Queue full! Dropping coil request."); 
  } 
} 

bool dequeueCoil(CoilRequest &req) { 
  if (!queueIsEmpty()) { 
    req = coilQueue[queueHead]; 
    queueHead = (queueHead + 1) % MAX_QUEUE; 
    return true; 
    } 
    return false; 
} 
  
bool delayTimer(unsigned long &timer, unsigned long interval) { 
  unsigned long now = millis(); 
  if (now - timer >= interval) { 
    timer = now; return true; 
  } 
  return false; 
} 

// ---------- Initialize W5500 ---------- 
void initialW5500() { 
  SPI.begin(ETH_SCK, ETH_MISO, ETH_MOSI); 
  pinMode(ETH_RST, OUTPUT); 
  digitalWrite(ETH_RST, LOW); 
  delay(100); 
  digitalWrite(ETH_RST, HIGH); 
  delay(200); 
  Ethernet.init(ETH_CS); 
  Ethernet.begin(mac, ip, gateway, subnet); 
  Serial.print("EHT: Server IP: "); 
  Serial.println(Ethernet.localIP()); 
  Serial.println("EHT: ✅ W5500 initialized"); 
} 

// ---------- Initialize External Output ----------
byte lamps[8];
void initialExternalOutput() {
  Wire.begin( I2C_SDA_PIN, I2C_SCL_PIN); 
  gpioExpander.PinState();
  gpioExpander.PinMode();
  gpioExpander.AllOn();
  delay(2000);
  gpioExpander.AllOff();
}

// ---------- Initialize Wi-Fi Access Point ---------- 
void initialWifiAccesspoint() { 
  Serial.println("WiFi: 🔧 Initializing Access Point..."); 
  if (!WiFi.softAPConfig(apIP, apgateway, apnetmask)) { 
    Serial.println("WiFi: ❌ Failed to configure AP IP"); 
    return;
  } 
  if (!WiFi.softAP(WIFI_AP_NAME, WIFI_AP_PASS)) { 
    Serial.println("WiFi: ❌ Failed to start Access Point"); 
    return; 
  } 
  IPAddress IP = WiFi.softAPIP(); 
  Serial.print("WiFi: ✅ Access Point started! IP: "); 
  Serial.println(IP); 
} 

// ---------- Wi-Fi Task ---------- 
void wifiTask(void *parameter) { 
  WiFiServer *server = (WiFiServer *)parameter; 
  // cast parameter to pointer 
  for (;;) { 
    WiFiClient client = server -> available(); 
    if (client) { 
      // IPAddress clientIP = client.remoteIP(); 
      // uint16_t clientPort = client.remotePort(); 
      Serial.print("WiFi: 🌐 New client connected from "); 
      // Serial.print(clientIP); Serial.print(" Port "); 
      // Serial.println(clientPort); 
      unsigned long lastActive = millis(); 
      String received = ""; 
      while (client.connected()) { 
        if (client.available()) { 
          char c = client.read(); 
          received += c; 
          // Serial.write(c); 
          lastActive = millis(); 
          if (c == '\n') { 
            // End of message 
            // --- Parse Data --- 
            writeData(received); 
            received = ""; 
          } 
          // vTaskDelay(1); 
          // ✅ Give Wi-Fi time to breathe 
        } 
        if (millis() - lastActive > 10000) { 
          Serial.println("WiFi: ⚠️ Client timeout (no data)"
        ); 
          break; 
        } 
        vTaskDelay(10); 
      } 
      Serial.println(); 
      client.stop();
      // Serial.println("WiFi: Client disconnected."); 
    } 
    vTaskDelay(10); 
  } 
} 

void writeData(String received) { 
  if (received.length() == 0) { 
    Serial.println("WiFi: ⚠️ Invalid data format"); 
    return; 
  } 
  int firstSep = received.indexOf('|'); 
  if (firstSep < 0) { 
    Serial.println("WiFi: ⚠️ Invalid data format"); 
    return; 
  } 
  String payload = received.substring(firstSep + 1); 
  // "C01=1,C02=0,C03=1" 
  int start = 0; 
  int counter = 1;
  while (start < payload.length()) { 
    int commaIndex = payload.indexOf(',', start); 
    String token = (commaIndex == -1) ? payload.substring(start) : payload.substring(start, commaIndex); 
    start = (commaIndex == -1) ? payload.length() : commaIndex + 1; 
    int eqIndex = token.indexOf('='); if (eqIndex < 0) continue; 
    int address = token.substring(1, eqIndex).toInt(); 
    // "C01" → 1 
    int num = token.substring(eqIndex + 1).toInt(); 
    bool value = (num == 1); 
    lamps[counter] = value;
    counter += 1;
    gpioExpander.SetLamps(lamps);
    enqueueCoil(address, value); 
    //writeCoil(address, value); 
    Serial.printf("Queued: C%d=%d\n", address, value); 
  } 
} 

unsigned long losttime = millis();

void modbusTask(void *parameter) {
  for (;;) {
    CoilRequest req; 
    if (dequeueCoil(req)) { 
      writeCoil(req.address, req.value); 
      losttime = millis();  // update when coil processed
    } 
    else {
      // No request -> check timeout
      if (millis() - losttime > 1000) {   // <-- FIXED
        if (delayTimer(ledBlinkTimer, 200)){ 
          currentLedStatus = !currentLedStatus; 
          lamps[0] = currentLedStatus ? 1 : 0;
          gpioExpander.SetLamps(lamps);
        }
      } 
    }

    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}

// ---------- Modbus Request ---------- 
const uint16_t startingID = 1000;
uint16_t transactionID = 1000; 
bool modbusConnected = false;
uint32_t nextModbusRetry = 0;

bool ensureModbusConnected() {
  if (modbusClient.connected()) return true;

  if (millis() < nextModbusRetry) return false;

  Serial.println("🔌 Modbus: Connecting...");

  modbusClient.stop();
  modbusClient.setTimeout(200);

  if (modbusClient.connect(serverIP, serverPort)) {
    Serial.println("✅ Modbus: Connected");
    modbusConnected = true;
    nextModbusRetry = millis() + 2000;
    return true;
  }

  Serial.println("❌ Modbus: Connect Failed");
  modbusConnected = false;
  nextModbusRetry = millis() + 2000;
  return false;
}

void sendModbusRequest(byte *req, int len) { 
  if (!ensureModbusConnected()) {
    Serial.println("⚠️ No connection — skip send");
    return;
  }

  size_t written = modbusClient.write(req, len);

  if (written != len) {
    Serial.println("❌ Send Failed");
    modbusClient.stop();
    modbusConnected = false;
    return;
  }

  modbusClient.flush();

  Serial.print("➡️ Sent: ");
  for (int i = 0; i < len; i++) Serial.printf("%02X ", req[i]);
  Serial.println();

  // Read response
  unsigned long startWait = millis();
  while (!modbusClient.available()) {
    if (millis() - startWait > 200) {
      Serial.println("❌ No response — timeout");
      return;
    }
  }

  Serial.print("⬅️ Response: ");
  while (modbusClient.available()) {
    Serial.printf("%02X ", modbusClient.read());
  }
  Serial.println();
} 

void writeCoil(int address, bool state) { 
  if (transactionID > startingID + 999){
    transactionID = startingID;
  }
  if (address >= 0) { 
    byte request[] = { 
      highByte(transactionID), 
      lowByte(transactionID), 
      0x00, 0x00, 0x00, 0x06, 0x01, 0x05, 
      highByte(address), 
      lowByte(address), state ? 0xFF : 0x00, 0x00 }; 
    sendModbusRequest(request, sizeof(request)); 
    transactionID++; 
  } 
} 

// ---------- Setup ---------- 
void setup() { 
  Serial.begin(115200); 
  while (!Serial);
  delay(1000); 
  Serial.println("ESP32-S3 + W5500 + Wi-Fi AP"); 
  initialW5500(); 
  initialWifiAccesspoint(); 
  initialExternalOutput();
  webServer1.begin(); 
  Serial.println("WiFi: 🌐 Web server started on port 80"); 
  webServer2.begin(); 
  Serial.println("WiFi: 🌐 Web server started on port 81");
  // webServer3.begin(); 
  // Serial.println("WiFi: 🌐 Web server started on port 82");

  xTaskCreatePinnedToCore(wifiTask, "WiFiTask1", 4096, &webServer1, 1, NULL, 1); 
  xTaskCreatePinnedToCore(wifiTask, "WiFiTask2", 4096, &webServer2, 1, NULL, 1); 
  // xTaskCreatePinnedToCore(wifiTask, "WiFiTask3", 4096, &webServer3, 1, NULL, 1);
  xTaskCreatePinnedToCore(modbusTask,"ModbusTask", 4096, NULL,    1, NULL, 1); 
} 

bool currentSendStatus = false; 
// ---------- Loop ---------- 
void loop() { 
  // Process one coil per loop iteration 
  // CoilRequest req; 
  // if (dequeueCoil(req)) { 
  //   writeCoil(req.address, req.value); 
  // } 
  // if (delayTimer(modbusSendTimer, 1000)){ 
  // currentSendStatus = !currentSendStatus; 
  // writeCoil(10, currentSendStatus); 
  // } 
}