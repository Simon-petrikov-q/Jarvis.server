import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Dicionário global para armazenar conversas na memória do servidor
# Nota: Esta memória apaga se o Render reiniciar o serviço.
memorias = {}

@app.route('/chat', methods=['POST'])
def chat():
    try:
        dados = request.json
        msg_usuario = dados.get('mensagem', '')
        # Usamos o seu ID de utilizador para separar as conversas
        uid = "Simon-Petrikov-q"

        # Se não houver histórico para este utilizador, cria um novo
        if uid not in memorias:
            memorias[uid] = [{"role": "system", "content": "Você é o Killmoon, assistente de Simon-Petrikov-q. Seja direto."}]
        
        # Adiciona a mensagem do utilizador ao histórico local
        memorias[uid].append({"role": "user", "content": msg_usuario})

        # Mantém apenas as últimas 10 mensagens para não sobrecarregar a memória
        if len(memorias[uid]) > 11:
            memorias[uid] = [memorias[uid][0]] + memorias[uid][-10:]

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=memorias[uid]
        )
        
        resposta = completion.choices[0].message.content
        
        # Guarda a resposta da IA no histórico
        memorias[uid].append({"role": "assistant", "content": resposta})

        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
