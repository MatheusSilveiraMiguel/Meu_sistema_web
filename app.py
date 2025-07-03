from flask import Flask, render_template, request, redirect, url_for
import json
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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
            "paga": False,
            "repetir": request.form.get("repetir") == "on"
        }

        lista = carregar_dados()
        lista.append(nova_divida)
        salvar_dados(lista)
        return redirect(url_for("index"))
    return render_template("adicionar.html")

@app.route("/vencimentos-proximos")
def vencimentos_proximos():
    hoje = datetime.now()
    limite = hoje + timedelta(days=10)

    lista = carregar_dados()
    proximas = []

    for divida in lista:
        try:
            data = interpretar_data(divida["vencimento"])
            if hoje <= data <= limite and not divida["paga"]:
                proximas.append(divida)
        except:
            continue

    return render_template("proximos.html", dividas=proximas)

@app.route("/pagar/<int:indice>")
def pagar(indice):
    lista = carregar_dados()
    if 0 <= indice < len(lista):
        divida = lista[indice]
        divida["paga"] = True

        # Se ela se repete, cria nova para o próximo mês
        if divida.get("repetir"):
            try:
                data_antiga = interpretar_data(divida["vencimento"])
                nova_data = data_antiga + relativedelta(months=1)
                nova_divida = divida.copy()
                nova_divida["vencimento"] = nova_data.strftime("%d/%m/%Y")
                nova_divida["paga"] = False
                lista.append(nova_divida)
            except:
                pass

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
