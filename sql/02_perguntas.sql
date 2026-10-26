-- ==============================================================================
-- PROJETO AVALIATIVO - MÓDULO 2
-- Ficheiro: sql/02_perguntas.sql
-- Objetivo: Respostas formais às 6 Perguntas de Negócio da Controladoria
-- ==============================================================================

USE pncp_controladoria;

-- ------------------------------------------------------------------------------
-- PERGUNTA 1: Economia global do Poder Público
-- Qual é o percentual e o valor financeiro nominal economizado pelo governo 
-- (diferença entre valor estimado e valor homologado)?
-- Regra de negócio: A economia só entra nos itens comparáveis (comparavel = 1).
-- Credenciamento (modalidade_id = 12) e distorções ficam fora da taxa de deságio.
-- ------------------------------------------------------------------------------
SELECT 
    SUM(valor_total_homologado) AS volume_total_homologado,
    SUM(CASE WHEN comparavel = 1 THEN valor_total_estimado ELSE 0 END) AS valor_estimado_comparavel,
    SUM(CASE WHEN comparavel = 1 THEN valor_total_homologado ELSE 0 END) AS valor_homologado_comparavel,
    SUM(economia_valor) AS economia_nominal_reais,
    ROUND((SUM(economia_valor) / NULLIF(SUM(CASE WHEN comparavel = 1 THEN valor_total_estimado ELSE 0 END), 0)) * 100, 2) AS taxa_economia_desagio_pct,
    COUNT(CASE WHEN comparavel = 1 THEN 1 END) AS itens_comparaveis,
    COUNT(*) AS total_itens_base
FROM fato_item_contratado;


-- ------------------------------------------------------------------------------
-- PERGUNTA 2: Concentração e risco de fornecedores
-- Quem são os maiores fornecedores em volume financeiro e qual percentual 
-- do orçamento público está concentrado neles?
-- Mostra os 10 maiores adjudicatários e o percentual sobre o orçamento global.
-- ------------------------------------------------------------------------------
SELECT 
    f.ni_fornecedor AS identificador_fiscal,
    f.nome_fornecedor,
    f.porte,
    f.tipo_pessoa,
    SUM(fat.valor_total_homologado) AS volume_homologado_fornecedor,
    ROUND(
        (SUM(fat.valor_total_homologado) / (SELECT SUM(valor_total_homologado) FROM fato_item_contratado)) * 100, 
        2
    ) AS participacao_orcamento_pct
FROM fato_item_contratado fat
JOIN dim_fornecedor f ON fat.sk_fornecedor = f.sk_fornecedor
GROUP BY f.ni_fornecedor, f.nome_fornecedor, f.porte, f.tipo_pessoa
ORDER BY volume_homologado_fornecedor DESC
LIMIT 10;


-- ------------------------------------------------------------------------------
-- PERGUNTA 3: Eficácia por modalidade
-- Quais modalidades licitatórias trazem maior deságio/economia e quais 
-- concentram o maior volume de recursos?
-- ------------------------------------------------------------------------------
SELECT 
    m.nome_modalidade,
    COUNT(fat.sk_fato) AS qtd_itens,
    SUM(fat.valor_total_homologado) AS volume_homologado,
    ROUND(
        (SUM(fat.valor_total_homologado) / (SELECT SUM(valor_total_homologado) FROM fato_item_contratado)) * 100, 
        2
    ) AS participacao_volume_pct,
    SUM(fat.economia_valor) AS economia_nominal_reais,
    ROUND(
        (SUM(fat.economia_valor) / NULLIF(SUM(CASE WHEN fat.comparavel = 1 THEN fat.valor_total_estimado ELSE 0 END), 0)) * 100, 
        2
    ) AS desagio_pct
FROM fato_item_contratado fat
JOIN dim_modalidade m ON fat.sk_modalidade = m.sk_modalidade
GROUP BY m.nome_modalidade
ORDER BY volume_homologado DESC;


-- ------------------------------------------------------------------------------
-- PERGUNTA 4: Tempo do ciclo de compras
-- Qual a duração média (em dias) entre o lançamento do edital e a sua 
-- homologação final, segmentada por órgão?
-- Regra de negócio: Agrupa pelo NOME padronizado do órgão, considera apenas
-- itens com ciclo válido (COUNT(dias_ciclo)) e filtra órgãos com 5 ou mais certames.
-- ------------------------------------------------------------------------------
SELECT 
    o.nome_orgao,
    COUNT(fat.dias_ciclo) AS certames_com_ciclo,
    COUNT(DISTINCT o.cnpj_orgao) AS unidades_compradoras_distintas,
    ROUND(AVG(fat.dias_ciclo), 1) AS ciclo_medio_dias,
    MAX(fat.dias_ciclo) AS ciclo_maximo_dias,
    MIN(fat.dias_ciclo) AS ciclo_minimo_dias
FROM fato_item_contratado fat
JOIN dim_orgao o ON fat.sk_orgao = o.sk_orgao
WHERE fat.dias_ciclo IS NOT NULL
GROUP BY o.nome_orgao
HAVING COUNT(fat.dias_ciclo) >= 5
ORDER BY ciclo_medio_dias DESC;


-- ------------------------------------------------------------------------------
-- PERGUNTA 5: Distribuição regional
-- Quais estados e regiões concentram as maiores despesas e quais 
-- apresentam os melhores indicadores de desconto?
-- ------------------------------------------------------------------------------
SELECT 
    l.regiao,
    l.uf_sigla,
    COUNT(DISTINCT fat.sk_orgao) AS unidades_compradoras,
    COUNT(fat.sk_fato) AS total_itens,
    SUM(fat.valor_total_homologado) AS volume_homologado,
    ROUND(
        (SUM(fat.valor_total_homologado) / (SELECT SUM(valor_total_homologado) FROM fato_item_contratado)) * 100, 
        2
    ) AS participacao_despesa_pct,
    ROUND(
        (SUM(fat.economia_valor) / NULLIF(SUM(CASE WHEN fat.comparavel = 1 THEN fat.valor_total_estimado ELSE 0 END), 0)) * 100, 
        2
    ) AS desagio_pct
FROM fato_item_contratado fat
JOIN dim_localidade l ON fat.sk_localidade = l.sk_localidade
GROUP BY l.regiao, l.uf_sigla
ORDER BY volume_homologado DESC;


-- ------------------------------------------------------------------------------
-- PERGUNTA 6: Perfil dos gastos
-- Como os recursos se distribuem entre bens, serviços e obras e engenharia?
-- ------------------------------------------------------------------------------
SELECT 
    perfil_gasto,
    COUNT(*) AS total_itens,
    SUM(valor_total_homologado) AS volume_homologado,
    ROUND(
        (SUM(valor_total_homologado) / (SELECT SUM(valor_total_homologado) FROM fato_item_contratado)) * 100, 
        2
    ) AS participacao_volume_pct,
    ROUND(SUM(valor_total_homologado) / COUNT(*), 2) AS ticket_medio_por_item_reais,
    ROUND(
        (SUM(fat.economia_valor) / NULLIF(SUM(CASE WHEN fat.comparavel = 1 THEN fat.valor_total_estimado ELSE 0 END), 0)) * 100, 
        2
    ) AS desagio_pct
FROM fato_item_contratado fat
GROUP BY perfil_gasto
ORDER BY volume_homologado DESC;
