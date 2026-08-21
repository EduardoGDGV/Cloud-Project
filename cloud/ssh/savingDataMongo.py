from pymongo import MongoClient
from datetime import datetime
import random
import time

# ====== CONFIGURAÇÃO DO MONGODB ======
MONGO_URI = ''  # ou sua string do MongoDB Atlas
DB_NAME = 'COMP_NUVEM'
COLLECTION_NAME = 'dadosTempTopico'

# ====== CONEXÃO COM O MONGODB ======
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
colecao = db[COLLECTION_NAME]

# ====== SIMULAÇÃO DE DADOS ======
for i in range(5):  # Inserir 5 registros de teste
    dado_simulado = {
        "temperatura": round(random.uniform(20.0, 30.0), 2),
        "umidade": round(random.uniform(40.0, 80.0), 2),
        "timestamp": datetime.utcnow().isoformat()
    }

    print(f"Inserindo no MongoDB: {dado_simulado}")
    colecao.insert_one(dado_simulado)
    time.sleep(1)  # Espera 1 segundo entre as inserções
