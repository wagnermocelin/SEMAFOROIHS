# Deploy na Vercel - Semáforo Bar

## 📋 Pré-requisitos

1. Conta na Vercel (https://vercel.com)
2. Vercel CLI instalado (opcional): `npm i -g vercel`
3. Repositório Git configurado

## 🚀 Passos para Deploy

### Opção 1: Deploy via Dashboard Vercel (Recomendado)

1. Acesse https://vercel.com/dashboard
2. Clique em "Add New Project"
3. Importe o repositório do GitHub: `wagnermocelin/SEMAFOROIHS`
4. Configure as seguintes variáveis de ambiente (se necessário):
   - `FLASK_ENV=production`
5. Clique em "Deploy"

### Opção 2: Deploy via CLI

```bash
# Instalar Vercel CLI (se ainda não tiver)
npm i -g vercel

# No diretório do projeto, executar:
vercel

# Para deploy em produção:
vercel --prod
```

## 🗄️ Configuração do Supabase PostgreSQL (OBRIGATÓRIO)

**✅ O código já está migrado para PostgreSQL!**

### Passo 1: Criar Projeto no Supabase

1. Acesse https://supabase.com
2. Faça login (GitHub, Google ou email)
3. Clique em **"New Project"**
4. Preencha:
   - **Name**: `semaforo-bar`
   - **Database Password**: Crie uma senha forte (ANOTE!)
   - **Region**: South America (São Paulo) ou mais próxima
   - **Plan**: Free (gratuito)
5. Clique em **"Create new project"**
6. Aguarde 1-2 minutos

### Passo 2: Obter Connection String

1. No projeto, clique em **Settings** (engrenagem)
2. Vá em **Database**
3. Em **Connection string**, selecione **URI**
4. Copie a URL e substitua `[YOUR-PASSWORD]` pela senha do Passo 1

**Formato:**
```
postgresql://postgres:SuaSenha@db.xxxxx.supabase.co:5432/postgres
```

### Passo 3: Configurar Variáveis de Ambiente na Vercel

No dashboard da Vercel, vá em **Settings > Environment Variables** e adicione:

```
POSTGRES_URL=<connection string do Supabase>
DATABASE_URL=<mesma connection string>
SECRET_KEY=<gere com: python -c "import secrets; print(secrets.token_hex(32))">
FLASK_ENV=production
```

### Passo 4: Deploy e Inicialização

Após configurar as variáveis:
1. Faça redeploy na Vercel
2. As tabelas serão criadas automaticamente no primeiro acesso
3. Verifique no Supabase → **Table Editor**

**📖 Para guia detalhado, consulte:** [SUPABASE_SETUP.md](SUPABASE_SETUP.md)

## 📁 Arquivos de Configuração

- `vercel.json` - Configuração de build e rotas
- `requirements.txt` - Dependências Python
- `.vercelignore` - Arquivos ignorados no deploy

## 🔧 Configurações Aplicadas

- ✅ Serverless Functions configuradas
- ✅ Rotas estáticas para `/static`
- ✅ Templates Flask configurados
- ✅ CORS habilitado

## 📝 Notas

- O banco de dados SQLite local não será persistido entre deploys
- Considere migrar para um banco de dados em nuvem para produção
- Arquivos estáticos são servidos diretamente pela Vercel
- Sessões Flask podem precisar de configuração adicional para produção

## 🔗 Links Úteis

- Documentação Vercel Python: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- Vercel CLI: https://vercel.com/docs/cli
