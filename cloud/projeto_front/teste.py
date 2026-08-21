from pymongo import MongoClient
import os
from pymongo.errors import ConnectionFailure

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:7054/")
DB_NAME = "COMP_NUVEM"
COLLECTION_NAME = "dadosTempTopico"

try:
    # Aumente o timeout se necessário
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Testa a conexão
    client.admin.command('ping')
    print("Conexão com o MongoDB estabelecida com sucesso!")
    
    db = client[DB_NAME]
    dados = list(db[COLLECTION_NAME].find().sort("timestamp", -1).limit(50))
    print(dados)

except ConnectionFailure as e:
    print(f"Falha na conexão com o MongoDB: {e}")
except Exception as e:
    print(f"Erro inesperado: {e}")
finally:
    if 'client' in locals():
        client.close()