-- ============================================
-- SCRIPT PARA CRIAR TABELAS NO SUPABASE
-- ============================================
-- Execute este script no SQL Editor do Supabase Dashboard
-- https://supabase.com/dashboard → Seu Projeto → SQL Editor

-- 1. Tabela de Configurações
CREATE TABLE IF NOT EXISTS configuracoes (
    id SERIAL PRIMARY KEY,
    nome_bar VARCHAR(255) DEFAULT 'Semáforo Bar',
    logo_path TEXT,
    pontos_vermelho_min INTEGER DEFAULT 0,
    pontos_amarelo_min INTEGER DEFAULT 200,
    pontos_verde_min INTEGER DEFAULT 500,
    senha_admin VARCHAR(255) DEFAULT 'admin123'
);

-- Inserir configuração padrão
INSERT INTO configuracoes (nome_bar, senha_admin) 
VALUES ('Semáforo Bar', 'admin123')
ON CONFLICT DO NOTHING;

-- 2. Tabela de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    email VARCHAR(255),
    senha VARCHAR(255),
    data_cadastro TIMESTAMP DEFAULT NOW(),
    pontos_totais INTEGER DEFAULT 0,
    nivel VARCHAR(20) DEFAULT 'vermelho',
    ultima_visita TIMESTAMP
);

-- Índice para melhorar performance de busca por pontos
CREATE INDEX IF NOT EXISTS idx_clientes_pontos ON clientes(pontos_totais DESC);

-- 3. Tabela de Pontuações
CREATE TABLE IF NOT EXISTS pontuacoes (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    pontos INTEGER NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    descricao TEXT,
    data TIMESTAMP DEFAULT NOW(),
    data_validade TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
);

-- Índice para melhorar performance de busca por cliente
CREATE INDEX IF NOT EXISTS idx_pontuacoes_cliente ON pontuacoes(cliente_id);

-- 4. Tabela de Produtos
CREATE TABLE IF NOT EXISTS produtos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    pontos INTEGER NOT NULL,
    ativo INTEGER DEFAULT 1,
    data_cadastro TIMESTAMP DEFAULT NOW()
);

-- 5. Tabela de Solicitações de Pontos
CREATE TABLE IF NOT EXISTS solicitacoes_pontos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER DEFAULT 1,
    pontos_total INTEGER NOT NULL,
    status TEXT DEFAULT 'pendente',
    observacao TEXT,
    data_solicitacao TIMESTAMP DEFAULT NOW(),
    data_validacao TIMESTAMP,
    validado_por VARCHAR(255),
    FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos (id) ON DELETE CASCADE
);

-- 6. Tabela de Checkins
CREATE TABLE IF NOT EXISTS checkins (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER NOT NULL,
    data_checkin TIMESTAMP DEFAULT NOW(),
    localizacao TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE CASCADE
);

-- Índice para melhorar performance de busca por data
CREATE INDEX IF NOT EXISTS idx_checkins_data ON checkins(data_checkin DESC);

-- ============================================
-- VERIFICAÇÃO
-- ============================================
-- Execute esta query para verificar se as tabelas foram criadas:

SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as num_colunas
FROM information_schema.tables t
WHERE table_schema = 'public'
ORDER BY table_name;

-- ============================================
-- SUCESSO!
-- ============================================
-- Se você ver as 6 tabelas listadas, está tudo pronto!
-- Tabelas criadas:
-- 1. checkins
-- 2. clientes
-- 3. configuracoes
-- 4. pontuacoes
-- 5. produtos
-- 6. solicitacoes_pontos
