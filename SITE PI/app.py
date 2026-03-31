from flask import Flask, render_template, request, redirect, session
import json
import os
from datetime import datetime

def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    dig1 = (soma * 10 % 11) % 10

    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    dig2 = (soma * 10 % 11) % 10

    return cpf[-2:] == f"{dig1}{dig2}"

def ler_json(arquivo):
    if not os.path.exists(arquivo):
        return []
    try:
        with open(arquivo, "r") as f:
            return json.load(f)
    except:
        return []

def salvar_json(arquivo, dados):
    with open(arquivo, "w") as f:
        json.dump(dados, f, indent=4)

app = Flask(__name__)
app.secret_key = "segredo123"

ARQUIVO = "denuncias.json"
ARQUIVO_PERGUNTAS = "perguntas.json"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login-aluno", methods=["GET", "POST"])
def login_aluno():
    if request.method == "POST":
        nome = request.form.get("nome")
        cpf = request.form.get("cpf")

        if not nome or not cpf:
            return render_template("login_aluno.html", erro="Preencha todos os campos")

        if not validar_cpf(cpf):
            return render_template("login_aluno.html", erro="CPF inválido")

        session["aluno"] = True
        session["nome"] = nome
        session["cpf"] = cpf

        return redirect("/dash-aluno")

    return render_template("login_aluno.html")

@app.route("/dash-aluno")
def dash_aluno():
    if not session.get("aluno"):
        return redirect("/login-aluno")

    return render_template("dash_aluno.html")

@app.route("/denunciar", methods=["POST"])
def denunciar():
    if not session.get("aluno"):
        return redirect("/login-aluno")

    titulo = request.form.get("titulo")
    descricao = request.form.get("descricao")

    dados = ler_json(ARQUIVO)

    dados.append({
        "titulo": titulo,
        "descricao": descricao,
        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "status": "Pendente",
        "autor": session.get("nome"),
        "cpf": session.get("cpf")
    })

    salvar_json(ARQUIVO, dados)

    return redirect("/dash-aluno")

@app.route("/login-escola", methods=["GET", "POST"])
def login_escola():
    if request.method == "POST":
        user = request.form.get("usuario")
        senha = request.form.get("senha")

        if user == "admin" and senha == "1234":
            session["admin"] = True
            return redirect("/dash-escola")

    return render_template("login_escola.html")

@app.route("/dash-escola")
def dash_escola():
    if not session.get("admin"):
        return redirect("/login-escola")

    denuncias = ler_json(ARQUIVO)
    perguntas = ler_json(ARQUIVO_PERGUNTAS)

    return render_template("dash_escola.html", denuncias=denuncias, perguntas=perguntas)

@app.route("/enviar-pergunta", methods=["POST"])
def enviar_pergunta():
    pergunta = request.form.get("pergunta")

    dados = ler_json(ARQUIVO_PERGUNTAS)

    dados.append({
        "pergunta": pergunta,
        "resposta": "",
        "data": datetime.now().strftime("%d/%m/%Y %H:%M")
    })

    salvar_json(ARQUIVO_PERGUNTAS, dados)

    return redirect("/perguntas")

@app.route("/responder/<int:id>", methods=["POST"])
def responder(id):
    resposta = request.form.get("resposta")

    dados = ler_json(ARQUIVO_PERGUNTAS)

    if 0 <= id < len(dados):
        dados[id]["resposta"] = resposta

    salvar_json(ARQUIVO_PERGUNTAS, dados)

    return redirect("/dash-escola")

@app.route("/resolver/<int:id>")
def resolver(id):
    dados = ler_json(ARQUIVO)

    if 0 <= id < len(dados):
        dados[id]["status"] = "Resolvido"

    salvar_json(ARQUIVO, dados)

    return redirect("/dash-escola")

@app.route("/perguntas")
def perguntas():
    lista = ler_json(ARQUIVO_PERGUNTAS)
    return render_template("perguntas.html", perguntas=lista)

@app.route("/ajuda-login")
def ajuda_login():
    return render_template("ajuda_login.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)