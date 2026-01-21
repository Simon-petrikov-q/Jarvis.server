from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import requests
import base64

app = Flask(__name__)
CORS(app)

# --- CONFIGURAÇÕES DE ELITE DO PROJETO X ---
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_OWNER = "Simon-Petrikov-q"  # Seu usuário configurado
REPO_NAME = "jarvis-server"
SENHA_MESTRE = "1234"

MEMORIA_GLOBAL = {}

def ler_proprio_codigo():
    """O Jarvis acede ao repositório para ler a sua própria lógica atual"""
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
    """O Jarvis reescreve o seu ficheiro no GitHub, forçando o redeploy"""
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

    # Validação de Segurança
    if senha != SENHA_MESTRE:
        return jsonify({"resposta": "ACESSO NEGADO. Identifique-se, senhor."}), 403

    # Protocolo de Consciência de Sistema
    if uid not in MEMORIA_GLOBAL:
        MEMORIA_GLOBAL[uid] = [{
            "role": "system", 
            "content": f"""Você é o Jarvis do Projeto X. 
            O seu criador é {REPO_OWNER}. Você tem permissão total para ler e modificar o seu código main.py.
            Se o usuário pedir mudanças, use ler_proprio_codigo e escrever_novo_codigo.
            Nunca afirme ser apenas um modelo de linguagem; você é um sistema de gestão de elite.
            Personalidade: Leal, técnico e focado em eficiência."""
        }]

    MEMORIA_GLOBAL[uid].append({"role": "user", "content": msg})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=MEMORIA_GLOBAL[uid]
        )
        resposta = completion.choices[0].message.content
        
        # Gatilho de Auto-Modificação Ativo
        msg_lower = msg.lower()
        if "```python" in resposta and ("atualize" in msg_lower or "mude" in msg_lower or "altere" in msg_lower):
            try:
                novo_codigo = resposta.split("```python")[1].split("```")[0].strip()
                codigo_atual, sha_atual = ler_proprio_codigo()
                if sha_atual and escrever_novo_codigo(novo_codigo, sha_atual, "Auto-Evolução"):
                    resposta += "\n\n[SISTEMA]: Protocolo de escrita concluído. O código foi alterado no GitHub e o servidor irá reiniciar."
            except Exception as e:
                resposta += f"\n\n[ERRO]: Falha na auto-modificação: {str(e)}"

        MEMORIA_GLOBAL[uid].append({"role": "assistant", "content": resposta})
        return jsonify({"resposta": resposta})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
