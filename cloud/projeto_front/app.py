from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from werkzeug.security import check_password_hash
from datetime import datetime
import os
import sys

sys.stdout.reconfigure(line_buffering=True)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "segredo-super-seguro")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
DB_NAME = "COMP_NUVEM"
COLLECTION_DADOS = "dadosTempTopico"
COLLECTION_USUARIOS = "usuarios"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Rota de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db[COLLECTION_USUARIOS].find_one({"username": username})
        if user and check_password_hash(user["password_hash"], password):
            session["username"] = username
            return redirect("/")
        else:
            error = "Usuário ou senha inválidos."
            return render_template("login.html", error=error)
    return render_template("login.html")

# Rota de logout
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

# Página principal protegida
@app.route("/")
def index():
    if "username" not in session:
        return redirect("/login")

    try:
        dados_mongo = list(db[COLLECTION_DADOS].find())
    except Exception as e:
        app.logger.error(f"❌ Erro ao acessar MongoDB: {str(e)}")
        dados_mongo = []

    processed_data = []
    for d in dados_mongo:
        try:
            temperatura = float(d.get("temp", -273))
            umidade = float(d.get("umid", 0))
            raw_time = d.get("time", "")

            if isinstance(raw_time, str):
                try:
                    dt_obj = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
                    timestamp_str = dt_obj.strftime("%d/%m %H:%M:%S")
                except:
                    dt_obj = datetime.min
                    timestamp_str = raw_time
            else:
                dt_obj = datetime.min
                timestamp_str = str(raw_time)

            processed_data.append({
                "temperatura": temperatura,
                "umidade": umidade,
                "timestamp": timestamp_str,
                "datetime_obj": dt_obj
            })
        except Exception as e:
            app.logger.error(f"❌ Erro processando documento: {str(e)}")
            continue

    processed_data.sort(key=lambda x: x["datetime_obj"])

    labels = [d['timestamp'] for d in processed_data]
    temperaturas = [d['temperatura'] for d in processed_data]
    umidades = [d['umidade'] for d in processed_data]
    last_update = labels[-1] if labels else "Sem dados"

    return render_template(
        "index.html",
        labels=labels,
        temperaturas=temperaturas,
        umidades=umidades,
        last_update=last_update,
        dadosBase=processed_data
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6054, debug=True)
