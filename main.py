from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import requests
import base64

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES DO SISTEMA ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_OWNER = "Simon-Petrikov-q"  # <--- COLOQUE SEU NOME DO GITHUB AQUI
REPO_NAME = "jarvis-server"
SENHA_MESTRE = "1234"

MEMORIA_GLOBAL = {}

def ler_proprio_codigo():
    """O Jarvis lê o arquivo atual para saber como se modificar"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/main.py"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        content = res.json()['content']
        return base64.b64decode(content).decode('utf-8'), res.json()['sha']
    return None, None

def escrever_novo_codigo(novo_conteudo, sha, motivo):
    """O Jarvis envia a nova versão para o GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/main.py"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    conteudo_b64 = base64.b64encode(novo_conteudo.encode()).decode()
    payload = {"message": f"Evolução Jarvis: {motivo}", "content": conteudo_b64, "sha": sha}
    res = requests.put(url, json=payload, headers=headers)
    return res.status_code == 200

@app.route('/chat', methods=['POST'])
def chat():
    dados = request.json
    msg = dados.get('mensagem', '').lower()
    senha = dados.get('senha')
    uid = dados.get('usuario_id', 'default')

    if senha != SENHA_MESTRE:
        return jsonify({"resposta": "ACESSO NEGADO."}), 403

    if uid not in MEMORIA_GLOBAL:
        MEMORIA_GLOBAL[uid] = [{
            "role": "system", 
            "content": "Você é o Jarvis. Você tem acesso ao seu código fonte. Se o usuário pedir para você mudar sua lógica, use a função de escrita após validar o código."
        }]

    # LÓGICA DE AUTO-EVOLUÇÃO
    if "atualize seu código" in msg or "mude sua lógica" in msg:
        codigo_atual, sha_atual = ler_proprio_codigo()
        if codigo_atual:
            # Aqui a IA processa a mudança (Exemplo: mudar a senha ou adicionar saudação)
            # Para este estágio, ele apenas confirma que leu e está pronto.
            return jsonify({"resposta": "Sistemas de leitura online. Eu li meu próprio código e identifiquei a versão. O que deseja que eu altere, senhor?"})

    MEMORIA_GLOBAL[uid].append({"role": "user", "content": msg})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=MEMORIA_GLOBAL[uid]
        )
        resposta = completion.choices[0].message.content
        MEMORIA_GLOBAL[uid].append({"role": "assistant", "content": resposta})
        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
