from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from views import *
from models import Usuario
from db import db
import hashlib
from flask_migrate import Migrate
import re


app = Flask(__name__)
app.secret_key = 'admim'
#app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:SENHA@localhost:3306/flask_app"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

def hash(txt):
   hash_obj = hashlib.sha256(txt.encode('utf-8'))
   return hash_obj.hexdigest()


lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


def validar_email(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email) is not None


@lm.user_loader
def user_loader(id):
   usuario = db.session.query(Usuario).filter_by(id=id).first()
   return usuario

@app.route('/')
@login_required
def home():
   print('usuario:', current_user.nome)
   return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
 if request.method =='GET':
    return render_template('login.html')
 elif request.method =='POST':
    nome = request.form['usuarioForm']
    senha = request.form['senhaForm']

    user = db.session.query(Usuario).filter_by(nome=nome, senha=hash(senha)).first()
    if not user:
        flash('Nome ou senha incorretos.', 'danger')
        return redirect(url_for('login'))
    
    login_user(user)
    return redirect(url_for('home'))
    




#aba de registrar, nome, valida email senha e coleta as informações
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method =='GET':
        return render_template('registrar.html')
    
    elif request.method == 'POST':
       nome = request.form['usuarioForm']
       
       email = request.form['emailForm']
       if not validar_email(email):
        flash('Email inválido.', 'danger')
        return redirect(url_for('registrar'))
       
       senha = request.form['senhaForm']
       if len(senha) < 6:
        flash('A senha deve ter no mínimo 6 caracteres.', 'danger')
        return redirect(url_for('registrar'))
    
       senha_mestre = request.form['senhaMestreForm']
       SENHA_MESTRE = 'adm'
       if senha_mestre  != SENHA_MESTRE:
        flash('Senha mestre incorreta. Cadastro não autorizado.', 'danger')
        return redirect(url_for('registrar'))


    # Verifica se o usuário ja existe
    existente = db.session.query(Usuario).filter_by(nome=nome).first()
    if existente:
        flash('Nome de usuário já existe. Escolha outro.', 'danger')
        return redirect(url_for('registrar'))



    novo_usuario = Usuario(nome=nome, senha=hash(senha), email=email)
    db.session.add(novo_usuario)
    db.session.commit()
 
    login_user(novo_usuario)
    flash('Conta criada com sucesso!', 'success')
    return redirect(url_for('login'))


#metodo de logout
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('login'))


#dashboard entrada vs saida












if __name__ == "__main__":
   #creiar banco de dados temporario(APAGAR DEPOIS)
   with app.app_context():
    db.create_all()
   app.run(debug=True)