import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Configuração estável do MongoDB
try:
    MONGO_URI = os.environ.get("MONGO_URI")
    client_mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client_mongo['jarvis_db']
    collection = db['conversas']
except Exception as e:
    print(f"Erro MongoDB: {e}")

client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SENHA_MESTRE = "1234"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        dados = request.json
        msg = dados.get('mensagem', '')
        senha = str(dados.get('senha', ''))
        uid = "Simon-Petrikov-q"

        if senha != SENHA_MESTRE:
            return jsonify({"resposta": "ACESSO NEGADO. DIGITE O PIN CORRETO."}), 403

        # Memória do Killmoon
        historico = [{"role": "system", "content": "Você é o Killmoon, assistente direto de Simon-Petrikov-q."}]
        try:
            doc = collection.find_one({"_id": uid})
            if doc: historico = doc['mensagens']
        except: pass

        historico.append({"role": "user", "content": msg})

        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico
        )
        resposta = completion.choices[0].message.content
        historico.append({"role": "assistant", "content": resposta})

        try:
            collection.update_one({"_id": uid}, {"$set": {"mensagens": historico}}, upsert=True)
        except: pass

        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"resposta": f"Erro: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
