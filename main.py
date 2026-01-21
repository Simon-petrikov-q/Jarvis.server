import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from pymongo import MongoClient

app = Flask(__name__)
# CORS configurado para aceitar pedidos do seu domínio GitHub
CORS(app, resources={r"/*": {"origins": "https://simon-petrikov-q.github.io"}})

client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
PIN_SISTEMA = "1234"

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200
        
    try:
        dados = request.json
        msg = dados.get('mensagem', '')
        pin = str(dados.get('senha', ''))

        if pin != PIN_SISTEMA:
            return jsonify({"resposta": "PIN INVÁLIDO. ACESSO NEGADO."}), 403

        # Resposta direta para teste de estabilidade
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Você é o Killmoon."}, {"role": "user", "content": msg}]
        )
        
        return jsonify({"resposta": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"resposta": f"Erro no Killmoon: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
