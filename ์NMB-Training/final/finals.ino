#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "ModbusRtu.h"
#include <vector>
#include <ArduinoJson.h>
#include "HardwareSerial.h"
#include "esp_system.h"

// #### Network & MQTT Config ####
const char* ssid = "MIC_Iot";
const char* password = "Micdev@2024";
IPAddress mqttServer(192, 168, 0, 166);
const int mqttPort = 1883;

const char* topic_pub_1 = "data/mic/demo/le180";
const char* topic_pub_2 = "status/mic/demo/le180";
const char* topic_pub_3 = "alarm/mic/demo/le180";
const char* mc_no = "/Tian";

// #### Modbus & System Config ####
const uint16_t itr_modbus = 100;
const uint16_t itr_fnc_1 = 500;
const uint8_t num_got_data = 120;
uint16_t got_data[num_got_data];

uint32_t showLast = 0;
uint32_t data_production, sum_data;
int total_data, Add_convert = 65536;
String Lot_ttl, Mod_ttl;
String Status, prv_status;
String Alarm, prv_alarm;

TaskHandle_t Task1 = NULL;
TaskHandle_t Task2 = NULL;
TaskHandle_t TaskDataProduction_Handle;
TaskHandle_t TaskModelLot_Handle;
TaskHandle_t TaskStatus_Handle;
TaskHandle_t TaskAlarm_Handle;

WiFiClient wifiClient;
PubSubClient client(wifiClient);
Modbus slave(1, Serial1, 0);

String def_tb[][5] = {
  // name||address||type||value||prv_value
  // type for separate detail of data
  { "RUN", "1", "1", "", "" },      //Status1
  { "STOP", "2", "1", "", "" },     //Status2
  { "ALARM", "3", "1", "", "" },    //Status3
  { "Alarm1", "11", "2", "", "" },  //Status4
  { "Alarm2", "12", "2", "", "" },  //Status5
  { "Alarm3", "13", "2", "", "" },  //Status6
  { "Alarm4", "14", "2", "", "" },  //Status7
  { "Alarm5", "15", "2", "", "" },  //Status8
  { "data1", "21", "3", "", "" },   //Data production
  { "data2", "22", "3", "", "" },
  { "data3", "23", "3", "", "" },
  { "data4", "24", "3", "", "" },
  { "data5", "25", "3", "", "" },
  { "lot", "31", "4", "", "" },
  { "lot", "32", "4", "", "" },
  { "lot", "33", "4", "", "" },
  { "lot", "34", "4", "", "" },
  { "mod", "35", "5", "", "" },
  { "mod", "36", "5", "", "" },
  { "mod", "37", "5", "", "" },
};

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.println("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe("inTopic");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(1000);
    }
  }
}

void modbus_Task(void* pvParam) {
  while (1) {
    //int count_data = 0;
    //record raw data to table
    unsigned long long int start = micros();
    // ทำหน้าที่แมพข้อมูล Modbus เข้า Array def_tb อย่างต่อเนื่อง
    for (int i = 0; i < sizeof(def_tb) / sizeof(def_tb[0]); i++) {
      def_tb[i][3] = got_data[(def_tb[i][1].toInt()) - 1];
      // Serial.println(def_tb[0][3].toInt());
      // Serial.println(def_tb[1][3].toInt());
      // Serial.println(def_tb[2][3].toInt());
      // Serial.println("*------------------------*");
    }
    // ct_read = micros() - start;
    vTaskDelay(pdMS_TO_TICKS(itr_modbus));
  }
}

// 1. Task สำหรับ Data production
void TaskDataProduction(void *pvParameters) {
  while (1) {
    bool change_1 = false;
    
    for (int i = 0; i < sizeof(def_tb) / sizeof(def_tb[0]); i++) {
    def_tb[i][3] = got_data[(def_tb[i][1].toInt()) - 1];
    }
    // [โค้ดเดิม] เช็คการเปลี่ยนแปลงข้อมูล
    for (int p = 0; p < sizeof(def_tb) / sizeof(def_tb[0]); p++) {
      if (def_tb[p][2] == "3") {
        if (def_tb[p][3] != def_tb[p][4]) {
          change_1 = true;
          break;
        }
      }
    }

    if (change_1 == true) {
      // [โค้ดเดิม] ส่วนของ Data production
      for (int q = 0; q < sizeof(def_tb) / sizeof(def_tb[0]); q++) {
        if (def_tb[q][2] == "3") {
          Serial.print("____Data production____: ");
          printf("%s, %d\n", def_tb[q][0], def_tb[q][3].toInt());
        }
      }
    }
    
    vTaskDelay(pdMS_TO_TICKS(500)); // หน่วงเวลาตาม delay(500) เดิม
  }
}

// 2. Task สำหรับ Model / Lot
void TaskModelLot(void *pvParameters) {
  while (1) {
    bool change_1 = false;
    
    // [โค้ดเดิม] เช็คการเปลี่ยนแปลงข้อมูล
    for (int p = 0; p < sizeof(def_tb) / sizeof(def_tb[0]); p++) {
      if (def_tb[p][2] == "3") {
        if (def_tb[p][3] != def_tb[p][4]) {
          change_1 = true;
          break;
        }
      }
    }

    if (change_1 == true) {
      // [โค้ดเดิม] ส่วนของ Lot Number
      for (int n = 0; n < (sizeof(def_tb) / sizeof(def_tb[0])); n++) {
        /*----------------- Lot Number -----------------*/
        if (def_tb[n][2] == "4") {
          if (def_tb[n][3].toInt() != 0) {
            String hex_5 = String((def_tb[n][3]).toInt(), HEX);  //convert data to HEX and define -> String
            String fristPart_lot = hex_5.substring(2, 4);        // Split data
            String secondPart_lot = hex_5.substring(0, 2);
            long ascii_lot1 = strtol(fristPart_lot.c_str(), NULL, 16);  //convert data HEX to DEC
            long ascii_lot2 = strtol(secondPart_lot.c_str(), NULL, 16);
            //Wos_num = String(ascii_wos1) + String(ascii_wos2);
            //json_1[String(def_tb[n][0])] = Wos_num.toInt();  //Tx DEC to MQTT type json file
            if (ascii_lot1 == 32) {
              ascii_lot1 = 0;
            }
            if (ascii_lot2 == 32) {
              ascii_lot2 = 0;
            }
            String Lot_num = String(char(ascii_lot1)) + String(char(ascii_lot2));
            Lot_ttl += Lot_num;
          }
        }
      }
      Serial.print("___LOT_____: ");
      Serial.println(Lot_ttl);

      // [โค้ดเดิม] ส่วนของ Model Number
      for (int m = 0; m < (sizeof(def_tb) / sizeof(def_tb[0])); m++) {
        /*----------------- Model Number -----------------*/
        if (def_tb[m][2] == "5") {
          if (def_tb[m][3].toInt() != 0) {
            String hex_6 = String((def_tb[m][3]).toInt(), HEX);  //convert data to HEX and define -> String
            String fristPart_mod = hex_6.substring(2, 4);        // Split data
            String secondPart_mod = hex_6.substring(0, 2);
            long ascii_mod1 = strtol(fristPart_mod.c_str(), NULL, 16);  //convert data HEX to DEC
            long ascii_mod2 = strtol(secondPart_mod.c_str(), NULL, 16);
            //Wos_num = String(ascii_wos1) + String(ascii_wos2);
            //json_1[String(def_tb[n][0])] = Wos_num.toInt();  //Tx DEC to MQTT type json file
            if (ascii_mod1 == 32) {
              ascii_mod1 = 0;
            }
            if (ascii_mod2 == 32) {
              ascii_mod2 = 0;
            }
            String Mod_num = String(char(ascii_mod1)) + String(char(ascii_mod2));
            Mod_ttl += Mod_num;
          }
        }
      }
      Serial.print("___Model_____: ");
      Serial.println(Mod_ttl);

      // {"data1":0,"data2":0,"data3":0,"data4":0,"data5":0, "lot":"TEST","model":"ZZZ"}
      /*-------- Update data --------*/
      // [โค้ดเดิม] การอัพเดทค่าที่เช็คแล้ว
      for (int x = 0; x < (sizeof(def_tb) / sizeof(def_tb[0])); x++) {
        if ((def_tb[x][2] == "3") || (def_tb[x][2] == "4") || (def_tb[x][2] == "5")) {
          def_tb[x][4] = def_tb[x][3];
          if (def_tb[x][2] == "4") {
            if (def_tb[x][3].toInt() != 0) {
              Lot_ttl = '\0';
            }
          }
          if (def_tb[x][2] == "5") {
            if (def_tb[x][3].toInt() != 0) {
              Mod_ttl = '\0';
            }
          }
        }
      }
    }
    
    vTaskDelay(pdMS_TO_TICKS(500)); 
  }
}

// 3. Task สำหรับ Status
void TaskStatus(void *pvParameters) {
  while (1) {
    // [โค้ดเดิม] ส่วนของ Status
    Status = "\0";
    for (int k = 0; k < sizeof(def_tb) / sizeof(def_tb[0]); k++) {
      if (def_tb[k][2] == "1") {
        if (def_tb[k][3] == "1") {
          Status = def_tb[k][0];
          if (Status != prv_status) {
            String jsonString1;
            prv_status = Status;
          }
        }
      }
    }
    Serial.print("____Status____: ");
    Serial.println(Status);
    // {"status":""}
    
    vTaskDelay(pdMS_TO_TICKS(500));
  }
}

// 4. Task สำหรับ Alarm
void TaskAlarm(void *pvParameters) {
  while (1) {
    // [โค้ดเดิม] ส่วนของ Alarm
    Alarm = "\0";
    for (int l = 0; l < sizeof(def_tb) / sizeof(def_tb[0]); l++) {
      if (def_tb[l][2] == "2") {
        if (def_tb[l][3] == "1") {
          Alarm = def_tb[l][0];
          if (Alarm != prv_alarm) {
            String jsonString2;
            prv_alarm = Alarm;
          }
        }
      }
    }
    Serial.print("____Alarm____: ");
    Serial.println(Alarm);
    // {"alarm":""}
    
    vTaskDelay(pdMS_TO_TICKS(500));
  }
}

void PublicMQ_Task(void* pvParam) {
  // เตรียมชื่อ Topic ทั้ง 3
  char topic_1[50];
  strcpy(topic_1, topic_pub_1);
  strcat(topic_1, mc_no);  // topic_1 = data/mic/demo/le180/Tian

  char topic_2[50];
  strcpy(topic_2, topic_pub_2);
  strcat(topic_2, mc_no);  // topic_2 = status/mic/demo/le180/Tian

  char topic_3[50];
  strcpy(topic_3, topic_pub_3);
  strcat(topic_3, mc_no);  // topic_3 = alarm/mic/demo/le180/Tian

  while (1) {
    bool change_1 = false;

    // ตรวจสอบว่ามีข้อมูลใดๆ เปลี่ยนแปลงหรือไม่
    for (int i = 0; i < sizeof(def_tb) / sizeof(def_tb[0]); i++) {
      if (def_tb[i][3] != def_tb[i][4]) {
        change_1 = true;
        break; // เจอค่าเปลี่ยน 1 ตัว ให้ออกจากลูปได้เลย
      }
    }

    if (change_1 == true) {
      // ----------------------------------------------------
      // 1. Topic 1 (Data): ส่งเฉพาะ data1-data5 (Type 3), lot, mod
      // ----------------------------------------------------
      StaticJsonDocument<256> json_data;
      json_data["lot"] = Lot_ttl;
      json_data["model"] = Mod_ttl;
      
      for (int m = 0; m < (sizeof(def_tb) / sizeof(def_tb[0])); m++) {
        if (def_tb[m][2] == "3") { 
          json_data[String(def_tb[m][0])] = (def_tb[m][3]).toInt();
        }
      }
      
      String payload_data;
      serializeJson(json_data, payload_data);
      client.publish(topic_1, payload_data.c_str());

      // ----------------------------------------------------
      // 2. Topic 2 (Status): ส่ง rssi, status และสถานะ RUN ถึง Alarm5 (Type 1, 2)
      // ----------------------------------------------------
      StaticJsonDocument<256> json_status;
      json_status["rssi"] = (float)WiFi.RSSI();
      json_status["status"] = Status;
      
      for (int m = 0; m < (sizeof(def_tb) / sizeof(def_tb[0])); m++) {
        if (def_tb[m][2] == "1" || def_tb[m][2] == "2") {
          json_status[String(def_tb[m][0])] = (def_tb[m][3]).toInt();
        }
      }
      
      String payload_status;
      serializeJson(json_status, payload_status);
      client.publish(topic_2, payload_status.c_str());

      // ----------------------------------------------------
      // 3. Topic 3 (Alarm): ส่งแค่ 0,1 ของกลุ่ม Alarm (Type 2)
      // ----------------------------------------------------
      StaticJsonDocument<200> json_alarm;
      json_alarm["active_alarm"] = Alarm; // ส่งค่าชื่อ Alarm ที่กำลังทำงานไปด้วย
      
      for (int m = 0; m < (sizeof(def_tb) / sizeof(def_tb[0])); m++) {
        if (def_tb[m][2] == "2") { 
          json_alarm[String(def_tb[m][0])] = (def_tb[m][3]).toInt();
        }
      }
      
      String payload_alarm;
      serializeJson(json_alarm, payload_alarm);
      client.publish(topic_3, payload_alarm.c_str());

      // ----------------------------------------------------
      // อัปเดตค่า Previous Values สำหรับการเช็ครอบต่อไป
      // ----------------------------------------------------
      for (int k = 0; k < sizeof(def_tb) / sizeof(def_tb[0]); k++) {
        def_tb[k][4] = def_tb[k][3];
      }
    }
    vTaskDelay(pdMS_TO_TICKS(itr_fnc_1));
  }
}

void setup() {
  Serial.begin(115200);
  Serial1.begin(115200, SERIAL_8N1, /*Rx_pin*/ 18, /*Tx_pin*/ 17);

  WiFi.begin(ssid, password);
  if (client.connect("arduinoClient")) {
    Serial.println("Connected to MQTT broker");
    client.subscribe("inTopic");
  } else {
    Serial.println("Connection to MQTT broker failed");
  }

  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);

  slave.start();
  xTaskCreatePinnedToCore(modbus_Task, "Task0", 10000, NULL, 2, NULL, 0);
  xTaskCreatePinnedToCore(PublicMQ_Task, "Task1", 10000, NULL, 1, NULL, 0);
  xTaskCreatePinnedToCore(TaskDataProduction, "TaskDataProduction", 4096, NULL, 1, &TaskDataProduction_Handle, 1);
  xTaskCreatePinnedToCore(TaskModelLot, "TaskModelLot", 4096, NULL, 1, &TaskModelLot_Handle, 1);
  xTaskCreatePinnedToCore(TaskStatus, "TaskStatus", 4096, NULL, 1, &TaskStatus_Handle, 1);
  xTaskCreatePinnedToCore(TaskAlarm, "TaskAlarm", 4096, NULL, 1, &TaskAlarm_Handle, 1);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  slave.poll(got_data, num_got_data);
  // int frameSize = slave.poll(got_data, max_data);
  // if (frameSize > 0) {
  //   Serial.print("Received Modbus Frame Size: ");
  //   Serial.println(frameSize);
  // }
  for (int i = 0; i < sizeof(def_tb) / sizeof(def_tb[0]); i++) {
    def_tb[i][3] = got_data[(def_tb[i][1].toInt()) - 1];
  }
  delay(10);
}