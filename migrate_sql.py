#!/usr/bin/env python3
"""Script para migrar app.py de SQLite para PostgreSQL"""

import re

# Ler o arquivo
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Substituir placeholders ? por %s (PostgreSQL)
# Substituir em queries SQL (dentro de aspas triplas e simples)
content = re.sub(r"VALUES\s*\(([^)]*)\)", lambda m: "VALUES (" + m.group(1).replace('?', '%s') + ")", content)
content = re.sub(r"WHERE\s+([^'\";\n]*?)\s*\?", lambda m: "WHERE " + m.group(1) + " %s", content)
content = re.sub(r"SET\s+([^'\";\n]*?)\s*=\s*\?", lambda m: "SET " + m.group(1) + " = %s", content)
content = re.sub(r"AND\s+([^'\";\n]*?)\s*=\s*\?", lambda m: "AND " + m.group(1) + " = %s", content)
content = re.sub(r"OR\s+([^'\";\n]*?)\s*>\s*\?", lambda m: "OR " + m.group(1) + " > %s", content)

# 2. Substituir datetime('now') por NOW()
content = content.replace("datetime('now', '+90 days')", "NOW() + INTERVAL '90 days'")
content = content.replace("datetime('now', '-30 days')", "NOW() - INTERVAL '30 days'")
content = content.replace("datetime('now')", "NOW()")

# 3. Substituir CURRENT_TIMESTAMP por NOW() (já foi feito parcialmente)
content = content.replace("CURRENT_TIMESTAMP", "NOW()")

# 4. Ajustar cursor.fetchone() para lidar com dicionários
# Substituir cursor = conn.cursor() por cursor = dict_cursor(conn) onde necessário
lines = content.split('\n')
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    # Se a linha tem cursor = conn.cursor() e não é na função dict_cursor
    if 'cursor = conn.cursor()' in line and 'def dict_cursor' not in '\n'.join(lines[max(0,i-5):i]):
        # Adicionar comentário
        indent = len(line) - len(line.lstrip())
        new_lines[-1] = ' ' * indent + 'cursor = dict_cursor(conn)  # PostgreSQL com dict'

content = '\n'.join(new_lines)

# Salvar o arquivo migrado
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Migração SQL concluída!")
print("Substituições realizadas:")
print("  - Placeholders ? → %s")
print("  - datetime('now') → NOW()")
print("  - datetime com intervalos → NOW() + INTERVAL")
print("  - cursor = conn.cursor() → cursor = dict_cursor(conn)")
