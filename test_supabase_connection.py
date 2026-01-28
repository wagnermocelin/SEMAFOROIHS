#!/usr/bin/env python3
"""
Script para testar conexão com Supabase PostgreSQL
"""

import psycopg2
import socket

# Configuração
SUPABASE_HOST = "db.mofyddgzvhwxaorhpzuq.supabase.co"
SUPABASE_DATABASE = "postgres"
SUPABASE_USER = "postgres"
SUPABASE_PASSWORD = "$$J25021989j@@"
SUPABASE_PORT = 5432

print("=" * 60)
print("🔍 TESTE DE CONEXÃO COM SUPABASE")
print("=" * 60)

# Teste 1: Resolver DNS
print("\n1️⃣ Testando resolução DNS...")
try:
    ip = socket.gethostbyname(SUPABASE_HOST)
    print(f"✅ DNS resolvido: {SUPABASE_HOST} → {ip}")
except Exception as e:
    print(f"❌ Erro ao resolver DNS: {e}")
    print("\n💡 Possíveis soluções:")
    print("  - Verifique sua conexão com a internet")
    print("  - Tente usar DNS público (8.8.8.8 ou 1.1.1.1)")
    print("  - Verifique se o firewall está bloqueando")
    exit(1)

# Teste 2: Testar porta
print(f"\n2️⃣ Testando conexão na porta {SUPABASE_PORT}...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((SUPABASE_HOST, SUPABASE_PORT))
    sock.close()
    
    if result == 0:
        print(f"✅ Porta {SUPABASE_PORT} está acessível")
    else:
        print(f"❌ Não foi possível conectar na porta {SUPABASE_PORT}")
        print("\n💡 Possíveis soluções:")
        print("  - Verifique se o firewall está bloqueando a porta 5432")
        print("  - Tente desativar temporariamente o antivírus")
        exit(1)
except Exception as e:
    print(f"❌ Erro ao testar porta: {e}")
    exit(1)

# Teste 3: Conectar ao PostgreSQL
print("\n3️⃣ Testando conexão PostgreSQL...")
try:
    conn = psycopg2.connect(
        host=SUPABASE_HOST,
        database=SUPABASE_DATABASE,
        user=SUPABASE_USER,
        password=SUPABASE_PASSWORD,
        port=SUPABASE_PORT,
        sslmode='require',
        connect_timeout=10
    )
    print("✅ Conectado ao Supabase PostgreSQL com sucesso!")
    
    # Teste 4: Executar query simples
    print("\n4️⃣ Testando query simples...")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ PostgreSQL Version: {version[:50]}...")
    
    # Teste 5: Listar tabelas
    print("\n5️⃣ Listando tabelas existentes...")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tabelas = cursor.fetchall()
    
    if tabelas:
        print(f"✅ Encontradas {len(tabelas)} tabelas:")
        for tabela in tabelas:
            print(f"   - {tabela[0]}")
    else:
        print("⚠️  Nenhuma tabela encontrada (banco vazio - OK para primeira migração)")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    print("\n🚀 Você pode executar o script de migração agora:")
    print("   python migrate_data_to_supabase.py")
    
except psycopg2.OperationalError as e:
    print(f"❌ Erro de conexão PostgreSQL: {e}")
    print("\n💡 Possíveis soluções:")
    print("  - Verifique se a senha está correta")
    print("  - Confirme que o projeto Supabase está ativo")
    print("  - Tente acessar o Supabase Dashboard para verificar status")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    print("\n💡 Entre em contato com o suporte se o problema persistir")
