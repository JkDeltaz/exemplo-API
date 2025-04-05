from flask import Flask, redirect, request, render_template, jsonify, url_for
from routes.auth import auth
from routes.atestados_alunos import atestados_alunos
from routes.professor import professor

app = Flask(__name__)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(atestados_alunos, url_prefix='/atestados_alunos')
app.register_blueprint(professor, url_prefix='/professor')

app.config['RA_SESSION'] = ''
app.config['SENHA_PROF'] = "123"

CADASTROS_JSON = "cadastros.json"

logged_in = False

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))
