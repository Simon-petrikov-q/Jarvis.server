import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Tenta ligar ao MongoDB com timeout curto para não travar o Render
try:
    MONGO_URI = os.environ.get("MONGO_URI")
    client_mongo = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    db = client_mongo['jarvis_db']
    collection = db['conversas']
    print("Conexão com MongoDB preparada.")
except Exception as e:
    print(f"Aviso: MongoDB offline ou erro de URI: {e}")

client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
SENHA_MESTRE = "1234"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        dados = request.json
        msg = dados.get('mensagem', '')
        senha = dados.get('senha')
        uid = "Simon-Petrikov-q"

        if str(senha) != SENHA_MESTRE:
            return jsonify({"resposta": "ACESSO NEGADO. PIN INCORRETO."}), 403

        # Recuperação de memória
        historico = [{"role": "system", "content": "Você é o Jarvis."}]
        try:
            doc = collection.find_one({"_id": uid})
            if doc: historico = doc['mensagens']
        except:
            print("Erro ao ler banco, usando memória temporária.")

        historico.append({"role": "user", "content": msg})

        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historico
        )
        resposta = completion.choices[0].message.content
        historico.append({"role": "assistant", "content": resposta})

        # Salva se o banco estiver disponível
        try:
            collection.update_one({"_id": uid}, {"$set": {"mensagens": historico}}, upsert=True)
        except:
            pass

        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
