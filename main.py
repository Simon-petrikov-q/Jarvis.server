import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Conecta ao Cluster "Petrikov" que você criou
MONGO_URI = os.environ.get("MONGO_URI")
db_client = MongoClient(MONGO_URI)
db = db_client['jarvis_db']
collection = db['conversas']

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SENHA_MESTRE = "1234"

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.json
    msg = dados.get('mensagem', '')
    senha = dados.get('senha')
    uid = "Simon-Petrikov-q" # ID fixo para evitar confusão de nomes

    if senha != SENHA_MESTRE:
        return jsonify({"resposta": "ACESSO NEGADO."}), 403

    # Busca o histórico no MongoDB
    doc = collection.find_one({"_id": uid})
    historico = doc['mensagens'] if doc else [{"role": "system", "content": "Você é o Jarvis, assistente do Simon-Petrikov-q."}]
    
    historico.append({"role": "user", "content": msg})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico
        )
        resposta = completion.choices[0].message.content
        historico.append({"role": "assistant", "content": resposta})

        # Salva no MongoDB para o Jarvis nunca mais ter amnésia
        collection.update_one({"_id": uid}, {"$set": {"mensagens": historico}}, upsert=True)

        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
