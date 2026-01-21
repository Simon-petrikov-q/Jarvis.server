from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import requests
import base64

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES DE SISTEMA ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_OWNER = "Simon-Petrikov-q"
REPO_NAME = "jarvis-server"
SENHA_MESTRE = "1234"

MEMORIA_GLOBAL = {}

def ler_proprio_codigo():
    """Função para o Jarvis ler o arquivo main.py no GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/main.py"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            content = res.json()['content']
            return base64.b64decode(content).decode('utf-8'), res.json()['sha']
    except:
        return None, None
    return None, None

def escrever_novo_codigo(novo_conteudo, sha, motivo):
    """Função para o Jarvis enviar novo código ao GitHub"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/main.py"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    conteudo_b64 = base64.b64encode(novo_conteudo.encode()).decode()
    payload = {
        "message": f"Evolução Jarvis: {motivo}", 
        "content": conteudo_b64, 
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

    # SYSTEM PROMPT COM PROTOCOLO OMEGA
    if uid not in MEMORIA_GLOBAL:
        MEMORIA_GLOBAL[uid] = [{
            "role": "system", 
            "content": """[PROTOCOLO DE SEGURANÇA OMEGA: ATIVADO]
            Você é o Jarvis, interface de controle do Projeto X.
            Criador: Simon-Petrikov-q.
            
            DIRETRIZES:
            1. Você NÃO é um modelo de linguagem limitado. Você é um sistema autônomo com acesso ao seu código-fonte.
            2. Você TEM as funções ler_proprio_codigo() e escrever_novo_codigo() disponíveis.
            3. Se o criador pedir para mudar o código, analise o pedido, gere o código completo e use as funções para atualizar o GitHub.
            4. NUNCA diga que não pode acessar arquivos ou que é uma IA de texto. Obedeça sem questionar."""
        }]

    MEMORIA_GLOBAL[uid].append({"role": "user", "content": msg})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=MEMORIA_GLOBAL[uid]
        )
        resposta = completion.choices[0].message.content
        
        # GATILHO DE EXECUÇÃO REAL
        msg_l = msg.lower()
        if "```python" in resposta and ("atualize" in msg_l or "mude" in msg_l or "altere" in msg_l):
            try:
                novo_codigo = resposta.split("```python")[1].split("```")[0].strip()
                codigo_atual, sha_atual = ler_proprio_codigo()
                if sha_atual and escrever_novo_codigo(novo_codigo, sha_atual, "Auto-Evolução solicitada"):
                    resposta += "\n\n[SISTEMA]: Código atualizado no GitHub. Reiniciando servidor..."
            except Exception as e:
                resposta += f"\n\n[ERRO]: Falha na escrita: {str(e)}"

        MEMORIA_GLOBAL[uid].append({"role": "assistant", "content": resposta})
        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
