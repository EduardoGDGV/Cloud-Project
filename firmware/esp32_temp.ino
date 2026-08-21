#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT22.h>
#include <time.h>

#define PIN_DATA 27
DHT22 dht22(PIN_DATA);

// Configurações WiFi
const char* ssid = "";
const char* password = "";

// Configurações MQTT
const char* mqtt_server = "";
const int mqtt_port = 5054;
const char* mqtt_topic = "sensor_temperatura";

WiFiClient espClient;
PubSubClient client(espClient);

// Configuração do NTP
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -3 * 3600; // Horário de Brasília (UTC-3)
const int daylightOffset_sec = 0;

void setup_wifi() {
  delay(10);
  Serial.println("Conectando ao WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi conectado");
  Serial.println(WiFi.localIP());
}

void initTime() {
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) {
    Serial.println("⏳ Aguardando sincronização NTP...");
    delay(1000);
  }
  Serial.println("⏰ Tempo sincronizado com NTP");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conexão MQTT...");
    String clientId = "ESP32Client-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("conectado");
    } else {
      Serial.print("falha, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  initTime();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) reconnect();
  client.loop();

  static unsigned long lastMsg = 0;
  unsigned long now = millis();
  if (now - lastMsg > 10000) {
    lastMsg = now;
    float t = dht22.getTemperature();
    float h = dht22.getHumidity();

    // Pega tempo formatado
    struct tm timeinfo;
    getLocalTime(&timeinfo);
    char timeStr[25];
    strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", &timeinfo);

    // Mensagem JSON com timestamp em string real
    String msg = "{\"temp\":" + String(t) +
                 ",\"umid\":" + String(h) +
                 ",\"time\":\"" + String(timeStr) + "\"}";

    Serial.println("Publicando: " + msg);

    if (client.publish(mqtt_topic, msg.c_str())) {
      Serial.println("✅ Mensagem publicada");
    } else {
      Serial.println("❌ Falha ao publicar");
    }
  }
}
