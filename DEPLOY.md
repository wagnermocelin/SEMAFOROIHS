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

## 🗄️ Configuração do Vercel Postgres (OBRIGATÓRIO)

**✅ O código já está migrado para PostgreSQL!**

### Passo 1: Criar Banco de Dados Vercel Postgres

1. Acesse https://vercel.com/dashboard/stores
2. Clique em **"Create Database"**
3. Selecione **"Postgres"**
4. Escolha um nome (ex: `semaforo-db`)
5. Selecione a região mais próxima
6. Clique em **"Create"**

### Passo 2: Conectar ao Projeto

1. No dashboard do banco criado, clique em **"Connect Project"**
2. Selecione seu projeto: `SEMAFOROIHS`
3. Clique em **"Connect"**
4. A variável `POSTGRES_URL` será automaticamente adicionada ao projeto

### Passo 3: Inicializar o Banco de Dados

Após o primeiro deploy, as tabelas serão criadas automaticamente pela função `init_db()`.

**Estrutura criada:**
- `clientes` - Dados dos clientes
- `pontuacoes` - Histórico de pontos
- `configuracoes` - Configurações do bar
- `produtos` - Produtos disponíveis
- `solicitacoes_pontos` - Solicitações pendentes
- `checkins` - Registro de visitas

### Passo 4: Configurar Variáveis de Ambiente

No dashboard da Vercel, vá em **Settings > Environment Variables** e adicione:

```
SECRET_KEY=<gere com: python -c "import secrets; print(secrets.token_hex(32))">
FLASK_ENV=production
```

**Nota:** `POSTGRES_URL` já foi configurada automaticamente no Passo 2.

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
