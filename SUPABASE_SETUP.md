# 🚀 Setup Supabase PostgreSQL - Guia Completo

## 📋 Visão Geral

Este guia mostra como configurar o Supabase PostgreSQL para o projeto Semáforo Bar e fazer deploy na Vercel.

**Vantagens do Supabase:**
- ✅ **Gratuito**: 500 MB de banco de dados no tier gratuito
- ✅ **PostgreSQL completo**: Todas as features do PostgreSQL
- ✅ **Backup automático**: Point-in-time recovery
- ✅ **Dashboard visual**: Interface para gerenciar dados
- ✅ **API REST automática**: Gerada automaticamente (opcional)
- ✅ **Sem cartão de crédito**: Tier gratuito sem necessidade de cartão

---

## 🎯 Passo 1: Criar Conta no Supabase

1. Acesse: https://supabase.com
2. Clique em **"Start your project"**
3. Faça login com GitHub, Google ou email
4. Confirme seu email

---

## 🗄️ Passo 2: Criar Projeto

1. No dashboard, clique em **"New Project"**
2. Preencha os dados:
   - **Name**: `semaforo-bar` (ou nome de sua preferência)
   - **Database Password**: Crie uma senha forte (ANOTE ESSA SENHA!)
   - **Region**: Escolha a mais próxima (ex: South America - São Paulo)
   - **Pricing Plan**: Free (gratuito)
3. Clique em **"Create new project"**
4. Aguarde 1-2 minutos enquanto o projeto é provisionado

---

## 🔑 Passo 3: Obter Connection String

1. No dashboard do projeto, clique no ícone de **engrenagem** (Settings)
2. No menu lateral, clique em **"Database"**
3. Role até a seção **"Connection string"**
4. Selecione a aba **"URI"**
5. Copie a URL que aparece (formato):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres
   ```
6. **IMPORTANTE**: Substitua `[YOUR-PASSWORD]` pela senha que você criou no Passo 2

**Exemplo:**
```
postgresql://postgres:MinhaSenh@123@db.abcdefghijk.supabase.co:5432/postgres
```

---

## 🔧 Passo 4: Configurar Variáveis de Ambiente na Vercel

1. Acesse: https://vercel.com/dashboard
2. Selecione seu projeto: **SEMAFOROIHS**
3. Vá em **Settings** → **Environment Variables**
4. Adicione as seguintes variáveis:

### Variável 1: POSTGRES_URL
- **Name**: `POSTGRES_URL`
- **Value**: Cole a connection string do Supabase (com a senha substituída)
- **Environment**: Production, Preview, Development (marque todos)
- Clique em **Save**

### Variável 2: DATABASE_URL
- **Name**: `DATABASE_URL`
- **Value**: Cole a mesma connection string (fallback)
- **Environment**: Production, Preview, Development (marque todos)
- Clique em **Save**

### Variável 3: SECRET_KEY
- **Name**: `SECRET_KEY`
- **Value**: Gere uma chave executando no terminal:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- **Environment**: Production, Preview, Development (marque todos)
- Clique em **Save**

### Variável 4: FLASK_ENV
- **Name**: `FLASK_ENV`
- **Value**: `production`
- **Environment**: Production (apenas Production)
- Clique em **Save**

---

## 🚀 Passo 5: Deploy na Vercel

### Opção A: Redeploy Automático

1. As variáveis de ambiente foram configuradas
2. Vá em **Deployments**
3. Clique nos **três pontos** do último deployment
4. Clique em **"Redeploy"**
5. Aguarde o deploy concluir

### Opção B: Novo Deploy via Git

1. Faça um commit qualquer no repositório:
   ```bash
   git commit --allow-empty -m "Trigger deploy com Supabase"
   git push origin main
   ```
2. A Vercel fará deploy automaticamente

---

## 🗃️ Passo 6: Inicializar Banco de Dados

Após o primeiro deploy bem-sucedido:

1. Acesse sua aplicação na URL da Vercel
2. As tabelas serão criadas automaticamente pela função `init_db()`
3. Verifique no Supabase:
   - Vá em **Table Editor** no dashboard
   - Você verá as tabelas: `clientes`, `pontuacoes`, `configuracoes`, `produtos`, `solicitacoes_pontos`, `checkins`

---

## 🔍 Passo 7: Verificar Funcionamento

### No Supabase Dashboard:

1. Vá em **Table Editor**
2. Clique na tabela `configuracoes`
3. Você deve ver 1 registro com:
   - `nome_bar`: "Semáforo Bar"
   - `senha_admin`: "admin123"

### Na Aplicação:

1. Acesse a URL da Vercel
2. Clique em **"Admin"**
3. Faça login com senha: `admin123`
4. Teste cadastrar um cliente
5. Volte ao Supabase → Table Editor → `clientes`
6. O cliente deve aparecer lá!

---

## 📊 Monitoramento e Logs

### Ver Logs da Aplicação (Vercel):
1. Dashboard Vercel → Seu Projeto
2. Clique em **"Logs"**
3. Veja erros de conexão ou SQL

### Ver Logs do Banco (Supabase):
1. Dashboard Supabase → Seu Projeto
2. Clique em **"Logs"** no menu lateral
3. Selecione **"Postgres Logs"**

### Executar Queries SQL (Supabase):
1. Dashboard Supabase → **"SQL Editor"**
2. Execute queries manualmente:
   ```sql
   SELECT * FROM clientes;
   SELECT * FROM pontuacoes;
   ```

---

## 🛠️ Troubleshooting

### Erro: "connection to server failed"

**Causa**: Connection string incorreta ou senha errada

**Solução**:
1. Verifique se substituiu `[YOUR-PASSWORD]` pela senha real
2. Confirme que não há espaços extras na connection string
3. Teste a conexão no SQL Editor do Supabase

### Erro: "relation does not exist"

**Causa**: Tabelas não foram criadas

**Solução**:
1. Verifique os logs da Vercel para erros no `init_db()`
2. Execute manualmente no SQL Editor do Supabase:
   ```sql
   -- Copie e cole o conteúdo da função init_db() do app.py
   ```

### Erro: "SSL connection required"

**Causa**: Supabase requer SSL

**Solução**:
- O código já está configurado com `sslmode='require'` na função `get_db()`
- Verifique se a connection string tem `?sslmode=require` no final (opcional)

### Banco de dados cheio (500 MB)

**Solução**:
1. Limpe dados antigos:
   ```sql
   DELETE FROM pontuacoes WHERE data < NOW() - INTERVAL '1 year';
   ```
2. Ou faça upgrade para o plano Pro do Supabase ($25/mês, 8 GB)

---

## 💡 Dicas e Boas Práticas

### Segurança:
- ✅ Nunca commite a senha do banco no Git
- ✅ Use variáveis de ambiente para credenciais
- ✅ Troque a senha padrão do admin (`admin123`)
- ✅ Ative Row Level Security (RLS) no Supabase para proteção extra

### Performance:
- ✅ Crie índices para queries frequentes:
  ```sql
  CREATE INDEX idx_clientes_pontos ON clientes(pontos_totais DESC);
  CREATE INDEX idx_pontuacoes_cliente ON pontuacoes(cliente_id);
  ```

### Backup:
- ✅ Supabase faz backup automático (Point-in-time recovery)
- ✅ Para backup manual: SQL Editor → Export → Download SQL

### Monitoramento:
- ✅ Configure alertas no Supabase para uso de recursos
- ✅ Monitore queries lentas no Dashboard → Database → Query Performance

---

## 📚 Recursos Úteis

- **Supabase Docs**: https://supabase.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Vercel Docs**: https://vercel.com/docs
- **psycopg2 Docs**: https://www.psycopg.org/docs/

---

## ✅ Checklist Final

- [ ] Conta Supabase criada
- [ ] Projeto Supabase criado
- [ ] Connection string copiada e senha substituída
- [ ] Variáveis de ambiente configuradas na Vercel
- [ ] Deploy realizado com sucesso
- [ ] Tabelas criadas no banco
- [ ] Aplicação funcionando
- [ ] Login admin testado
- [ ] Cadastro de cliente testado

**Parabéns! Seu projeto está rodando em produção com Supabase PostgreSQL! 🎉**
