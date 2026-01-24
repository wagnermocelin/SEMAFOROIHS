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

## ⚠️ Importante - Banco de Dados

**ATENÇÃO:** SQLite não é recomendado para produção na Vercel devido à natureza serverless.

### Soluções para Produção:

1. **Vercel Postgres** (Recomendado)
   - Criar database em: https://vercel.com/dashboard/stores
   - Atualizar código para usar PostgreSQL

2. **PlanetScale** (MySQL)
   - Criar database em: https://planetscale.com
   - Configurar connection string

3. **Supabase** (PostgreSQL)
   - Criar projeto em: https://supabase.com
   - Usar PostgreSQL connection

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
