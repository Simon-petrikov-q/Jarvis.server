import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
# Permite que o seu site no GitHub fale com este servidor
CORS(app)

client_groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
PIN_SISTEMA = "1234"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        dados = request.json
        msg = dados.get('mensagem', '')
        pin = str(dados.get('senha', ''))

        if pin != PIN_SISTEMA:
            return jsonify({"resposta": "ACESSO NEGADO. PIN INCORRETO."}), 403

        # Chamada para o modelo Llama
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Você é o Killmoon, assistente de Simon-Petrikov-q."},
                {"role": "user", "content": msg}
            ]
        )
        
        return jsonify({"resposta": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"resposta": f"Erro no Killmoon: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
