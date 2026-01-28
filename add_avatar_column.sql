-- ============================================
-- ADICIONAR COLUNA AVATAR_URL NA TABELA CLIENTES
-- ============================================
-- Execute este script no SQL Editor do Supabase Dashboard
-- https://supabase.com/dashboard → Seu Projeto → SQL Editor

-- Adicionar coluna avatar_url se não existir
ALTER TABLE clientes 
ADD COLUMN IF NOT EXISTS avatar_url TEXT;

-- Verificar a alteração
SELECT id, nome, avatar_url FROM clientes LIMIT 5;
