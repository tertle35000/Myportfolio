#include "FS.h"
#include "SPIFFS.h"
#include <WiFi.h>
#include <ArduinoJson.h>
#include "TCA9554.h"

#define TCA9554_ADDRESS         0x20                      // TCA9554PWR I2C address
TCA9554 gpioExpander (TCA9554_ADDRESS);
#define I2C_SCL_PIN       41
#define I2C_SDA_PIN       42

#define TOTAL_COILS 5  // จำนวน coils ต่อบอร์ด
int coilStartIndex = 361; // ตั้งค่าตามบอร์ด: 0, 5, 10, ...

int coils[TOTAL_COILS] = {0};
int inputValues[TOTAL_COILS] = {0}; // เก็บค่าจาก DI pins

#define Device1    4
#define Device2    5
#define Device3    6
#define Device4    7
#define Device5    8

// #define Device6    9
// #define Device7    10


#define RED_DO     0
#define GREEN_DO   1
// #define test1      5
// #define test2      6

// Wi-Fi
const char* ssid = "ESP32_1";
const char* password = "12345678";
WiFiClient client;
const char* receiverIP = "192.168.130.1";   // IP ของ ESP32 Receiver
const uint16_t receiverPort = 80;        // Port ที่ Receiver เปิดไว้


IPAddress local_IP(192, 168, 130, 100); // Your desired static IP
IPAddress gateway(192, 168, 130, 254);    // Your router's IP address
IPAddress subnet(255, 255, 255, 0); // Your network's subnet mask

bool wifiConnected = false;
unsigned long previousMillis = 0;
const unsigned long blinkInterval = 300;
bool ledState = false;

// เพิ่มตัวควบคุม Reconnect
unsigned long lastReconnectAttempt = 0;
const unsigned long reconnectInterval = 5000; // 5 วินาที

WiFiServer server(5000);   // หรือ port ที่ต้องการรับ

TaskHandle_t clientTaskHandle = NULL;
TaskHandle_t wifiTaskHandle = NULL;

void setup() {
  // Serial.begin(115200);
  setupExternalOutput();
  setupWiFi();
  setupTCPServer();
  setupSPIFFS();
  setupPins();
}

// --- WiFi ---
void setupWiFi() {
  WiFi.config(local_IP, gateway, subnet);
  Serial.println("Connecting to WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  xTaskCreatePinnedToCore(
    WiFiTask,"WiFiTask",        // Name
    8192,NULL,1,                 // Priority
    &wifiTaskHandle,1                  // Core (0 or 1)
  );
}

// --- TCP Server ---
void setupTCPServer() {
  server.begin();
  Serial.println("TCP server started");
   xTaskCreatePinnedToCore( 
    handleClientTask,"ClientTask",       // Name
    8192,NULL,1,                  // Priority
    &clientTaskHandle,1                   // Core ID (0 or 1)
  );
}

// ---------- Initialize External Output ----------
byte lamps[8];
void setupExternalOutput() {
  Wire.begin( I2C_SDA_PIN, I2C_SCL_PIN); 
  gpioExpander.PinState();
  gpioExpander.PinMode();
  gpioExpander.AllOn();
  delay(2000);
  gpioExpander.AllOff();
}


void setupSPIFFS() {
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }

  if (SPIFFS.exists("/config.txt")) {
    readCoilsFromFile(); // ถ้ามีไฟล์อยู่ → อ่านค่าจากไฟล์
  } else {
    createDefaultCoils(); // ถ้าไม่มีไฟล์ → สร้างค่าเริ่มต้น
  }
}

// --- อ่านค่า coils จากไฟล์ config ---
void readCoilsFromFile() {
  File file = SPIFFS.open("/config.txt", FILE_READ);
  if (!file) {
    Serial.println("Failed to open config file for reading");
    return;
  }

  while (file.available()) {
    String line = file.readStringUntil('\n'); // อ่านทีละบรรทัด
    line.trim(); // ลบช่องว่างหรือ \r
    if (line.length() == 0) continue;

    int eqIndex = line.indexOf('='); // หาตำแหน่ง "="
    if (eqIndex == -1) continue;

    String coilName = line.substring(0, eqIndex); // เช่น "C0"
    int coilIndex = coilName.substring(1).toInt() - coilStartIndex; // แปลงเป็น index
    int value = line.substring(eqIndex + 1).toInt(); // ค่า 0 หรือ 1

    if (coilIndex >= 0 && coilIndex < TOTAL_COILS) {
      coils[coilIndex] = value;
    }
  }

  file.close();

  Serial.println("Coils loaded from config:");
  for (int i = 0; i < TOTAL_COILS; i++) {
    Serial.print("C"); Serial.print(i + coilStartIndex);
    Serial.print("="); Serial.println(coils[i]);
  }
}

// --- ฟังก์ชันสร้างค่าเริ่มต้นและไฟล์ config ---
void createDefaultCoils() {
  for (int i = 0; i < TOTAL_COILS; i++) {
    coils[i] = (i < 2) ? 1 : 0; // ตัวอย่าง: C0-C2 = 1
  }

  String msg = "";
  for (int i = 0; i < TOTAL_COILS; i++) {
    msg += "C" + String(i + coilStartIndex) + "=" + String(coils[i]) + "\n"; // +coilStartIndex
  }

  File file = SPIFFS.open("/config.txt", FILE_WRITE);
  if (file) {
    file.print(msg);
    file.close();
    Serial.println("Config file written:");
    Serial.println(msg);
  } else {
    Serial.println("Failed to open config file for writing");
  }
}


// --- Pins ---
void setupPins() {
  int inputPins[] = {Device1 , Device2 , Device3 ,Device4 , Device5};
  for (int i = 0; i < sizeof(inputPins)/sizeof(inputPins[0]); i++) {
    pinMode(inputPins[i], INPUT_PULLUP);
  }

  int outputPins[] = {RED_DO, GREEN_DO};
  for (int i = 0; i < sizeof(outputPins)/sizeof(outputPins[0]); i++) {
    // pinMode(outputPins[i], OUTPUT);

  }
}

// ===============================================================================  Program  =============================================================================== //

// ฟังก์ชันแปลง JSON → อัปเดต coils[]
void parseJSONAndUpdateCoils(String jsonStr) {
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, jsonStr);
  if (error) {
    Serial.print("JSON parse failed: ");
    Serial.println(error.c_str());
    return;
  }

  for (JsonPair kv : doc.as<JsonObject>()) {
    String key = kv.key().c_str(); // "C0", "C1", ...
    int index = key.substring(1).toInt() - coilStartIndex; // ใช้ offset
    int value = atoi(kv.value().as<const char*>());
    if (index >= 0 && index < TOTAL_COILS) {
      coils[index] = value;
      Serial.printf("Updated %s = %d\n", key.c_str(), value);
    }
  }
}


void saveCoilsToFile() {
  String msg = "";
  for (int i = 0; i < TOTAL_COILS; i++) {
    msg += "C" + String(i + coilStartIndex) + "=" + String(coils[i]) + "\n";
  }

  File file = SPIFFS.open("/config.txt", FILE_WRITE); 
  if (file) {
    file.print(msg);
    file.close();
    Serial.println("Coils saved to config.txt.");
  } else {
    Serial.println("Failed to write config file");
  }
}


void handleClientTask(void *parameter) {
  for (;;) {
    unsigned long start = millis();
    WiFiClient wifiClient = server.available();
    if (!wifiClient) {
      vTaskDelay(10 / portTICK_PERIOD_MS); // prevent CPU busy loop
      continue;
    }

    Serial.println("Client connected");

    String line = "";
    unsigned long startTime = millis();

    while (wifiClient.connected()) {
      while (wifiClient.available()) {
        char c = wifiClient.read();
        line += c;

        if (c == '\n') {
          Serial.println("Received raw: " + line);

          if (line.length() > 2) {
            parseJSONAndUpdateCoils(line);
            saveCoilsToFile();
          }

          line = "";
          startTime = millis();
        }
      }

      if (millis() - startTime > 2000) {
        Serial.println("Client timeout");
        break;
      }

      vTaskDelay(1 / portTICK_PERIOD_MS); // yield to other tasks
    }

    wifiClient.stop();
    Serial.println("Client disconnected");

    Serial.printf("handleClient: %lu ms\n", millis() - start);
  }
}

void WiFiTask(void *parameter) {
  for (;;) {
    // unsigned long t2 = millis();
    checkWiFi();
    // Serial.printf("checkWiFi: %lu ms\n", millis() - t2);

    // unsigned long t4 = millis();
    if (wifiConnected) sendToReceiver();
    // Serial.printf("sendToReceiver: %lu ms\n", millis() - t4);

    vTaskDelay(10 / portTICK_PERIOD_MS);  // Run every 0.5s
  }
}

void checkWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    if (!wifiConnected) {
      wifiConnected = true;
      lamps[GREEN_DO] = 1;
      gpioExpander.SetLamps(lamps);
      //digitalWrite(GREEN_DO, HIGH);
      Serial.print("WiFi connected. IP: ");
      Serial.println(WiFi.localIP());
    }
  } else {
    wifiConnected = false;

    // กระพริบไฟเขียว
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= blinkInterval) {
      previousMillis = currentMillis;
      ledState = !ledState;
      lamps[GREEN_DO] = ledState ? 1 : 0;
      gpioExpander.SetLamps(lamps);
      //digitalWrite(GREEN_DO, ledState);
    }

    // reconnect ทุก 5 วินาที
    if (millis() - lastReconnectAttempt >= reconnectInterval) {
      Serial.println("Reconnecting WiFi...");
      WiFi.disconnect(true);
      WiFi.config(local_IP, gateway, subnet);
      WiFi.mode(WIFI_STA);
      WiFi.begin(ssid, password);
      lastReconnectAttempt = millis();
    }
  }
}

void readInputs() {
  inputValues[0] = !digitalRead(Device1);
  inputValues[1] = !digitalRead(Device2);
  inputValues[2] = !digitalRead(Device3);
  inputValues[3] = !digitalRead(Device4);
  inputValues[4] = !digitalRead(Device5);    // ถ้า TOTAL_COILS > 3 ต้องอ่าน DI เพิ่มเอง หรือกำหนด 0
  // inputValues[5] = digitalRead(Device6);
  // inputValues[6] = digitalRead(Device7);


  Serial.print("Device1: "); Serial.print(inputValues[0]);
  Serial.print(" Device2: "); Serial.print(inputValues[1]);
  Serial.print(" Device3: "); Serial.print(inputValues[2]);
  Serial.print(" Device4: "); Serial.print(inputValues[3]);
  Serial.print(" Device5: "); Serial.println(inputValues[4]);

  // OUTPUT
  if (inputValues[0] || inputValues[1] || inputValues[2] || inputValues[3] || inputValues[4]) {
    // ถ้าตัวใดตัวหนึ่งเป็น 1 (ถูกกด)
    lamps[RED_DO] = 1; 
  } else {
    // ถ้าทุกตัวเป็น 0 (ไม่ถูกกดเลย)
    lamps[RED_DO] = 0; 
  }

  gpioExpander.SetLamps(lamps);
  // digitalWrite(RED_DO, inputValues[0]);
}


void sendToReceiver() {
  if (WiFi.status() != WL_CONNECTED) return;

  static unsigned long lastReconnect = 0;
  const unsigned long reconnectDelay = 2000; // ลอง reconnect ทุก 2 วิ

  if (!client.connected()) {
    unsigned long now = millis();
    if (now - lastReconnect >= reconnectDelay) {
      lastReconnect = now;
      unsigned long t0 = millis();
      Serial.println("[INFO] Trying to reconnect...");
      if (client.connect(receiverIP, receiverPort, 500)) {
        client.setNoDelay(true); // ส่งทันที ไม่ buffer
        Serial.printf("[INFO] Reconnected in %lu ms\n", millis() - t0);
      } else {
        Serial.printf("[WARN] Reconnect failed after %lu ms\n", millis() - t0);
      }
    }
    return; // ยังไม่ต่อได้ → ไม่ต้องส่ง
  }

  // === สร้างข้อความ ===
  String ipSuffix = String(local_IP[3]);
  String msg = ipSuffix + "|";
  bool first = true;
  for (int i = 0; i < TOTAL_COILS; i++) {
    if (coils[i] == 1) {
      if (!first) msg += ",";
      msg += "C" + String(i + coilStartIndex) + "=" + String(inputValues[i]);
      first = false;
    }
  }
  msg += "\n";

  // === ส่งข้อความ ===
  unsigned long tSend = millis();
  size_t sent = client.print(msg);
  unsigned long elapsed = millis() - tSend;

  if (sent > 0) {
    Serial.printf("[SEND OK] %s (took %lu ms)\n", msg.c_str(), elapsed);
  } else {
    Serial.printf("[SEND FAIL] after %lu ms, closing socket\n", elapsed);
    client.stop(); // บังคับ reconnect รอบหน้า
  }
}


void loop() {
  //unsigned long t3 = millis();
  readInputs();
  //Serial.printf("readInputs: %lu ms\n", millis() - t3);

  // unsigned long t2 = millis();
  // checkWiFi();
  // Serial.printf("checkWiFi: %lu ms\n", millis() - t2);


  // unsigned long t4 = millis();
  // if (wifiConnected) sendToReceiver();
  // Serial.printf("sendToReceiver: %lu ms\n", millis() - t4);

  Serial.println("---- loop end ----");
  vTaskDelay(10 / portTICK_PERIOD_MS);  // Run every 0.5s
}


