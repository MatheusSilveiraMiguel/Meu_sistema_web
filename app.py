from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
ARQUIVO = "dividas.json"

def carregar_dados():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_dados(lista):
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(lista, f, indent=2, ensure_ascii=False)

def interpretar_data(data_str):
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d%m%y"]
    for fmt in formatos:
        try:
            return datetime.strptime(data_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Formato de data inválido: {data_str}")

@app.route("/")
def index():
    dividas = carregar_dados()
    return render_template("index.html", dividas=dividas)

@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        vencimento_str = request.form["vencimento"]
        try:
            vencimento_data = interpretar_data(vencimento_str)
        except ValueError as e:
            return f"Erro: {e}", 400

        vencimento_formatado = vencimento_data.strftime("%d/%m/%Y")

        nova_divida = {
            "nome": request.form["nome"],
            "valor": float(request.form["valor"]),
            "vencimento": vencimento_formatado,
            "prioridade": request.form["prioridade"],
            "paga": False
        }

        lista = carregar_dados()
        lista.append(nova_divida)
        salvar_dados(lista)
        return redirect(url_for("index"))
    return render_template("adicionar.html")

@app.route("/pagar/<int:indice>")
def pagar(indice):
    lista = carregar_dados()
    if 0 <= indice < len(lista):
        lista[indice]["paga"] = True
        salvar_dados(lista)
    return redirect(url_for("index"))

@app.route("/excluir/<int:indice>")
def excluir(indice):
    lista = carregar_dados()
    if 0 <= indice < len(lista):
        if lista[indice].get("paga", False):
            lista.pop(indice)
            salvar_dados(lista)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
