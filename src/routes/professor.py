from flask import Blueprint, Flask, redirect, request, render_template, url_for, current_app, send_file
from io import BytesIO
import os, json


professor = Blueprint('professor', __name__)

CADASTROS_JSON = "cadastros.json"

def get_user_info(ra):
    with open(CADASTROS_JSON, encoding='utf-8') as file:
        cadastros = json.load(file)
        for usuario in cadastros:
            if usuario['RA'] == ra:
                return usuario
    return {}

def pegar_atestado(ra, id):
    usuario = get_user_info(ra=ra)
    for atestado in usuario.keys():
        if 'atestado' in atestado and usuario[atestado]['id'] == id:
            return atestado

@professor.route('/index', methods=['GET', 'POST'])
def index():
    usuarios = []
    with open(CADASTROS_JSON, 'r', encoding='UTF-8') as file:
        usuarios = json.load(file)
    if request.method == 'POST':
        pesquisa = request.form['Pesquisar']
        classificar = request.form['classificar']
        
        usuarios_filtrados = [usuario for usuario in usuarios if pesquisa in usuario['RA'] or pesquisa.lower() in usuario['username'].lower()]

        if classificar == 'alfabetica':
            usuarios_filtrados = sorted(usuarios_filtrados, key=lambda x: x['username'].lower())


        return render_template("area_professor.html", usuarios=usuarios_filtrados)
    return render_template('area_professor.html', usuarios=usuarios)

@professor.route('/abrir_pdf/<path:pdf>')
def abrir_pdf(pdf):
    return send_file(pdf, mimetype='application/pdf', as_attachment=False)

@professor.route('/download/<string:id>/<string:ra>')
def download(id, ra):
    usuario = get_user_info(ra=ra)
    atestado = pegar_atestado(id=id, ra=ra)

    file_name = f"Atestado {usuario[atestado]['data_criado']}  {usuario['username']}.pdf"
    path = usuario[atestado]['pdf']
    with open(path, "rb") as file:
        pdf_bytes = BytesIO(file.read())
    return send_file(pdf_bytes, 
                mimetype='application/pdf', 
                as_attachment=True, 
                download_name=file_name)

@professor.route('/verificar/<string:id>/<string:ra>/<string:status>')
def verificar(id, ra, status):
    
    with open(CADASTROS_JSON, 'r', encoding='utf-8') as file:
        usuarios = json.load(file)

    usuario_atual = {}
    position = 0
    for i, usuario in enumerate(usuarios):
        if usuario['RA'] == ra:
            usuario_atual = usuario
            position = i

    atestado_atual = ""
    for atestado in usuario_atual:
        if 'atestado' in atestado:
            if usuario_atual[atestado]['id'] != id:
                continue
            atestado_atual = atestado
            break
    
    usuarios[position][atestado_atual]['status'] = status

    with open(CADASTROS_JSON, 'w', encoding='utf-8') as file:
        json.dump(usuarios, file, indent=4, ensure_ascii=False)

    return redirect(url_for('professor.index'))