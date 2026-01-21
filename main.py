from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# CONFIGURAÇÕES DO PROJETO X
SENHA_MESTRE = "1234" # ALTERE PARA A SENHA QUE DESEJAR
MEMORIA_GLOBAL = {} # Dicionário para guardar conversas de diferentes usuários

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.json
    mensagem_usuario = dados.get('mensagem')
    senha_enviada = dados.get('senha')
    usuario_id = dados.get('usuario_id', 'default') # Para identificar quem está falando

    # 1. VERIFICAÇÃO DE SEGURANÇA
    if senha_enviada != SENHA_MESTRE:
        return jsonify({"resposta": "ACESSO NEGADO. Senha incorreta, senhor."}), 403

    # 2. GESTÃO DE MEMÓRIA (Persistência por sessão)
    if usuario_id not in MEMORIA_GLOBAL:
        MEMORIA_GLOBAL[usuario_id] = [
            {"role": "system", "content": "Você é o Jarvis, assistente pessoal do Projeto X. Personalidade: Sarcástico, ultra-eficiente, leal e técnico. Use termos como 'Senhor' e 'Sistemas Online'."}
        ]

    # Adiciona a nova fala ao histórico
    MEMORIA_GLOBAL[usuario_id].append({"role": "user", "content": mensagem_usuario})

    try:
        # 3. CHAMADA DA IA COM CONTEXTO COMPLETO
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=MEMORIA_GLOBAL[usuario_id]
        )
        
        resposta = completion.choices[0].message.content
        
        # Guarda a resposta do Jarvis na memória para a próxima pergunta
        MEMORIA_GLOBAL[usuario_id].append({"role": "assistant", "content": resposta})
        
        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
