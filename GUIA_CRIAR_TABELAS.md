# 🗄️ Guia: Criar Tabelas no Supabase

## 📋 Passo a Passo

### **1. Acessar o SQL Editor do Supabase**

1. Acesse: https://supabase.com/dashboard
2. Faça login (se necessário)
3. Selecione seu projeto: **semaforo-bar**
4. No menu lateral esquerdo, clique em **"SQL Editor"** (ícone de terminal)

### **2. Criar Nova Query**

1. Clique no botão **"New query"** (ou "+ New query")
2. Você verá um editor SQL vazio

### **3. Copiar e Colar o Script**

1. Abra o arquivo: `create_tables_supabase.sql`
2. **Copie TODO o conteúdo** do arquivo (Ctrl+A, Ctrl+C)
3. **Cole no SQL Editor** do Supabase (Ctrl+V)

### **4. Executar o Script**

1. Clique no botão **"Run"** (ou pressione Ctrl+Enter)
2. Aguarde alguns segundos
3. Você verá mensagens de sucesso:
   ```
   Success. No rows returned
   ```

### **5. Verificar Tabelas Criadas**

**Opção A: Via Table Editor**
1. Clique em **"Table Editor"** no menu lateral
2. Você deve ver 6 tabelas:
   - ✅ `checkins`
   - ✅ `clientes`
   - ✅ `configuracoes`
   - ✅ `pontuacoes`
   - ✅ `produtos`
   - ✅ `solicitacoes_pontos`

**Opção B: Via SQL Editor**
Execute esta query:
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

### **6. Verificar Dados Iniciais**

1. Clique em **Table Editor** → **configuracoes**
2. Você deve ver 1 registro:
   - `nome_bar`: "Semáforo Bar"
   - `senha_admin`: "admin123"

---

## ✅ Pronto!

Suas tabelas estão criadas e prontas para uso!

## 🚀 Próximos Passos

### **Opção 1: Importar Dados dos CSVs (Se você tem dados)**

1. No **Table Editor**, selecione a tabela
2. Clique em **"Insert"** → **"Import data from CSV"**
3. Faça upload dos arquivos na ordem:
   - `configuracoes.csv` (pule se já existe)
   - `clientes.csv`
   - `pontuacoes.csv`
   - `produtos.csv`
   - `checkins.csv`

### **Opção 2: Deploy na Vercel (Recomendado)**

Agora que as tabelas estão criadas, você pode fazer o deploy:

1. Acesse: https://vercel.com/dashboard
2. Selecione seu projeto: **SEMAFOROIHS**
3. Vá em **Settings** → **Environment Variables**
4. Configure as variáveis:
   ```
   POSTGRES_URL=postgresql://postgres:$$J25021989j@@db.mofyddgzvhwxaorhpzuq.supabase.co:5432/postgres
   DATABASE_URL=postgresql://postgres:$$J25021989j@@db.mofyddgzvhwxaorhpzuq.supabase.co:5432/postgres
   SECRET_KEY=de307193e1210b5d51bc8586122d3f99867ff647520f6e8889244d7f84d493be
   FLASK_ENV=production
   ```
5. Vá em **Deployments** → **Redeploy**
6. Aguarde o deploy concluir
7. Acesse sua aplicação!

---

## 🔍 Troubleshooting

### Erro: "relation already exists"
**Causa:** Tabelas já foram criadas antes

**Solução:** Tudo bem! As tabelas já existem. Pule para os próximos passos.

### Erro: "permission denied"
**Causa:** Problema de permissões no Supabase

**Solução:**
1. Verifique se você está logado no projeto correto
2. Confirme que você é o owner do projeto

### Tabelas não aparecem no Table Editor
**Causa:** Cache do navegador

**Solução:**
1. Atualize a página (F5)
2. Ou limpe o cache (Ctrl+Shift+R)

---

## 📊 Estrutura das Tabelas

### **clientes**
- Armazena dados dos clientes
- Campos: nome, telefone, email, pontos_totais, nivel

### **pontuacoes**
- Histórico de pontos de cada cliente
- Campos: cliente_id, pontos, tipo, descricao, data

### **configuracoes**
- Configurações do sistema
- Campos: nome_bar, logo_path, níveis de pontos, senha_admin

### **produtos**
- Produtos disponíveis para troca
- Campos: nome, descricao, pontos, ativo

### **solicitacoes_pontos**
- Solicitações de resgate de produtos
- Campos: cliente_id, produto_id, status, pontos_total

### **checkins**
- Registro de visitas dos clientes
- Campos: cliente_id, data_checkin, localizacao

---

**Boa sorte com o deploy! 🚀**
