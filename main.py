import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Conexão com MongoDB
MONGO_URI = os.environ.get("MONGO_URI")
client_mongo = MongoClient(MONGO_URI)
db = client_mongo['jarvis_db']
collection = db['conversas']

client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route('/chat', methods=['POST'])
def chat():
    try:
        dados = request.json
        msg_usuario = dados.get('mensagem', '')
        # Se você não quiser usar senha agora, o código ignora o campo 'senha'
        
        uid = "Simon-Petrikov-q"

        # Recuperar histórico do banco
        doc = collection.find_one({"_id": uid})
        historico = doc['mensagens'] if doc else [{"role": "system", "content": "Você é o Killmoon, assistente de Simon-Petrikov-q."}]
        
        historico.append({"role": "user", "content": msg_usuario})

        # Resposta da IA
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico
        )
        resposta = completion.choices[0].message.content
        
        historico.append({"role": "assistant", "content": resposta})

        # Salvar histórico atualizado
        collection.update_one({"_id": uid}, {"$set": {"mensagens": historico}}, upsert=True)

        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"resposta": f"Erro: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
