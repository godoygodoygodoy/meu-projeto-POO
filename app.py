from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_bcrypt import Bcrypt
import mysql.connector
import os

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

# ========== ROTAS PÚBLICAS ==========
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/cardapio')
def cardapio():
    cardapio = [
        {"nome": "Nightwing Burguer", "descricao": "Picanha com cheddar, cebola roxa e molho secreto", "preco": 28.90},
        {"nome": "Robin Combo", "descricao": "Smash burger com batata frita e refrigerante", "preco": 22.50},
        {"nome": "Batgirl Veggie", "descricao": "Hambúrguer de grão-de-bico com salada", "preco": 25.00},
        {"nome": "Capuz Vermelho", "descricao": "Duplo bacon com pimenta e atitude", "preco": 30.00}
    ]
    return render_template('cardapio.html', cardapio=cardapio)

# ========== AUTENTICAÇÃO ==========
@app.route('/logar', methods=['POST'])
def logar():
    username = request.form['username']
    senha = request.form['senha']

    cursor.execute("SELECT senha, foto FROM usuarios WHERE username = %s", (username,))
    resultado = cursor.fetchone()

    if resultado and bcrypt.check_password_hash(resultado[0], senha):
        session['usuario'] = username
        session['foto'] = resultado[1]
        return redirect('/home')
    else:
        flash('Usuário ou senha inválidos')
        return redirect('/login')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    username = request.form['username']
    senha = request.form['senha']
    senha_hash = bcrypt.generate_password_hash(senha).decode('utf-8')
    foto = request.files['foto']

    if foto and foto.filename != '':
        caminho = os.path.join('static/perfis', foto.filename)
        foto.save(caminho)
        foto_url = '/' + caminho.replace('\\', '/')
    else:
        foto_url = '/static/coisas/default.png'

    try:
        cursor.execute("INSERT INTO usuarios (username, senha, foto) VALUES (%s, %s, %s)", (username, senha_hash, foto_url))
        conn.commit()
        flash('Conta criada com sucesso!')
        return redirect('/login')
    except:
        flash('Nome de usuário já está em uso.')
        return redirect('/cadastro')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ========== ÁREA LOGADA ==========
@app.route('/home')
def home():
    if 'usuario' in session:
        return render_template('index.html', usuario=session['usuario'], foto=session.get('foto'))
    else:
        return redirect('/login')

# ========== CARRINHO ==========
@app.route('/adicionar_carrinho', methods=['POST'])
def adicionar_carrinho():
    nome = request.form['nome']
    preco = float(request.form['preco'])

    if 'carrinho' not in session:
        session['carrinho'] = []

    session['carrinho'].append({'nome': nome, 'preco': preco})
    flash(f"{nome} adicionado ao carrinho!")
    return redirect('/cardapio')

@app.route('/carrinho')
def carrinho():
    carrinho = session.get('carrinho', [])
    total = sum(item['preco'] for item in carrinho)
    return render_template('carrinho.html', carrinho=carrinho, total=total)

@app.route('/esvaziar_carrinho', methods=['POST'])
def esvaziar_carrinho():
    session['carrinho'] = []
    flash("Carrinho esvaziado!")
    return redirect('/carrinho')

# ========== API DE LANCHES ==========
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

# ========== INÍCIO DOS PEDIDOS ==========
@app.route('/index')
def index():
    if 'usuario' in session:
        return render_template('index.html', usuario=session['usuario'], foto=session.get('foto'))
    else:
        return redirect('/login')

# ========== EXECUÇÃO ==========
if __name__ == '__main__':
    app.run(debug=True)
