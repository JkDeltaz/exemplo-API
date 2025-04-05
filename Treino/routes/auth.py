from flask import Blueprint, Flask, redirect, request, render_template, url_for, current_app
import os, json

auth = Blueprint('auth', __name__)

CADASTROS_JSON = "cadastros.json"

def carregar_usuarios():
    if not os.path.exists(CADASTROS_JSON):
        return []

    with open(CADASTROS_JSON, "r", encoding="utf-8") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def salvar_usuarios(usuarios):
    with open(CADASTROS_JSON, "w", encoding='utf-8') as file:
        json.dump(usuarios, file, indent=4, ensure_ascii=False)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in
    if request.method == 'POST':
        ra = request.form['RA']
        password = request.form['password']

        usuarios = carregar_usuarios()

        for usuario in usuarios:
            if usuario['RA'] == ra and usuario['password'] == password:
                logged_in = True
                current_app.config['RA_SESSION'] = usuario['RA']
                return redirect(url_for('atestados_alunos.index'))

    return render_template("login.html")

@auth.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        dados = {'username': request.form['username'],
                 'RA' : request.form['RA'],
                 'password': request.form['password']}


        usuarios = carregar_usuarios()

        for usuario in usuarios:
            if usuario['RA'] == dados['RA']:
                return redirect(url_for('auth.cadastro'))
        
        usuarios.append(dados)
        salvar_usuarios(usuarios)
        return redirect(url_for('auth.login'))
    else:
        return render_template('cadastro.html')

@auth.route('/professor', methods=['GET', 'POST'])
def professor():

    if request.method == 'POST':
        senha = request.form['password']

        if senha == current_app.config['SENHA_PROF']:
            return redirect(url_for("professor.index"))

    return render_template('login_professor.html')