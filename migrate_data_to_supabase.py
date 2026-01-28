#!/usr/bin/env python3
"""
Script para migrar dados do SQLite local para Supabase PostgreSQL
"""

import sqlite3
import psycopg2
import psycopg2.extras
from datetime import datetime

# Configuração - EDITE AQUI COM SUAS CREDENCIAIS
SUPABASE_HOST = "db.mofyddgzvhwxaorhpzuq.supabase.co"
SUPABASE_DATABASE = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = "$$J25021989j@@"
SUPABASE_PORT = "5432"
SQLITE_DB = "semaforo.db"

def conectar_sqlite():
    """Conecta ao banco SQLite local"""
    try:
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        print("✅ Conectado ao SQLite local")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar SQLite: {e}")
        return None

def conectar_supabase():
    """Conecta ao Supabase PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            database=SUPABASE_DATABASE,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
            port=SUPABASE_PORT,
            sslmode='require'
        )
        print("✅ Conectado ao Supabase PostgreSQL")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar Supabase: {e}")
        print("Verifique se as credenciais estão corretas e se o banco está ativo")
        return None

def criar_tabelas_supabase(pg_conn):
    """Cria as tabelas no Supabase se não existirem"""
    cursor = pg_conn.cursor()
    
    print("\n📋 Criando estrutura de tabelas no Supabase...")
    
    # Tabela clientes
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
    
    # Tabela pontuacoes
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
    
    # Tabela configuracoes
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
    
    # Tabela produtos
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
    
    # Tabela solicitacoes_pontos
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
    
    # Tabela checkins
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checkins (
            id SERIAL PRIMARY KEY,
            cliente_id INTEGER NOT NULL,
            data_checkin TIMESTAMP DEFAULT NOW(),
            localizacao TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
        )
    ''')
    
    pg_conn.commit()
    print("✅ Estrutura de tabelas criada com sucesso")

def migrar_configuracoes(sqlite_conn, pg_conn):
    """Migra configurações"""
    print("\n🔧 Migrando configurações...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Buscar configurações do SQLite
    sqlite_cursor.execute('SELECT * FROM configuracoes LIMIT 1')
    config = sqlite_cursor.fetchone()
    
    if config:
        # Verificar se já existe configuração no Supabase
        pg_cursor.execute('SELECT COUNT(*) FROM configuracoes')
        count = pg_cursor.fetchone()[0]
        
        if count == 0:
            pg_cursor.execute('''
                INSERT INTO configuracoes 
                (nome_bar, logo_path, pontos_vermelho_min, pontos_amarelo_min, 
                 pontos_verde_min, senha_admin)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (config['nome_bar'], config['logo_path'], config['pontos_vermelho_min'],
                  config['pontos_amarelo_min'], config['pontos_verde_min'], config['senha_admin']))
            pg_conn.commit()
            print(f"✅ Configurações migradas: {config['nome_bar']}")
        else:
            print("⚠️  Configurações já existem no Supabase, pulando...")
    else:
        print("⚠️  Nenhuma configuração encontrada no SQLite")

def migrar_clientes(sqlite_conn, pg_conn):
    """Migra clientes"""
    print("\n👥 Migrando clientes...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Buscar todos os clientes do SQLite
    sqlite_cursor.execute('SELECT * FROM clientes ORDER BY id')
    clientes = sqlite_cursor.fetchall()
    
    if not clientes:
        print("⚠️  Nenhum cliente encontrado no SQLite")
        return {}
    
    # Mapear IDs antigos para novos
    id_map = {}
    
    for cliente in clientes:
        # Inserir no Supabase
        pg_cursor.execute('''
            INSERT INTO clientes 
            (nome, telefone, email, senha, data_cadastro, pontos_totais, nivel, ultima_visita)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (cliente['nome'], cliente['telefone'], cliente['email'], cliente['senha'],
              cliente['data_cadastro'], cliente['pontos_totais'], cliente['nivel'], 
              cliente['ultima_visita']))
        
        novo_id = pg_cursor.fetchone()[0]
        id_map[cliente['id']] = novo_id
    
    pg_conn.commit()
    print(f"✅ {len(clientes)} clientes migrados")
    return id_map

def migrar_pontuacoes(sqlite_conn, pg_conn, cliente_id_map):
    """Migra pontuações"""
    print("\n🎯 Migrando pontuações...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    # Buscar todas as pontuações do SQLite
    sqlite_cursor.execute('SELECT * FROM pontuacoes ORDER BY id')
    pontuacoes = sqlite_cursor.fetchall()
    
    if not pontuacoes:
        print("⚠️  Nenhuma pontuação encontrada no SQLite")
        return
    
    migradas = 0
    for pont in pontuacoes:
        # Mapear ID do cliente antigo para novo
        novo_cliente_id = cliente_id_map.get(pont['cliente_id'])
        
        if novo_cliente_id:
            pg_cursor.execute('''
                INSERT INTO pontuacoes 
                (cliente_id, pontos, tipo, descricao, data, data_validade)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (novo_cliente_id, pont['pontos'], pont['tipo'], pont['descricao'],
                  pont['data'], pont['data_validade']))
            migradas += 1
    
    pg_conn.commit()
    print(f"✅ {migradas} pontuações migradas")

def migrar_produtos(sqlite_conn, pg_conn):
    """Migra produtos"""
    print("\n📦 Migrando produtos...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    try:
        sqlite_cursor.execute('SELECT * FROM produtos ORDER BY id')
        produtos = sqlite_cursor.fetchall()
        
        if not produtos:
            print("⚠️  Nenhum produto encontrado no SQLite")
            return {}
        
        id_map = {}
        for prod in produtos:
            pg_cursor.execute('''
                INSERT INTO produtos 
                (nome, descricao, pontos, ativo, data_cadastro)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (prod['nome'], prod['descricao'], prod['pontos'], 
                  prod['ativo'], prod['data_cadastro']))
            
            novo_id = pg_cursor.fetchone()[0]
            id_map[prod['id']] = novo_id
        
        pg_conn.commit()
        print(f"✅ {len(produtos)} produtos migrados")
        return id_map
    except Exception as e:
        print(f"⚠️  Tabela produtos não existe ou está vazia: {e}")
        return {}

def migrar_checkins(sqlite_conn, pg_conn, cliente_id_map):
    """Migra checkins"""
    print("\n📍 Migrando checkins...")
    
    sqlite_cursor = sqlite_conn.cursor()
    pg_cursor = pg_conn.cursor()
    
    try:
        sqlite_cursor.execute('SELECT * FROM checkins ORDER BY id')
        checkins = sqlite_cursor.fetchall()
        
        if not checkins:
            print("⚠️  Nenhum checkin encontrado no SQLite")
            return
        
        migrados = 0
        for checkin in checkins:
            novo_cliente_id = cliente_id_map.get(checkin['cliente_id'])
            
            if novo_cliente_id:
                pg_cursor.execute('''
                    INSERT INTO checkins 
                    (cliente_id, data_checkin, localizacao)
                    VALUES (%s, %s, %s)
                ''', (novo_cliente_id, checkin['data_checkin'], checkin['localizacao']))
                migrados += 1
        
        pg_conn.commit()
        print(f"✅ {migrados} checkins migrados")
    except Exception as e:
        print(f"⚠️  Tabela checkins não existe ou está vazia: {e}")

def verificar_migracao(pg_conn):
    """Verifica os dados migrados"""
    print("\n📊 Verificando dados migrados...")
    
    cursor = pg_conn.cursor()
    
    # Contar registros em cada tabela
    tabelas = ['clientes', 'pontuacoes', 'configuracoes', 'produtos', 'checkins']
    
    for tabela in tabelas:
        cursor.execute(f'SELECT COUNT(*) FROM {tabela}')
        count = cursor.fetchone()[0]
        print(f"  - {tabela}: {count} registros")

def main():
    """Função principal"""
    print("=" * 60)
    print("🔄 MIGRAÇÃO DE DADOS: SQLite → Supabase PostgreSQL")
    print("=" * 60)
    
    # Conectar aos bancos
    sqlite_conn = conectar_sqlite()
    if not sqlite_conn:
        return
    
    pg_conn = conectar_supabase()
    if not pg_conn:
        sqlite_conn.close()
        return
    
    try:
        # Criar estrutura de tabelas
        criar_tabelas_supabase(pg_conn)
        
        # Migrar dados na ordem correta (respeitando foreign keys)
        migrar_configuracoes(sqlite_conn, pg_conn)
        cliente_id_map = migrar_clientes(sqlite_conn, pg_conn)
        migrar_pontuacoes(sqlite_conn, pg_conn, cliente_id_map)
        produto_id_map = migrar_produtos(sqlite_conn, pg_conn)
        migrar_checkins(sqlite_conn, pg_conn, cliente_id_map)
        
        # Verificar migração
        verificar_migracao(pg_conn)
        
        print("\n" + "=" * 60)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("\n📋 Próximos passos:")
        print("1. Acesse o Supabase Dashboard → Table Editor")
        print("2. Verifique se os dados estão corretos")
        print("3. Faça deploy na Vercel com as variáveis de ambiente configuradas")
        
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        pg_conn.rollback()
    finally:
        sqlite_conn.close()
        pg_conn.close()
        print("\n🔌 Conexões fechadas")

if __name__ == "__main__":
    main()
