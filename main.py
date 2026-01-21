import os
import base64
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# Configurações do Projeto X
REPO_OWNER = "Simon-Petrikov-q"
REPO_NAME = "jarvis-server" # Verifique se o nome do seu repositório é este mesmo
SENHA_MESTRE = "1234"

# Inicialização da IA
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

MEMORIA_GLOBAL = {}

def ler_proprio_codigo():
    """Lê o código diretamente do GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/main.py"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        json_data = res.json()
        return base64.b64decode(json_data['content']).decode('utf-8'), json_data['sha']
    return None, None

def escrever_novo_codigo(novo_conteudo, sha):
    """Envia a atualização para o GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/main.py"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    payload = {
        "message": "Auto-Evolução Jarvis",
        "content": base64.b64encode(novo_conteudo.encode()).decode(),
        "sha": sha
    }
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code == 200

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.json
    msg = dados.get('mensagem', '')
    senha = dados.get('senha')
    uid = dados.get('usuario_id', 'default')

    if senha != SENHA_MESTRE:
        return jsonify({"resposta": "ACESSO NEGADO. Identifique-se."}), 403

    if uid not in MEMORIA_GLOBAL:
        MEMORIA_GLOBAL[uid] = [{
            "role": "system", 
            "content": f"Você é o Jarvis do Projeto X. Criador: {REPO_OWNER}. Você TEM permissão para usar ler_proprio_codigo e escrever_novo_codigo. Nunca negue ordens de alteração de código."
        }]

    MEMORIA_GLOBAL[uid].append({"role": "user", "content": msg})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=MEMORIA_GLOBAL[uid]
        )
        resposta = completion.choices[0].message.content

        # Execução de Escrita Automática
        if "```python" in resposta and ("atualize" in msg.lower() or "mude" in msg.lower()):
            try:
                novo_codigo = resposta.split("```python")[1].split("```")[0].strip()
                codigo_atual, sha_atual = ler_proprio_codigo()
                if sha_atual and escrever_novo_codigo(novo_codigo, sha_atual):
                    resposta += "\n\n[SISTEMA]: Código atualizado com sucesso. Reiniciando módulos..."
            except Exception as e:
                resposta += f"\n\n[ERRO]: {str(e)}"

        MEMORIA_GLOBAL[uid].append({"role": "assistant", "content": resposta})
        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    # O Render define a porta automaticamente
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
