#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <SoftwareSerial.h>

#define trigPin D5
#define echoPin D6
SoftwareSerial dfPlayerSerial(D1, D2); // RX, TX to DFPlayer

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverIP = "YOUR_IP_ADDRESS";  // <-- CHANGE THIS TO YOUR PC's IP
const int serverPort = 5000;

void sendDFPlayerCommand(uint8_t fileNumber) {
  dfPlayerSerial.write(0x7E); // Start byte
  dfPlayerSerial.write(0xFF);
  dfPlayerSerial.write(0x06);
  dfPlayerSerial.write(0x03); // Play track
  dfPlayerSerial.write(0x00);
  dfPlayerSerial.write(0x00);
  dfPlayerSerial.write(fileNumber); // Track number (e.g., 1.mp3 = 0x01)
  dfPlayerSerial.write(0xEF); // End byte
}

void sendToServer(String message) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = "http://" + String(serverIP) + ":" + String(serverPort) + "/echo";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    String payload = "{\"message\":\"" + message + "\"}";
    http.POST(payload);
    http.end();
  }
}

void setup() {
  Serial.begin(115200);           
  dfPlayerSerial.begin(9600);     

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void loop() {
  // 1. Handle detection input from ESP32-CAM
  if (Serial.available()) {
    String label = Serial.readStringUntil('\n');
    label.trim();

    if (label == "Object: Person Left") {
      sendDFPlayerCommand(1);
      sendToServer("Person Left");
    } else if (label == "Object: Car Right") {
      sendDFPlayerCommand(2);
      sendToServer("Car Right");
    }
    // Add more mappings as needed
  }

  // 2. Handle obstacle detection
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  float distance = duration * 0.034 / 2;

  if (distance < 100 && distance > 2) {
    sendDFPlayerCommand(3); // Obstacle alert
    sendToServer("Obstacle ahead");
    delay(2000);
  }

  delay(100);
}
