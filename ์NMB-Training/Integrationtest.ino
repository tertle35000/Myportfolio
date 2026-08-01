#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// ================================================================
// CONFIGURATION SELECTION
// Set to true  -> Use Modbus TCP (Ethernet)
// Set to false -> Use Modbus RTU (RS485 Serial)
// ================================================================
#define USE_MODBUS_TCP true

// WiFi & MQTT Settings
const char* ssid = "MIC_Iot";
const char* password = "Micdev@2024";
const char* mqtt_server = "192.168.0.208";

// Modbus Data Buffer (Shared between RTU and TCP modes)
uint16_t au16data[20] = {0};

#if USE_MODBUS_TCP
  // --- Modbus TCP Libraries & Config ---
  #include <SPI.h>
  #include <EthernetENC.h>
  #include <ModbusEthernet.h>

  byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
  IPAddress ip(192, 168, 3, 17);
  ModbusEthernet mb;
  EthernetServer server(502);

#else
  // --- Modbus RTU Libraries & Config ---
  #include <ModbusRtu.h>

  #define RX_PIN 18
  #define TX_PIN 17
  #define SLAVE_ID 1

  Modbus slave(SLAVE_ID, Serial1, 0); // Slave ID 1, Serial1, Dere/Rts pin 0
#endif

// MQTT Setup
WiFiClient espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

  if ((char)payload[0] == '1') {
    digitalWrite(BUILTIN_LED, LOW);
  } else {
    digitalWrite(BUILTIN_LED, HIGH);
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.publish("outTopic", "hello world");
      client.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  pinMode(BUILTIN_LED, OUTPUT);
  Serial.begin(115200);

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

#if USE_MODBUS_TCP
  Serial.println("Initializing Modbus TCP (Ethernet)...");
  Ethernet.init(10);        // CS/SS pin
  Ethernet.begin(mac, ip);
  delay(1000);

  mb.server();
  server.begin();
  // Register Holding Registers 0 - 19
  for (int i = 0; i < 20; i++) {
    mb.addReg(HREG(i));
  }
  Serial.println("Modbus TCP Server Ready");

#else
  Serial.println("Initializing Modbus RTU (Serial)...");
  Serial1.begin(115200, SERIAL_8N1, RX_PIN, TX_PIN);
  slave.start();
  Serial.println("Modbus RTU Slave Ready");
#endif
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

#if USE_MODBUS_TCP
  // Process Modbus TCP Server tasks & sync HREG to au16data array
  mb.task();
  for (int i = 0; i < 20; i++) {
    au16data[i] = mb.Hreg(i);
  }

#else
  // Process Modbus RTU Slave tasks
  slave.poll(au16data, 20);
#endif

  // Send MQTT Telemetry Data every 2 seconds
  unsigned long now = millis();
  if (now - lastMsg > 2000) {
    lastMsg = now;

    // --- MAP DATA FROM ARRAY (Index 0 - 19) ---
    uint16_t status1 = au16data[0];
    uint16_t status2 = au16data[1];
    uint16_t status3 = au16data[2];

    bool lamp1 = au16data[3];
    bool lamp2 = au16data[4];
    bool lamp3 = au16data[5];
    bool lamp4 = au16data[6];
    bool lamp5 = au16data[7];

    uint16_t data1 = au16data[8];
    uint16_t data2 = au16data[9];
    uint16_t data3 = au16data[10];
    uint16_t data4 = au16data[11];
    uint16_t data5 = au16data[12];

    uint16_t lot1 = au16data[13];
    uint16_t lot2 = au16data[14];
    uint16_t lot3 = au16data[15];

    uint16_t model1 = au16data[16];
    uint16_t model2 = au16data[17];
    uint16_t model3 = au16data[18];
    uint16_t model4 = au16data[19];

    // --- PUBLISH MQTT JSON (สำหรับ ArduinoJson v6) ---
    StaticJsonDocument<512> doc;
    String json_payload;

    // 1. Group: Status
    JsonObject statusObj = doc.createNestedObject("Status");
    statusObj["mode"] = USE_MODBUS_TCP ? "TCP" : "RTU";
    statusObj["s1"]   = status1;
    statusObj["s2"]   = status2;
    statusObj["s3"]   = status3;

    // 2. Group: Alarm
    JsonObject alarmObj = doc.createNestedObject("Alarm");
    alarmObj["lamp1"] = lamp1;
    alarmObj["lamp2"] = lamp2;
    alarmObj["lamp3"] = lamp3;
    alarmObj["lamp4"] = lamp4;
    alarmObj["lamp5"] = lamp5;

    // 3. Group: Data
    JsonObject dataObj = doc.createNestedObject("Data");
    dataObj["d1"]    = data1;
    dataObj["d2"]    = data2;
    dataObj["d3"]    = data3;
    dataObj["d4"]    = data4;
    dataObj["d5"]    = data5;
    dataObj["lot"]   = lot1 + lot2 + lot3;
    dataObj["model"] = model1 + model2 + model3 + model4;

    serializeJson(doc, json_payload);
    client.publish("A/B/C/outTopic", json_payload.c_str());
  }
}