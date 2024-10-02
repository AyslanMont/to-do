from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from datetime import datetime

login_manager = LoginManager()
load_dotenv()

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_PORT'))
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
app.config['MYSQL_CURSORCLASS'] = os.getenv('MYSQL_CURSORCLASS')
app.config['SECRET_KEY'] = str(os.getenv('SECRET_KEY'))

mysql = MySQL(app)
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, email, senha):
        self.email = email
        self.senha = senha
        self.id = None
    
    @classmethod
    def get(cls, id):
        cursor = mysql.connection.cursor()
        SELECT = "SELECT * FROM tb_usuarios WHERE usu_id = %s"
        cursor.execute(SELECT, (id,))
        dados = cursor.fetchone()
        cursor.close()
        if dados:
            user = User(dados['usu_email'], dados['usu_senha'])
            user.id = dados['usu_id']
            return user
        return None

    @classmethod
    def get_by_email(cls, email):
        cursor = mysql.connection.cursor()
        SELECT = "SELECT * FROM tb_usuarios WHERE usu_email = %s"
        cursor.execute(SELECT, (email,))
        dados = cursor.fetchone()
        cursor.close()
        if dados:
            user = User(dados['usu_email'], dados['usu_senha'])
            user.id = dados['usu_id']
            return user
        return None


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['password']
        user = User.get_by_email(email)
        if user and check_password_hash(user.senha, senha):
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Email ou senha incorretos. Verifique suas credenciais e tente novamente.", "danger")
    
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['password']
        user = User.get_by_email(email)
        senha_hash = generate_password_hash(senha)

        if user:
            flash("O usuário já está cadastrado!", "danger")
        else:
            cursor = mysql.connection.cursor()
            INSERT = "INSERT INTO tb_usuarios (usu_nome, usu_email, usu_senha) VALUES (%s,%s,%s)"
            cursor.execute(INSERT, (nome, email, senha_hash))
            mysql.connection.commit()
            cursor.close()
            flash("Registro efetuado com sucesso! Use suas credenciais para fazer login.", "success")
            return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():

    cursor = mysql.connection.cursor()
    SELECT = "SELECT * FROM tb_tarefas WHERE tar_usu_id = %s"
    cursor.execute(SELECT, (current_user.id,))
    dados = cursor.fetchall()
    if not dados:
        flash("Você ainda não criou nenhuma tarefa.", "warning")

    return render_template("home.html", dados=dados)

@app.route("/criar-tarefa", methods=["GET", "POST"])
@login_required
def criar_tarefa():
    if request.method == "POST":
        titulo =  request.form['titulo']
        descricao =  request.form['descricao']
        data_limite =  request.form['data_limite']
        status =  request.form['status']
        prioridade =  request.form['prioridade']
        categoria =  request.form['categoria']
        data_criacao = datetime.now()

        cursor = mysql.connection.cursor()
        INSERT = "INSERT INTO tb_tarefas (tar_titulo, tar_desc, tar_data_criacao, tar_data_limite, tar_status, tar_prioridade, tar_categoria, tar_usu_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(INSERT, (titulo, descricao, data_criacao, data_limite, status, prioridade, categoria, current_user.id))
        mysql.connection.commit()
        cursor.close()



    return render_template("criar_tarefa.html")

@app.route("/atualizar-tarefa", methods=["GET", "POST"])
@login_required
def atualizar_tarefa():

    if request.method == "POST":
        
        id = request.form['id']
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        data_limite = request.form['data_limite']
        status = request.form['status']

        cursor = mysql.connection.cursor()
        UPDATE = "UPDATE tb_tarefas SET tar_titulo=%s, tar_desc=%s, tar_data_limite=%s, tar_status=%s WHERE tar_id=%s"
        cursor.execute(UPDATE, (titulo, descricao, data_limite, status, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('home'))
    return render_template('atualizar_tarefa.html')

@app.route("/deletar-tarefa/<int:id>", methods=["GET", "POST"])
@login_required
def deletar_tarefa(id):        
    id = id
    cursor = mysql.connection.cursor()
    DELETE = "DELETE FROM tb_tarefas WHERE tar_id=%s"
    cursor.execute(DELETE, (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('home'))