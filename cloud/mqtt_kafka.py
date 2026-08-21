import json
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
from time import sleep
import sys
sys.stdout.reconfigure(line_buffering=True)

sleep(10)

# Configurações MQTT
MQTT_BROKER = 'mosquitto'
MQTT_PORT = 1883
MQTT_TOPIC = 'sensor_temperatura'

# Configurações Kafka
KAFKA_BROKER = 'kafka:9092'
KAFKA_TOPIC = 'sensor_temperatura'

# Inicializa o produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Callback quando o cliente conecta no broker MQTT
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado ao broker MQTT com sucesso")
        client.subscribe(MQTT_TOPIC)
        print(f"📡 Inscrito no tópico: {MQTT_TOPIC}")
    else:
        print(f"❌ Falha na conexão MQTT. Código de erro: {rc}")

# Callback quando uma mensagem MQTT é recebida
def on_message(client, userdata, msg):
    import time
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        print(f"Recebido em: {time.time()} - Dados: {data}")
        producer.send(KAFKA_TOPIC, data)
        producer.flush()  # Força envio imediato ao Kafka
        print(f"Enviado para Kafka em: {time.time()}")
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

# Inicializa o cliente MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

print("🔄 Conectando ao broker MQTT...")
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

# Loop de escuta contínua
try:
    print("🚀 Ponte MQTT → Kafka ativa! Aguardando mensagens...\n")
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    print("⛔ Interrompido pelo usuário.")
finally:
    mqtt_client.disconnect()
    producer.close()
    print("🛑 Conexões encerradas.")
