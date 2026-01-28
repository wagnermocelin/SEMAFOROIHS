-- ============================================
-- ATUALIZAR NOME DO BAR NO SUPABASE
-- ============================================
-- Execute este script no SQL Editor do Supabase Dashboard
-- https://supabase.com/dashboard → Seu Projeto → SQL Editor

-- Atualizar o nome do bar para "Semáforo I Hop So"
UPDATE configuracoes 
SET nome_bar = 'Semáforo I Hop So'
WHERE id = 1;

-- Verificar a atualização
SELECT * FROM configuracoes;
