from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_bcrypt import Bcrypt
import mysql.connector

app = Flask(__name__)
app.secret_key = 'batsegredo123'
bcrypt = Bcrypt(app)

# CONEXÃO COM O BANCO MYSQL (XAMPP)
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='',
    database='batfamily_burguer'
)
cursor = conn.cursor()

# ========== ROTAS DE AUTENTICAÇÃO ==========

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/logar', methods=['POST'])
def logar():
    username = request.form['username']
    senha = request.form['senha']
    
    cursor.execute("SELECT senha FROM usuarios WHERE username = %s", (username,))
    resultado = cursor.fetchone()

    if resultado and bcrypt.check_password_hash(resultado[0], senha):
        session['usuario'] = username
        return redirect('/home')
    else:
        flash('Usuário ou senha inválidos')
        return redirect('/')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    username = request.form['username']
    senha = request.form['senha']
    senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

    try:
        cursor.execute("INSERT INTO usuarios (username, senha) VALUES (%s, %s)", (username, senha_hash))
        conn.commit()
        flash('Conta criada com sucesso!')
        return redirect('/')
    except:
        flash('Nome de usuário já está em uso.')
        return redirect('/cadastro')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/')

# ========== ÁREA LOGADA ==========

@app.route('/home')
def home():
    if 'usuario' in session:
        return render_template('index.html', usuario=session['usuario'])
    else:
        return redirect('/')

# ========== ROTAS DE PEDIDOS COM MYSQL ==========

@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'usuario' not in session:
        return jsonify({'mensagem': 'Acesso negado'}), 403

    data = request.get_json()
    nome = data['nome']
    preco = data['preco']

    cursor.execute("INSERT INTO lanches (nome, preco) VALUES (%s, %s)", (nome, preco))
    conn.commit()
    return jsonify({'mensagem': 'Lanche salvo com sucesso!'})

@app.route('/lanches', methods=['GET'])
def listar():
    cursor.execute("SELECT nome, preco FROM lanches")
    lanches = cursor.fetchall()
    return jsonify([{'nome': nome, 'preco': preco} for nome, preco in lanches])

# ========== PÁGINAS EXTRAS (CARDÁPIO, SOBRE) ==========

@app.route('/cardapio')
def cardapio():
    if 'usuario' in session:
        return render_template('cardapio.html')
    else:
        return redirect('/')

@app.route('/sobre')
def sobre():
    if 'usuario' in session:
        return render_template('sobre.html')
    else:
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)

