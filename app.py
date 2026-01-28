from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import psycopg2
import psycopg2.extras
import secrets
import os
import base64
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(16))
CORS(app, supports_credentials=True)

# Configuração do banco de dados
DATABASE_URL = os.getenv('POSTGRES_URL', os.getenv('DATABASE_URL', ''))
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'svg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db():
    """Conecta ao PostgreSQL usando a URL do Supabase"""
    try:
        if not DATABASE_URL:
            raise Exception("DATABASE_URL não configurada. Configure POSTGRES_URL ou DATABASE_URL nas variáveis de ambiente.")
        
        # Adicionar sslmode=require na URL se não estiver presente
        url = DATABASE_URL
        if '?' not in url:
            url += '?sslmode=require'
        elif 'sslmode' not in url:
            url += '&sslmode=require'
        
        print(f"Tentando conectar ao banco... (URL configurada: {'Sim' if DATABASE_URL else 'Não'})")
        conn = psycopg2.connect(url)
        print("✅ Conexão com banco estabelecida com sucesso!")
        return conn
    except Exception as e:
        print(f"❌ ERRO DE CONEXÃO: {e}")
        print(f"DATABASE_URL configurada: {'Sim' if DATABASE_URL else 'Não'}")
        print(f"Tipo de erro: {type(e).__name__}")
        raise

def dict_cursor(conn):
    """Retorna um cursor que retorna dicionários em vez de tuplas"""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

def init_db():
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            telefone VARCHAR(20),
            email VARCHAR(255),
            senha VARCHAR(255),
            data_cadastro TIMESTAMP DEFAULT NOW(),
            pontos_totais INTEGER DEFAULT 0,
            nivel VARCHAR(20) DEFAULT 'vermelho',
            ultima_visita TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pontuacoes (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER NOT NULL,
            pontos INTEGER NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            descricao TEXT,
            data TIMESTAMP DEFAULT NOW(),
            data_validade TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            id SERIAL PRIMARY KEY,
            nome_bar VARCHAR(255) DEFAULT 'Semáforo Bar',
            logo_path TEXT,
            pontos_vermelho_min INTEGER DEFAULT 0,
            pontos_amarelo_min INTEGER DEFAULT 200,
            pontos_verde_min INTEGER DEFAULT 500,
            senha_admin VARCHAR(255) DEFAULT 'admin123'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            descricao TEXT,
            pontos INTEGER NOT NULL,
            ativo INTEGER DEFAULT 1,
            data_cadastro TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solicitacoes_pontos (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER DEFAULT 1,
            pontos_total INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            observacao TEXT,
            data_solicitacao TIMESTAMP DEFAULT NOW(),
            data_validacao TIMESTAMP,
            validado_por VARCHAR(255),
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
            FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkins (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER NOT NULL,
            data_checkin TIMESTAMP DEFAULT NOW(),
            localizacao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM configuracoes')
    count = cursor.fetchone()[0]
    if count == 0:
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
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('SELECT * FROM configuracoes LIMIT 1')
    config = cursor.fetchone()
    conn.close()
    return dict(config) if config else None

def calcular_pontos_validos(cliente_id):
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    cursor.execute('''
        SELECT SUM(pontos) as total
        FROM pontuacoes
        WHERE cliente_id = %s
        AND (data_validade IS NULL OR data_validade > NOW())
    ''', (cliente_id,))
    
    resultado = cursor.fetchone()
    conn.close()
    
    return resultado[0] if resultado[0] else 0

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

def calcular_pontos_frequencia(cliente_id):
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    cursor.execute('''
        SELECT COUNT(DISTINCT DATE(data_checkin)) as dias_visitados
        FROM checkins
        WHERE cliente_id = %s
        AND data_checkin >= NOW() - INTERVAL '30 days'
    ''', (cliente_id,))
    
    resultado = cursor.fetchone()
    dias_visitados = resultado[0] if resultado[0] else 0
    
    pontos_bonus = 0
    if dias_visitados >= 20:
        pontos_bonus = 100
    elif dias_visitados >= 15:
        pontos_bonus = 75
    elif dias_visitados >= 10:
        pontos_bonus = 50
    elif dias_visitados >= 5:
        pontos_bonus = 25
    
    conn.close()
    return pontos_bonus, dias_visitados

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de diagnóstico para verificar status da aplicação"""
    try:
        # Testar conexão com banco
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'database_url_configured': bool(DATABASE_URL),
            'message': 'Aplicação funcionando corretamente'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'database_url_configured': bool(DATABASE_URL),
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/debug/tables', methods=['GET'])
def debug_tables():
    """Endpoint para verificar status das tabelas"""
    try:
        conn = get_db()
        cursor = dict_cursor(conn)
        
        # Verificar quais tabelas existem
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tabelas = [row['table_name'] for row in cursor.fetchall()]
        
        # Contar registros em cada tabela
        contagens = {}
        for tabela in tabelas:
            try:
                cursor.execute(f'SELECT COUNT(*) as total FROM {tabela}')
                contagens[tabela] = cursor.fetchone()['total']
            except:
                contagens[tabela] = 'erro'
        
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'tabelas_existentes': tabelas,
            'contagem_registros': contagens
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/debug/estatisticas', methods=['GET'])
def debug_estatisticas():
    """Endpoint para testar query de estatísticas passo a passo"""
    try:
        conn = get_db()
        cursor = dict_cursor(conn)
        
        resultados = {}
        
        # Teste 1: Contar total de clientes
        try:
            cursor.execute('SELECT COUNT(*) as total FROM clientes')
            resultados['total_clientes'] = cursor.fetchone()['total']
        except Exception as e:
            resultados['total_clientes'] = f'ERRO: {str(e)}'
        
        # Teste 2: Contar clientes verdes
        try:
            cursor.execute("SELECT COUNT(*) as total FROM clientes WHERE nivel = 'verde'")
            resultados['clientes_verde'] = cursor.fetchone()['total']
        except Exception as e:
            resultados['clientes_verde'] = f'ERRO: {str(e)}'
        
        # Teste 3: Contar clientes amarelos
        try:
            cursor.execute("SELECT COUNT(*) as total FROM clientes WHERE nivel = 'amarelo'")
            resultados['clientes_amarelo'] = cursor.fetchone()['total']
        except Exception as e:
            resultados['clientes_amarelo'] = f'ERRO: {str(e)}'
        
        # Teste 4: Contar clientes vermelhos
        try:
            cursor.execute("SELECT COUNT(*) as total FROM clientes WHERE nivel = 'vermelho'")
            resultados['clientes_vermelho'] = cursor.fetchone()['total']
        except Exception as e:
            resultados['clientes_vermelho'] = f'ERRO: {str(e)}'
        
        # Teste 5: Somar pontos
        try:
            cursor.execute('SELECT SUM(pontos) as total FROM pontuacoes')
            result = cursor.fetchone()
            resultados['pontos_distribuidos'] = result['total'] if result['total'] else 0
        except Exception as e:
            resultados['pontos_distribuidos'] = f'ERRO: {str(e)}'
        
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'resultados': resultados
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@app.route('/api/clientes', methods=['GET'])
def listar_clientes():
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
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
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('''
        INSERT INTO clientes (nome, telefone, email)
        VALUES (%s, %s, %s)
    ''', (nome, telefone, email))
    conn.commit()
    cliente_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': cliente_id, 'message': 'Cliente cadastrado com sucesso'}), 201

@app.route('/api/clientes/<int:cliente_id>', methods=['GET'])
def obter_cliente(cliente_id):
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
    cliente = cursor.fetchone()
    
    if not cliente:
        conn.close()
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    cursor.execute('''
        SELECT * FROM pontuacoes 
        WHERE cliente_id = %s 
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
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('''
        UPDATE clientes 
        SET nome = %s, telefone = ?, email = ?
        WHERE id = %s
    ''', (nome, telefone, email, cliente_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Cliente atualizado com sucesso'})

@app.route('/api/clientes/<int:cliente_id>', methods=['DELETE'])
def deletar_cliente(cliente_id):
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('DELETE FROM pontuacoes WHERE cliente_id = %s', (cliente_id,))
    cursor.execute('DELETE FROM clientes WHERE id = %s', (cliente_id,))
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
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    cursor.execute('''
        INSERT INTO pontuacoes (cliente_id, pontos, tipo, descricao, data_validade)
        VALUES (%s, %s, %s, %s, NOW() + INTERVAL '90 days')
    ''', (cliente_id, pontos, tipo, descricao))
    
    pontos_validos = calcular_pontos_validos(cliente_id)
    pontos_bonus, dias_visitados = calcular_pontos_frequencia(cliente_id)
    
    if pontos_bonus > 0:
        cursor.execute('''
            INSERT INTO pontuacoes (cliente_id, pontos, tipo, descricao, data_validade)
            VALUES (%s, %s, 'frequencia', %s, NOW() + INTERVAL '90 days')
        ''', (cliente_id, pontos_bonus, f'Bônus de frequência: {dias_visitados} visitas em 30 dias'))
        pontos_validos = calcular_pontos_validos(cliente_id)
    
    cursor.execute('''
        UPDATE clientes 
        SET pontos_totais = %s,
            nivel = %s,
            ultima_visita = NOW()
        WHERE id = %s
    ''', (pontos_validos, calcular_nivel(pontos_validos), cliente_id))
    
    conn.commit()
    conn.close()
    
    mensagem = 'Pontos adicionados com sucesso'
    if pontos_bonus > 0:
        mensagem += f' + {pontos_bonus} pts de bônus por frequência!'
    
    return jsonify({
        'message': mensagem,
        'pontos_totais': pontos_validos,
        'pontos_bonus': pontos_bonus,
        'nivel': calcular_nivel(pontos_validos)
    })

@app.route('/api/ranking', methods=['GET'])
def ranking():
    try:
        conn = get_db()
        cursor = dict_cursor(conn)  # PostgreSQL com dict
        cursor.execute('''
            SELECT id, nome, pontos_totais, nivel
            FROM clientes
            ORDER BY pontos_totais DESC
            LIMIT 10
        ''')
        ranking = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(ranking)
    except Exception as e:
        print(f"ERRO em /api/ranking: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    try:
        conn = get_db()
        cursor = dict_cursor(conn)  # PostgreSQL com dict
        
        cursor.execute('SELECT COUNT(*) as total FROM clientes')
        total_clientes = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM clientes WHERE nivel = 'verde'")
        clientes_verde = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM clientes WHERE nivel = 'amarelo'")
        clientes_amarelo = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM clientes WHERE nivel = 'vermelho'")
        clientes_vermelho = cursor.fetchone()['total']
        
        cursor.execute('SELECT SUM(pontos) as total FROM pontuacoes')
        result = cursor.fetchone()
        pontos_distribuidos = result['total'] if result['total'] else 0
        
        conn.close()
        
        return jsonify({
            'total_clientes': total_clientes,
            'clientes_verde': clientes_verde,
            'clientes_amarelo': clientes_amarelo,
            'clientes_vermelho': clientes_vermelho,
            'pontos_distribuidos': pontos_distribuidos
        })
    except Exception as e:
        print(f"ERRO em /api/estatisticas: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/configuracoes', methods=['GET'])
def obter_configuracoes():
    try:
        config = get_configuracoes()
        if config:
            config.pop('senha_admin', None)
        return jsonify(config or {})
    except Exception as e:
        print(f"ERRO em /api/configuracoes: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        senha = data.get('senha')
        
        config = get_configuracoes()
        if config and config['senha_admin'] == senha:
            session['admin'] = True
            return jsonify({'success': True, 'message': 'Login realizado com sucesso'})
        
        return jsonify({'success': False, 'message': 'Senha incorreta'}), 401
    except Exception as e:
        print(f"ERRO em /api/admin/login: {e}")
        return jsonify({'error': str(e)}), 500

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
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    if senha_admin:
        cursor.execute('''
            UPDATE configuracoes 
            SET nome_bar = %s, pontos_vermelho_min = ?, 
                pontos_amarelo_min = ?, pontos_verde_min = ?,
                senha_admin = ?
            WHERE id = 1
        ''', (nome_bar, pontos_vermelho_min, pontos_amarelo_min, pontos_verde_min, senha_admin))
    else:
        cursor.execute('''
            UPDATE configuracoes 
            SET nome_bar = %s, pontos_vermelho_min = ?, 
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
        cursor = dict_cursor(conn)  # PostgreSQL com dict
        cursor.execute('UPDATE configuracoes SET logo_path = %s WHERE id = 1', (logo_path,))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'logo_path': logo_path})
    
    return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/cliente')
def area_cliente():
    return render_template('cliente.html')

@app.route('/api/cliente/login', methods=['POST'])
def cliente_login():
    data = request.json
    telefone = data.get('telefone')
    senha = data.get('senha')
    
    if not telefone:
        return jsonify({'error': 'Telefone é obrigatório'}), 400
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    if senha:
        cursor.execute('SELECT * FROM clientes WHERE telefone = %s AND senha = %s', (telefone, senha))
    else:
        cursor.execute('SELECT * FROM clientes WHERE telefone = %s', (telefone,))
    
    cliente = cursor.fetchone()
    conn.close()
    
    if cliente:
        session['cliente_id'] = cliente['id']
        session['cliente_nome'] = cliente['nome']
        return jsonify({
            'success': True,
            'cliente': {
                'id': cliente['id'],
                'nome': cliente['nome'],
                'telefone': cliente['telefone'],
                'email': cliente['email'],
                'pontos_totais': cliente['pontos_totais'],
                'nivel': cliente['nivel']
            }
        })
    
    return jsonify({'error': 'Cliente não encontrado ou senha incorreta'}), 401

@app.route('/api/cliente/logout', methods=['POST'])
def cliente_logout():
    session.pop('cliente_id', None)
    session.pop('cliente_nome', None)
    return jsonify({'success': True})

@app.route('/api/cliente/perfil', methods=['GET'])
def cliente_perfil():
    try:
        if 'cliente_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        
        cliente_id = session['cliente_id']
        
        conn = get_db()
        cursor = dict_cursor(conn)  # PostgreSQL com dict
        cursor.execute('SELECT * FROM clientes WHERE id = %s', (cliente_id,))
        cliente = cursor.fetchone()
        
        if not cliente:
            conn.close()
            return jsonify({'error': 'Cliente não encontrado'}), 404
        
        cursor.execute('''
            SELECT * FROM pontuacoes 
            WHERE cliente_id = %s 
            ORDER BY data DESC
        ''', (cliente_id,))
        historico = [dict(row) for row in cursor.fetchall()]
        
        cursor.execute('''
            SELECT SUM(pontos) as total
            FROM pontuacoes
            WHERE cliente_id = %s
            AND data_validade IS NOT NULL
            AND data_validade <= NOW()
        ''', (cliente_id,))
        resultado_expirados = cursor.fetchone()
        pontos_expirados = resultado_expirados['total'] if resultado_expirados and resultado_expirados['total'] else 0
        
        pontos_bonus, dias_visitados = calcular_pontos_frequencia(cliente_id)
        
        conn.close()
        
        config = get_configuracoes()
        pontos_validos = calcular_pontos_validos(cliente_id)
        
        return jsonify({
            'id': cliente['id'],
            'nome': cliente['nome'],
            'telefone': cliente['telefone'],
            'email': cliente['email'],
            'pontos_totais': pontos_validos,
            'pontos_expirados': pontos_expirados,
            'pontos_bonus_disponiveis': pontos_bonus,
            'dias_visitados_mes': dias_visitados,
            'nivel': calcular_nivel(pontos_validos),
            'data_cadastro': cliente['data_cadastro'],
            'ultima_visita': cliente['ultima_visita'],
            'historico': historico,
            'config': {
                'pontos_amarelo': config['pontos_amarelo_min'] if config else 200,
                'pontos_verde': config['pontos_verde_min'] if config else 500
            }
        })
    except Exception as e:
        print(f"ERRO em /api/cliente/perfil: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/cliente/definir-senha', methods=['POST'])
def cliente_definir_senha():
    data = request.json
    telefone = data.get('telefone')
    senha = data.get('senha')
    
    if not telefone or not senha:
        return jsonify({'error': 'Telefone e senha são obrigatórios'}), 400
    
    if len(senha) < 4:
        return jsonify({'error': 'Senha deve ter no mínimo 4 caracteres'}), 400
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('UPDATE clientes SET senha = %s WHERE telefone = %s', (senha, telefone))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Cliente não encontrado'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Senha definida com sucesso'})

@app.route('/api/cliente/checkin', methods=['POST'])
def fazer_checkin():
    if 'cliente_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    cliente_id = session['cliente_id']
    data = request.json
    localizacao = data.get('localizacao', '')
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    cursor.execute('''
        SELECT COUNT(*) FROM checkins
        WHERE cliente_id = %s
        AND DATE(data_checkin) = DATE('now')
    ''', (cliente_id,))
    
    checkin_hoje = cursor.fetchone()[0]
    
    if checkin_hoje > 0:
        conn.close()
        return jsonify({'error': 'Você já fez check-in hoje!'}), 400
    
    cursor.execute('''
        INSERT INTO checkins (cliente_id, localizacao)
        VALUES (%s, %s)
    ''', (cliente_id, localizacao))
    
    cursor.execute('''
        UPDATE clientes 
        SET ultima_visita = NOW()
        WHERE id = %s
    ''', (cliente_id,))
    
    conn.commit()
    
    pontos_bonus, dias_visitados = calcular_pontos_frequencia(cliente_id)
    
    conn.close()
    
    mensagem = 'Check-in realizado com sucesso!'
    if pontos_bonus > 0:
        mensagem += f' Você tem {pontos_bonus} pontos de bônus disponíveis por frequência!'
    
    return jsonify({
        'success': True,
        'message': mensagem,
        'dias_visitados': dias_visitados,
        'pontos_bonus_disponiveis': pontos_bonus
    })

@app.route('/api/cliente/checkins', methods=['GET'])
def listar_checkins_cliente():
    if 'cliente_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    cliente_id = session['cliente_id']
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('''
        SELECT * FROM checkins
        WHERE cliente_id = %s
        ORDER BY data_checkin DESC
        LIMIT 30
    ''', (cliente_id,))
    
    checkins = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify(checkins)

@app.route('/api/cliente/pode-checkin', methods=['GET'])
def pode_fazer_checkin():
    try:
        if 'cliente_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        
        cliente_id = session['cliente_id']
        
        conn = get_db()
        cursor = dict_cursor(conn)  # PostgreSQL com dict
        cursor.execute('''
            SELECT COUNT(*) as count FROM checkins
            WHERE cliente_id = %s
            AND DATE(data_checkin) = CURRENT_DATE
        ''', (cliente_id,))
        
        result = cursor.fetchone()
        checkin_hoje = result['count'] if result else 0
        conn.close()
        
        return jsonify({
            'pode_checkin': checkin_hoje == 0,
            'ja_fez_checkin': checkin_hoje > 0
        })
    except Exception as e:
        print(f"ERRO em /api/cliente/pode-checkin: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    apenas_ativos = request.args.get('ativos', 'false').lower() == 'true'
    
    if apenas_ativos:
        cursor.execute('SELECT * FROM produtos WHERE ativo = 1 ORDER BY nome')
    else:
        cursor.execute('SELECT * FROM produtos ORDER BY nome')
    
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(produtos)

@app.route('/api/produtos', methods=['POST'])
def cadastrar_produto():
    if not session.get('admin'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.json
    nome = data.get('nome')
    descricao = data.get('descricao', '')
    pontos = data.get('pontos', 0)
    
    if not nome or pontos <= 0:
        return jsonify({'error': 'Nome e pontos são obrigatórios'}), 400
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('''
        INSERT INTO produtos (nome, descricao, pontos)
        VALUES (%s, %s, %s)
    ''', (nome, descricao, pontos))
    conn.commit()
    produto_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': produto_id, 'message': 'Produto cadastrado com sucesso'}), 201

@app.route('/api/produtos/<int:produto_id>', methods=['PUT'])
def atualizar_produto(produto_id):
    if not session.get('admin'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.json
    nome = data.get('nome')
    descricao = data.get('descricao', '')
    pontos = data.get('pontos', 0)
    ativo = data.get('ativo', 1)
    
    if not nome or pontos <= 0:
        return jsonify({'error': 'Nome e pontos são obrigatórios'}), 400
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('''
        UPDATE produtos 
        SET nome = %s, descricao = ?, pontos = ?, ativo = ?
        WHERE id = %s
    ''', (nome, descricao, pontos, ativo, produto_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Produto atualizado com sucesso'})

@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def deletar_produto(produto_id):
    if not session.get('admin'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('DELETE FROM produtos WHERE id = %s', (produto_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Produto deletado com sucesso'})

@app.route('/api/solicitacoes', methods=['POST'])
def solicitar_pontos():
    if 'cliente_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    data = request.json
    produto_id = data.get('produto_id')
    quantidade = data.get('quantidade', 1)
    observacao = data.get('observacao', '')
    
    if not produto_id or quantidade <= 0:
        return jsonify({'error': 'Dados inválidos'}), 400
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    cursor.execute('SELECT * FROM produtos WHERE id = %s AND ativo = 1', (produto_id,))
    produto = cursor.fetchone()
    
    if not produto:
        conn.close()
        return jsonify({'error': 'Produto não encontrado ou inativo'}), 404
    
    pontos_total = produto['pontos'] * quantidade
    cliente_id = session['cliente_id']
    
    cursor.execute('''
        INSERT INTO solicitacoes_pontos (cliente_id, produto_id, quantidade, pontos_total, observacao)
        VALUES (%s, %s, %s, %s, %s)
    ''', (cliente_id, produto_id, quantidade, pontos_total, observacao))
    conn.commit()
    solicitacao_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'id': solicitacao_id,
        'message': 'Solicitação enviada com sucesso! Aguarde a validação do administrador.',
        'pontos_total': pontos_total
    }), 201

@app.route('/api/solicitacoes', methods=['GET'])
def listar_solicitacoes():
    if not session.get('admin'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    status = request.args.get('status', 'pendente')
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    if status == 'todas':
        cursor.execute('''
            SELECT s.*, c.nome as cliente_nome, c.telefone as cliente_telefone,
                   p.nome as produto_nome, p.descricao as produto_descricao
            FROM solicitacoes_pontos s
            JOIN clientes c ON s.cliente_id = c.id
            JOIN produtos p ON s.produto_id = p.id
            ORDER BY s.data_solicitacao DESC
        ''')
    else:
        cursor.execute('''
            SELECT s.*, c.nome as cliente_nome, c.telefone as cliente_telefone,
                   p.nome as produto_nome, p.descricao as produto_descricao
            FROM solicitacoes_pontos s
            JOIN clientes c ON s.cliente_id = c.id
            JOIN produtos p ON s.produto_id = p.id
            WHERE s.status = %s
            ORDER BY s.data_solicitacao DESC
        ''', (status,))
    
    solicitacoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(solicitacoes)

@app.route('/api/solicitacoes/cliente', methods=['GET'])
def listar_solicitacoes_cliente():
    if 'cliente_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    cliente_id = session['cliente_id']
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    cursor.execute('''
        SELECT s.*, p.nome as produto_nome, p.descricao as produto_descricao
        FROM solicitacoes_pontos s
        JOIN produtos p ON s.produto_id = p.id
        WHERE s.cliente_id = %s
        ORDER BY s.data_solicitacao DESC
    ''', (cliente_id,))
    
    solicitacoes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(solicitacoes)

@app.route('/api/solicitacoes/<int:solicitacao_id>/validar', methods=['POST'])
def validar_solicitacao(solicitacao_id):
    if not session.get('admin'):
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.json
    aprovar = data.get('aprovar', False)
    
    conn = get_db()
    cursor = dict_cursor(conn)  # PostgreSQL com dict
    
    cursor.execute('SELECT * FROM solicitacoes_pontos WHERE id = %s', (solicitacao_id,))
    solicitacao = cursor.fetchone()
    
    if not solicitacao:
        conn.close()
        return jsonify({'error': 'Solicitação não encontrada'}), 404
    
    if solicitacao['status'] != 'pendente':
        conn.close()
        return jsonify({'error': 'Solicitação já foi processada'}), 400
    
    novo_status = 'aprovada' if aprovar else 'rejeitada'
    
    cursor.execute('''
        UPDATE solicitacoes_pontos 
        SET status = %s, data_validacao = NOW(), validado_por = 'admin'
        WHERE id = %s
    ''', (novo_status, solicitacao_id))
    
    if aprovar:
        cursor.execute('''
            INSERT INTO pontuacoes (cliente_id, pontos, tipo, descricao, data_validade)
            VALUES (%s, %s, 'produto', %s, NOW() + INTERVAL '90 days')
        ''', (solicitacao['cliente_id'], solicitacao['pontos_total'], 
              f"Produto consumido (Solicitação #{solicitacao_id})"))
        
        pontos_validos = calcular_pontos_validos(solicitacao['cliente_id'])
        pontos_bonus, dias_visitados = calcular_pontos_frequencia(solicitacao['cliente_id'])
        
        if pontos_bonus > 0:
            cursor.execute('''
                INSERT INTO pontuacoes (cliente_id, pontos, tipo, descricao, data_validade)
                VALUES (%s, %s, 'frequencia', %s, NOW() + INTERVAL '90 days')
            ''', (solicitacao['cliente_id'], pontos_bonus, f'Bônus de frequência: {dias_visitados} visitas em 30 dias'))
            pontos_validos = calcular_pontos_validos(solicitacao['cliente_id'])
        
        cursor.execute('''
            UPDATE clientes 
            SET pontos_totais = %s,
                nivel = ?,
                ultima_visita = NOW()
            WHERE id = %s
        ''', (pontos_validos, calcular_nivel(pontos_validos), solicitacao['cliente_id']))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': f'Solicitação {novo_status} com sucesso!',
        'status': novo_status
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
