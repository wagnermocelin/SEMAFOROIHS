#!/usr/bin/env python3
"""
Script para migrar queries SQLite para PostgreSQL no app.py
"""

import re

def migrate_sql_syntax(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Substituir placeholders ? por %s (PostgreSQL)
    # Precisa ser cuidadoso para não substituir ? em strings
    content = re.sub(r"VALUES\s*\(([?%s,\s]+)\)", lambda m: "VALUES (" + m.group(1).replace('?', '%s') + ")", content)
    content = re.sub(r"WHERE\s+([^'\"]*?)\?", lambda m: "WHERE " + m.group(1) + "%s", content)
    content = re.sub(r"SET\s+([^'\"]*?)\?", lambda m: "SET " + m.group(1) + "%s", content)
    
    # Substituir datetime('now') por NOW()
    content = content.replace("datetime('now')", "NOW()")
    content = content.replace("datetime('now', '+90 days')", "NOW() + INTERVAL '90 days'")
    content = content.replace("datetime('now', '-30 days')", "NOW() - INTERVAL '30 days'")
    
    # Substituir DATE() por date_trunc ou CAST
    content = re.sub(r"DATE\(([^)]+)\)", r"DATE(\1)", content)
    
    # Substituir CURRENT_TIMESTAMP por NOW()
    content = content.replace("CURRENT_TIMESTAMP", "NOW()")
    
    # Substituir conn.row_factory por dict_cursor
    content = content.replace("cursor = conn.cursor()", "cursor = dict_cursor(conn)")
    
    print("Migração de sintaxe SQL concluída!")
    print("\nPróximos passos manuais necessários:")
    print("1. Revisar todas as queries que usam placeholders ?")
    print("2. Substituir manualmente ? por %s onde necessário")
    print("3. Verificar queries com datetime() e ajustar intervalos")
    print("4. Testar todas as rotas da API")
    
    return content

if __name__ == "__main__":
    print("Este é um script auxiliar de migração.")
    print("Execute manualmente as substituições no app.py")
