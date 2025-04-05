from flask import Blueprint, Flask, redirect, request, render_template, url_for, current_app, send_file
from datetime import datetime, timezone
from uuid import uuid4
from io import BytesIO
import json, os

atestados_alunos = Blueprint('atestados_alunos', __name__)

CADASTROS_JSON = "cadastros.json"
UPLOAD_FOLDER = "uploads"

def get_user_info():
    with open(CADASTROS_JSON, encoding='utf-8') as file:
        cadastros = json.load(file)
        for usuario in cadastros:
            if usuario['RA'] == current_app.config['RA_SESSION']:
                return usuario
    return {}

def pegar_atestado(id):
    usuario = get_user_info()
    for atestado in usuario.keys():
        if 'atestado' in atestado and usuario[atestado]['id'] == id:
            return atestado

@atestados_alunos.route('/index', methods=['POST', 'GET'])
def index():
    usuario = get_user_info()
    if not current_app.config['RA_SESSION']:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        pdf = request.files['pdf']
        c_afastamento = request.form['c_afastamento']
        f_afastamento = request.form['f_afastamento']
        
        os.makedirs(f"uploads/{current_app.config['RA_SESSION']}", exist_ok=True)

        pdf_path = f'uploads/{current_app.config['RA_SESSION']}/{pdf.filename}'
        caminho_pdf = os.path.join(pdf_path)


        pdf.save(caminho_pdf)
        if 'num_arquivos' in usuario.keys():
            usuario['num_arquivos'] += 1
        else:
            usuario['num_arquivos'] = 1

        with open(CADASTROS_JSON, 'r', encoding='utf-8') as file:
            cadastros = json.load(file)
        

        for i, cadastro in enumerate(cadastros):
            if cadastro['RA'] == usuario['RA']:

                if 'num_arquivos' in cadastros[i]:
                    cadastros[i]['num_arquivos'] += 1
                else:
                    cadastros[i]['num_arquivos'] = 1

                pdf_path = f'uploads/{current_app.config['RA_SESSION']}/{pdf.filename}'

                cadastros[i][f'atestado_{usuario['num_arquivos']}'] = {'pdf': pdf_path,
                                                        'id': str(uuid4()),
                                                        'data_criado': str(datetime.now(timezone.utc)).split(' ')[0],
                                                        'status': 'Não Verificado',
                                                        'c_afastamento': c_afastamento,
                                                        'f_afastamento': f_afastamento}
                

        with open(CADASTROS_JSON, 'w', encoding='utf-8') as file:
            json.dump(cadastros, file, indent=4, ensure_ascii=False)
        return redirect(url_for('atestados_alunos.index'))
    
    
    atestados = []
    for item in usuario.keys():
        if 'atestado' in item:
            atestados.append(usuario[item])
                

    return render_template('atestados_alunos.html', atestados=atestados, usuario=usuario)

@atestados_alunos.route('/download/<string:id>')
def download(id):
    usuario = get_user_info()
    atestado = pegar_atestado(id=id)

    file_name = f"Atestado {usuario[atestado]['data_criado']}  {usuario['username']}.pdf"
    path = usuario[atestado]['pdf']
    with open(path, "rb") as file:
        pdf_bytes = BytesIO(file.read())
    return send_file(pdf_bytes, 
                mimetype='application/pdf', 
                as_attachment=True, 
                download_name=file_name)

@atestados_alunos.route('/delete/<string:id>')
def delete(id):
    usuario = get_user_info()
    
    try:
        os.remove(usuario[pegar_atestado(id)]['pdf'])
    except:
        pass

    usuario.pop(pegar_atestado(id))

    cadastros = []
    with open(CADASTROS_JSON, 'r', encoding='utf-8') as file:
        cadastros = json.load(file)

    for cadastro in cadastros:
        if cadastro['RA'] == usuario['RA']:
            continue

    with open(CADASTROS_JSON, 'w', encoding='utf-8') as file:
        json.dump([usuario], file, indent=4, ensure_ascii=False)
    return redirect(url_for('atestados_alunos.index'))


@atestados_alunos.route('/abrir_pdf/<path:pdf>')
def abrir_pdf(pdf):
    return send_file(pdf, mimetype='application/pdf', as_attachment=False)