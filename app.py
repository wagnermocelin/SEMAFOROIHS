from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import sqlite3
import secrets
import os
import base64

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
CORS(app, supports_credentials=True)

DATABASE = 'semaforo.db'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            pontos_totais INTEGER DEFAULT 0,
            nivel TEXT DEFAULT 'vermelho',
            ultima_visita TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pontuacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            pontos INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            descricao TEXT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_bar TEXT DEFAULT 'Semáforo Bar',
            logo_path TEXT,
            pontos_vermelho_min INTEGER DEFAULT 0,
            pontos_amarelo_min INTEGER DEFAULT 200,
            pontos_verde_min INTEGER DEFAULT 500,
            senha_admin TEXT DEFAULT 'admin123'
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM configuracoes')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO configuracoes (nome_bar, senha_admin) 
            VALUES ('Semáforo Bar', 'admin123')
        ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_configuracoes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM configuracoes LIMIT 1')
    config = cursor.fetchone()
    conn.close()
    return dict(config) if config else None

def calcular_nivel(pontos):
    config = get_configuracoes()
    if config:
        if pontos >= config['pontos_verde_min']:
            return 'verde'
        elif pontos >= config['pontos_amarelo_min']:
            return 'amarelo'
    else:
        if pontos >= 500:
            return 'verde'
        elif pontos >= 200:
            return 'amarelo'
    return 'vermelho'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, nome, telefone, email, pontos_totais, nivel, 
               data_cadastro, ultima_visita
        FROM clientes
        ORDER BY pontos_totais DESC
    ''')
    clientes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(clientes)

@app.route('/api/clientes', methods=['POST'])
def cadastrar_cliente():
    data = request.json
    nome = data.get('nome')
    telefone = data.get('telefone', '')
    email = data.get('email', '')
    
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clientes (nome, telefone, email)
        VALUES (?, ?, ?)
    ''', (nome, telefone, email))
    conn.commit()
    cliente_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': cliente_id, 'message': 'Cliente cadastrado com sucesso'}), 201

@app.route('/api/clientes/<int:cliente_id>', methods=['GET'])
def obter_cliente(cliente_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,))
    cliente = cursor.fetchone()
    
    if not cliente:
        conn.close()
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    cursor.execute('''
        SELECT * FROM pontuacoes 
        WHERE cliente_id = ? 
        ORDER BY data DESC 
        LIMIT 20
    ''', (cliente_id,))
    historico = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    resultado = dict(cliente)
    resultado['historico'] = historico
    
    return jsonify(resultado)

@app.route('/api/clientes/<int:cliente_id>', methods=['PUT'])
def atualizar_cliente(cliente_id):
    data = request.json
    nome = data.get('nome')
    telefone = data.get('telefone', '')
    email = data.get('email', '')
    
    if not nome:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE clientes 
        SET nome = ?, telefone = ?, email = ?
        WHERE id = ?
    ''', (nome, telefone, email, cliente_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Cliente atualizado com sucesso'})

@app.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
def deletar_cliente(cliente_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pontuacoes WHERE cliente_id = ?', (cliente_id,))
    cursor.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Cliente deletado com sucesso'})

@app.route('/api/pontuacao', methods=['POST'])
def adicionar_pontos():
    data = request.json
    cliente_id = data.get('cliente_id')
    pontos = data.get('pontos', 0)
    tipo = data.get('tipo', 'consumo')
    descricao = data.get('descricao', '')
    
    if not cliente_id or pontos <= 0:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO pontuacoes (cliente_id, pontos, tipo, descricao)
        VALUES (?, ?, ?, ?)
    ''', (cliente_id, pontos, tipo, descricao))
    
    cursor.execute('''
        UPDATE clientes 
        SET pontos_totais = pontos_totais + ?,
            nivel = ?,
            ultima_visita = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (pontos, calcular_nivel(pontos), cliente_id))
    
    cursor.execute('SELECT pontos_totais FROM clientes WHERE id = ?', (cliente_id,))
    resultado = cursor.fetchone()
    pontos_totais = resultado[0] if resultado else 0
    
    cursor.execute('''
        UPDATE clientes 
        SET nivel = ?
        WHERE id = ?
    ''', (calcular_nivel(pontos_totais), cliente_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': 'Pontos adicionados com sucesso',
        'pontos_totais': pontos_totais,
        'nivel': calcular_nivel(pontos_totais)
    })

@app.route('/api/ranking', methods=['GET'])
def ranking():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, nome, pontos_totais, nivel
        FROM clientes
        ORDER BY pontos_totais DESC
        LIMIT 10
    ''')
    ranking = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(ranking)

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM clientes')
    total_clientes = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as total FROM clientes WHERE nivel = "verde"')
    clientes_verde = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as total FROM clientes WHERE nivel = "amarelo"')
    clientes_amarelo = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as total FROM clientes WHERE nivel = "vermelho"')
    clientes_vermelho = cursor.fetchone()[0]
    
    cursor.execute('SELECT SUM(pontos) as total FROM pontuacoes')
    pontos_distribuidos = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return jsonify({
        'total_clientes': total_clientes,
        'clientes_verde': clientes_verde,
        'clientes_amarelo': clientes_amarelo,
        'clientes_vermelho': clientes_vermelho,
        'pontos_distribuidos': pontos_distribuidos
    })

@app.route('/api/configuracoes', methods=['GET'])
def obter_configuracoes():
    config = get_configuracoes()
    if config:
        config.pop('senha_admin', None)
    return jsonify(config or {})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    senha = data.get('senha')
    
    config = get_configuracoes()
    if config and config['senha_admin'] == senha:
        session['admin'] = True
        return jsonify({'success': True, 'message': 'Login realizado com sucesso'})
    
    return jsonify({'success': False, 'message': 'Senha incorreta'}), 401

@app.route('/api/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin', None)
    return jsonify({'success': True})

@app.route('/api/admin/configuracoes', methods=['PUT'])
def atualizar_configuracoes():
    if not session.get('admin'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.json
    nome_bar = data.get('nome_bar')
    pontos_vermelho_min = data.get('pontos_vermelho_min', 0)
    pontos_amarelo_min = data.get('pontos_amarelo_min', 200)
    pontos_verde_min = data.get('pontos_verde_min', 500)
    senha_admin = data.get('senha_admin')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if senha_admin:
        cursor.execute('''
            UPDATE configuracoes 
            SET nome_bar = ?, pontos_vermelho_min = ?, 
                pontos_amarelo_min = ?, pontos_verde_min = ?,
                senha_admin = ?
            WHERE id = 1
        ''', (nome_bar, pontos_vermelho_min, pontos_amarelo_min, pontos_verde_min, senha_admin))
    else:
        cursor.execute('''
            UPDATE configuracoes 
            SET nome_bar = ?, pontos_vermelho_min = ?, 
                pontos_amarelo_min = ?, pontos_verde_min = ?
            WHERE id = 1
        ''', (nome_bar, pontos_vermelho_min, pontos_amarelo_min, pontos_verde_min))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Configurações atualizadas com sucesso'})

@app.route('/api/admin/upload-logo', methods=['POST'])
def upload_logo():
    if not session.get('admin'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    if 'logo' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['logo']
    
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f'logo_{timestamp}_{filename}'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logo_path = f'/static/uploads/{filename}'
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('UPDATE configuracoes SET logo_path = ? WHERE id = 1', (logo_path,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'logo_path': logo_path})
    
    return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
