from kafka import KafkaConsumer
from sshtunnel import SSHTunnelForwarder
import time
#Definindo variáveis
SSH_HOST = ''
SSH_PORT = 
SSH_USER = ''
SSH_PASSWORD = ''

KAFKA_REMOTE_HOST = 'localhost'
KAFKA_REMOTE_PORT = 9092
KAFKA_LOCAL_PORT = 9093

TOPICO = 'sensor_temperatura'

# Túnel SSH
tunnel = SSHTunnelForwarder(
    (SSH_HOST, SSH_PORT),
    ssh_username=SSH_USER,
    ssh_password=SSH_PASSWORD,
    remote_bind_address=(KAFKA_REMOTE_HOST, KAFKA_REMOTE_PORT),
    local_bind_address=('localhost', KAFKA_LOCAL_PORT)
)
tunnel.start()
print(f"Túnel SSH ativo: localhost:{KAFKA_LOCAL_PORT} → {KAFKA_REMOTE_HOST}:{KAFKA_REMOTE_PORT}")
time.sleep(3)

# Kafka
consumer = KafkaConsumer(
    TOPICO,
    bootstrap_servers=f'localhost:{KAFKA_LOCAL_PORT}',
    auto_offset_reset='earliest',
    group_id='teste1',
    api_version=(0, 10, 1)  
)

print(f"Conectado ao tópico '{TOPICO}'. Aguardando mensagens...\n")

try:
    for mensagem in consumer:
        print(f"Mensagem recebida: {mensagem.value.decode('utf-8')}")
except KeyboardInterrupt:
    print("Encerrando consumidor.")
finally:
    consumer.close()
    tunnel.stop()
