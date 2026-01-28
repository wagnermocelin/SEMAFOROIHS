# 📤 Como Migrar Dados do SQLite para Supabase

## 🎯 Objetivo

Este guia mostra como exportar todos os dados do seu banco SQLite local (`semaforo.db`) para o Supabase PostgreSQL.

---

## ⚠️ Antes de Começar

**Certifique-se de que:**
1. ✅ Você já criou o projeto no Supabase
2. ✅ O banco Supabase está ativo e acessível
3. ✅ Você tem a connection string completa
4. ✅ Você instalou as dependências: `pip install psycopg2-binary python-dotenv`

---

## 🚀 Passo a Passo

### 1. Verificar se tem dados no SQLite local

Antes de migrar, confirme que você tem dados para migrar:

```bash
# No diretório do projeto
ls -la semaforo.db
```

Se o arquivo existe e tem tamanho > 0, você tem dados.

### 2. Executar o Script de Migração

```bash
python migrate_data_to_supabase.py
```

### 3. Acompanhar o Processo

O script mostrará o progresso:

```
============================================================
🔄 MIGRAÇÃO DE DADOS: SQLite → Supabase PostgreSQL
============================================================
✅ Conectado ao SQLite local
✅ Conectado ao Supabase PostgreSQL

📋 Criando estrutura de tabelas no Supabase...
✅ Estrutura de tabelas criada com sucesso

🔧 Migrando configurações...
✅ Configurações migradas: Semáforo Bar

👥 Migrando clientes...
✅ 15 clientes migrados

🎯 Migrando pontuações...
✅ 45 pontuações migradas

📦 Migrando produtos...
✅ 8 produtos migrados

📍 Migrando checkins...
✅ 23 checkins migrados

📊 Verificando dados migrados...
  - clientes: 15 registros
  - pontuacoes: 45 registros
  - configuracoes: 1 registros
  - produtos: 8 registros
  - checkins: 23 registros

============================================================
✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!
============================================================
```

---

## 🔍 Verificar Dados no Supabase

Após a migração:

1. Acesse: https://supabase.com/dashboard
2. Selecione seu projeto: `semaforo-bar`
3. Vá em **Table Editor** no menu lateral
4. Clique em cada tabela para ver os dados:
   - `clientes` - Seus clientes
   - `pontuacoes` - Histórico de pontos
   - `configuracoes` - Configurações do bar
   - `produtos` - Produtos cadastrados
   - `checkins` - Registro de visitas

---

## 🛠️ Troubleshooting

### Erro: "connection to server failed"

**Causa:** Connection string incorreta ou Supabase offline

**Solução:**
1. Verifique se a URL está correta no script
2. Teste a conexão no SQL Editor do Supabase
3. Confirme que o projeto Supabase está ativo

### Erro: "relation already exists"

**Causa:** Tabelas já existem no Supabase

**Solução:**
- O script usa `CREATE TABLE IF NOT EXISTS`, então isso não deve acontecer
- Se acontecer, os dados serão adicionados às tabelas existentes

### Erro: "foreign key constraint"

**Causa:** Ordem de migração incorreta

**Solução:**
- O script já migra na ordem correta (configurações → clientes → pontuações)
- Se persistir, limpe o banco e execute novamente

### Dados duplicados

**Causa:** Script executado múltiplas vezes

**Solução:**
Para limpar e recomeçar, execute no SQL Editor do Supabase:

```sql
-- CUIDADO: Isso apaga TODOS os dados!
DROP TABLE IF EXISTS checkins CASCADE;
DROP TABLE IF EXISTS solicitacoes_pontos CASCADE;
DROP TABLE IF EXISTS pontuacoes CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;
DROP TABLE IF EXISTS configuracoes CASCADE;
```

Depois execute o script novamente.

---

## 📊 O Que é Migrado

| Tabela | Dados Migrados |
|--------|----------------|
| `configuracoes` | Nome do bar, logo, níveis de pontos, senha admin |
| `clientes` | Nome, telefone, email, pontos, nível |
| `pontuacoes` | Histórico completo de pontos de cada cliente |
| `produtos` | Produtos cadastrados (se existir) |
| `checkins` | Registro de visitas (se existir) |
| `solicitacoes_pontos` | Não migrado (dados temporários) |

---

## ✅ Após a Migração

1. **Verifique os dados** no Supabase Table Editor
2. **Configure as variáveis de ambiente** na Vercel
3. **Faça deploy** na Vercel
4. **Teste a aplicação** online
5. **Opcional:** Faça backup do `semaforo.db` local e arquive

---

## 🔐 Segurança

⚠️ **IMPORTANTE:**
- O script contém sua senha do Supabase
- **NÃO faça commit** deste script no Git
- Após a migração, você pode deletar o script ou remover a senha

---

## 💡 Dicas

1. **Backup antes de migrar:**
   ```bash
   cp semaforo.db semaforo_backup.db
   ```

2. **Migração incremental:**
   - O script verifica se já existem configurações
   - Clientes são sempre adicionados (pode gerar duplicatas se executar 2x)

3. **Teste primeiro:**
   - Crie um projeto Supabase de teste
   - Migre os dados
   - Verifique se está tudo OK
   - Depois migre para o projeto de produção

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do script
2. Teste a conexão manualmente no SQL Editor do Supabase
3. Confirme que as credenciais estão corretas
4. Verifique se o arquivo `semaforo.db` existe e tem dados

---

**Boa migração! 🚀**
