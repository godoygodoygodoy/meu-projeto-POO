from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# cria a tabela no banco, se não existir
def criar_tabela():
    conn = sqlite3.connect('lanchesGodoy.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lanches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

criar_tabela()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adicionar', methods=['POST'])
def adicionar():
    data = request.get_json()
    nome = data['nome']
    preco = data['preco']

    conn = sqlite3.connect('lanchesGodoy.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO lanches (nome, preco) VALUES (?, ?)", (nome, preco))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': 'Lanche salvo com sucesso!'})

@app.route('/lanches', methods=['GET'])
def listar():
    conn = sqlite3.connect('lanchesGodoy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT nome, preco FROM lanches")
    lanches = cursor.fetchall()
    conn.close()
    return jsonify([{'nome': nome, 'preco': preco} for nome, preco in lanches])

if __name__ == '__main__':
    app.run(debug=True)
