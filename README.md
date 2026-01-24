# 🚦 Semáforo Bar - Sistema de Pontuação de Clientes

Sistema moderno e rápido para gerenciar pontuação de clientes do bar, com níveis baseados em semáforo (vermelho, amarelo, verde).

## 🎯 Funcionalidades

### 👥 Gestão de Clientes
- ✅ **Cadastro de Clientes**: Registre clientes com nome, telefone e email
- 🎯 **Sistema de Pontuação**: Adicione pontos por consumo, frequência, bônus e eventos especiais
- 🔍 **Busca**: Filtre clientes rapidamente
- 📋 **Histórico**: Visualize todas as pontuações de cada cliente

### 🚦 Sistema de Níveis
- 🔴 **Vermelho**: 0-199 pontos (Cliente iniciante)
- 🟡 **Amarelo**: 200-499 pontos (Cliente regular)
- 🟢 **Verde**: 500+ pontos (Cliente VIP)
- ⚙️ **Níveis Configuráveis**: Ajuste os pontos mínimos de cada nível

### 📊 Dashboard e Ranking
- 📈 **Estatísticas em Tempo Real**: Acompanhe o desempenho do programa
- 🏆 **Ranking**: Top 10 clientes com mais pontos
- 📊 **Distribuição por Níveis**: Visualize quantos clientes em cada categoria

### 🔐 Painel Administrativo
- 🏪 **Personalização do Bar**: Configure nome e logo do estabelecimento
- 🎨 **Upload de Logo**: Adicione a identidade visual do seu bar
- 🎯 **Configuração de Níveis**: Ajuste os pontos necessários para cada categoria
- 🔒 **Segurança**: Altere a senha de administrador
- 📱 **Interface Moderna**: Design responsivo com Tailwind CSS

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

2. **Execute o aplicativo:**
```bash
python app.py
```

3. **Acesse no navegador:**
```
http://localhost:5000
```

## 📖 Como Usar

### 1. Dashboard
- Visualize estatísticas gerais
- Veja a distribuição de clientes por nível
- Entenda o sistema de pontuação

### 2. Cadastrar Cliente
- Clique em "Novo Cliente"
- Preencha nome (obrigatório), telefone e email
- Cliente começa no nível vermelho (0 pontos)

### 3. Adicionar Pontos
- Na lista de clientes, clique no botão "+"
- Escolha a quantidade de pontos
- Selecione o tipo:
  - **Consumo**: Pontos por compras
  - **Frequência**: Pontos por visitas regulares
  - **Bônus**: Pontos extras promocionais
  - **Evento Especial**: Pontos em datas comemorativas
- Adicione uma descrição (opcional)

### 4. Ranking
- Veja os top 10 clientes
- Acompanhe a evolução dos melhores

## 🎨 Sistema de Níveis

| Nível | Pontos | Descrição |
|-------|--------|-----------|
| 🔴 Vermelho | 0-199 | Cliente iniciante |
| 🟡 Amarelo | 200-499 | Cliente regular |
| 🟢 Verde | 500+ | Cliente VIP |

## 🛠️ Tecnologias

- **Backend**: Flask (Python)
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Banco de Dados**: SQLite
- **Ícones**: Font Awesome

## 📁 Estrutura do Projeto

```
SEMAFORO/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── semaforo.db           # Banco de dados (criado automaticamente)
├── templates/
│   └── index.html        # Interface do usuário
└── README.md             # Este arquivo
```

## 🔧 API Endpoints

- `GET /api/clientes` - Lista todos os clientes
- `POST /api/clientes` - Cadastra novo cliente
- `GET /api/clientes/<id>` - Detalhes de um cliente
- `PUT /api/clientes/<id>` - Atualiza cliente
- `DELETE /api/clientes/<id>` - Remove cliente
- `POST /api/pontuacao` - Adiciona pontos a um cliente
- `GET /api/ranking` - Top 10 clientes
- `GET /api/estatisticas` - Estatísticas gerais

## 💡 Dicas de Uso

1. **Defina critérios de pontuação**: Ex: 1 ponto = R$ 10 gastos
2. **Crie promoções**: Dobre pontos em dias específicos
3. **Recompense frequência**: Pontos extras para visitas semanais
4. **Eventos especiais**: Bônus em aniversários ou datas comemorativas
5. **Metas de nível**: Ofereça benefícios para clientes verdes (VIP)

## 🎁 Sugestões de Recompensas por Nível

### 🔴 Vermelho (0-199 pontos)
- Boas-vindas ao programa
- Desconto de 5% na próxima visita

### 🟡 Amarelo (200-499 pontos)
- Desconto de 10%
- Petisco grátis no aniversário
- Prioridade em reservas

### 🟢 Verde (500+ pontos)
- Desconto de 15%
- Bebida grátis toda semana
- Acesso a eventos exclusivos
- Mesa reservada permanente

## 🔒 Segurança

- Dados armazenados localmente
- Sessões seguras com Flask
- CORS configurado para desenvolvimento

## 🌐 Deploy na Vercel

Para fazer deploy na Vercel, consulte o arquivo [DEPLOY.md](DEPLOY.md) com instruções detalhadas.

**Resumo rápido:**
1. Conecte seu repositório GitHub à Vercel
2. Configure as variáveis de ambiente necessárias
3. Deploy automático a cada push

⚠️ **Importante**: Para produção, considere migrar de SQLite para um banco de dados em nuvem (PostgreSQL, MySQL, etc.)

## 📝 Licença

Projeto livre para uso pessoal e comercial.

---

Desenvolvido com ❤️ para o Semáforo Bar
