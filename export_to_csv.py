#!/usr/bin/env python3
"""
Script para exportar dados do SQLite para CSV
Depois você pode importar via Supabase Dashboard
"""

import sqlite3
import csv
import os
from datetime import datetime

SQLITE_DB = "semaforo.db"
OUTPUT_DIR = "export_csv"

def criar_diretorio():
    """Cria diretório para os arquivos CSV"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    print(f"📁 Diretório criado: {OUTPUT_DIR}/")

def exportar_tabela(conn, tabela, colunas):
    """Exporta uma tabela para CSV"""
    try:
        cursor = conn.cursor()
        cursor.execute(f'SELECT {", ".join(colunas)} FROM {tabela}')
        dados = cursor.fetchall()
        
        if not dados:
            print(f"⚠️  Tabela '{tabela}' está vazia")
            return 0
        
        arquivo = f"{OUTPUT_DIR}/{tabela}.csv"
        with open(arquivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(colunas)  # Cabeçalho
            writer.writerows(dados)
        
        print(f"✅ {tabela}.csv - {len(dados)} registros exportados")
        return len(dados)
    except Exception as e:
        print(f"❌ Erro ao exportar '{tabela}': {e}")
        return 0

def main():
    print("=" * 60)
    print("📤 EXPORTAÇÃO DE DADOS PARA CSV")
    print("=" * 60)
    
    # Conectar ao SQLite
    try:
        conn = sqlite3.connect(SQLITE_DB)
        print(f"✅ Conectado ao {SQLITE_DB}\n")
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return
    
    # Criar diretório
    criar_diretorio()
    
    print("\n📊 Exportando tabelas...\n")
    
    total = 0
    
    # Exportar configurações
    total += exportar_tabela(conn, 'configuracoes', [
        'id', 'nome_bar', 'logo_path', 'pontos_vermelho_min',
        'pontos_amarelo_min', 'pontos_verde_min', 'senha_admin'
    ])
    
    # Exportar clientes
    total += exportar_tabela(conn, 'clientes', [
        'id', 'nome', 'telefone', 'email', 'senha', 'data_cadastro',
        'pontos_totais', 'nivel', 'ultima_visita'
    ])
    
    # Exportar pontuações
    total += exportar_tabela(conn, 'pontuacoes', [
        'id', 'cliente_id', 'pontos', 'tipo', 'descricao',
        'data', 'data_validade'
    ])
    
    # Exportar produtos (se existir)
    try:
        total += exportar_tabela(conn, 'produtos', [
            'id', 'nome', 'descricao', 'pontos', 'ativo', 'data_cadastro'
        ])
    except:
        pass
    
    # Exportar checkins (se existir)
    try:
        total += exportar_tabela(conn, 'checkins', [
            'id', 'cliente_id', 'data_checkin', 'localizacao'
        ])
    except:
        pass
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ EXPORTAÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"\n📊 Total de registros exportados: {total}")
    print(f"📁 Arquivos salvos em: {OUTPUT_DIR}/")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Acesse: https://supabase.com/dashboard")
    print("2. Selecione seu projeto")
    print("3. Vá em 'Table Editor'")
    print("4. Clique em 'Import data' ou 'Insert' → 'Import CSV'")
    print("5. Faça upload dos arquivos CSV na ordem:")
    print("   - configuracoes.csv (primeiro)")
    print("   - clientes.csv")
    print("   - pontuacoes.csv")
    print("   - produtos.csv (se existir)")
    print("   - checkins.csv (se existir)")

if __name__ == "__main__":
    main()
