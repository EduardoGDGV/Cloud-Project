o#include <WiFi.h>
#include <PubSubClient.h>

// Configurações de WiFi
const char* ssid = "";
const char* password = "";

// Configurações MQTT
const char* mqtt_server = "127.0. 0.1";
const int mqtt_port = 1883;
const char* mqtt_topic = "sensor_temperatura"; // Tópico para publicar

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conexão MQTT...");
    
    String clientId = "ESP32Client-Pub-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("conectado");
    } else {
      Serial.print("falha, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Publica uma mensagem a cada 3 segundos
  static unsigned long lastMsg = 0;
  unsigned long now = millis();
  if (now - lastMsg > 3000) {
    lastMsg = now;
    
    // Cria uma mensagem com valor aleatório e timestamp
    String msg = "{\"temp\":" + String(random(20, 30)) + 
                 ",\"umid\":" + String(random(40, 80)) + 
                 ",\"time\":" + String(now) + "}";
    
    Serial.print("Publicando mensagem: ");
    Serial.println(msg);
    
    if (client.publish(mqtt_topic, msg.c_str())) {
      Serial.println("Mensagem publicada com sucesso");
    } else {
      Serial.println("Falha ao publicar mensagem");
    }
  }
}
