# Dashboard Executivo: Inteligência de Compras PNCP (Power BI)

![Imagem resultado tratativa de dados](img/dashboard.png)

##  Visão Geral do Projeto

Este projeto entrega um dashboard executivo limpo, profissional e responsivo em formato 16:9, desenvolvido no Power BI com foco na auditoria e análise de dados de compras públicas do **PNCP (Portal Nacional de Contratações Públicas)**. Desenhado especificamente para a Controladoria e alta gestão (C-level), o painel destaca volumes de contratação, concentração de fornecedores e eficiência de preços através de um layout em três níveis, totalmente livre de barras de rolagem.

![Imagem resultado tratativa de dados](img/screenshot-20261020-212509.png)

## Estrutura e Layout do Dashboard




O dashboard está estruturado em três blocos visuais principais otimizados para leitura executiva rápida:

1. **Seção Superior:** Cartões de visão geral e principais indicadores (KPI cards).

2. **Seção Intermédia (Lado a Lado):**

   * **Volume Homologado por Modalidade:** Gráfico de barras horizontais exibindo a distribuição do poder de compra por modalidade licitatória.

   * **Top 6 Fornecedores vs. "Outros" (Gráfico de Barras Horizontais):** Análise granular de fornecedores agrupando a cauda longa numa categoria consolidada para evitar poluição visual.

3. **Seção Inferior (Base):**

   * **Deságio vs. Média Geral (p.p.) (Gráfico de Barras Verticais):** Avalia o desempenho de desconto por modalidade de contratação comparado à linha de base global.

##  Modelo de Dados e Esquema Relacional

O modelo relacional em estrela (*Star Schema*) é composto por tabelas de dimensão otimizadas ligadas à tabela fato transacional:

```
dim_modalidade (1) -------< fato_item_contratado (*)
dim_fornecedor (1) -------< fato_item_contratado (*)

```

* **`dim_modalidade`**: Modalidades de contratação extraídas e normalizadas do PNCP.

* **`dim_fornecedor`**: Dados mestres de fornecedores aprimorados com lógica de agrupamento e ordenação personalizada.

* **`fato_item_contratado`**: Tabela transacional de itens contratados capturando valores estimados, valores homologados e métricas de desempenho.

## Principais Cálculos DAX e Otimizações

### 1. Volume Homologado

```
Volume Homologado = SUM(fato_item_contratado[valor_total_homologado])

```

### 2. Agrupamento de Fornecedores (Top 6 + "Outros / Demais")

Para evitar erros de capacidade de memória (estouro com `RANKX` em colunas calculadas) e manter uma distribuição limpa:

```
Fornecedor Agrupado = 
VAR _Total = CALCULATE(SUM(fato_item_contratado[valor_total_homologado]))
VAR _Ranking = 
    IF(
        ISBLANK(_Total) || _Total = 0,
        BLANK(),
        RANKX(
            ALL(dim_fornecedor),
            CALCULATE(SUM(fato_item_contratado[valor_total_homologado])),
            ,
            DESC,
            Dense
        )
    )
RETURN
IF(
    ISBLANK(_Ranking),
    BLANK(),
    IF(_Ranking <= 6, dim_fornecedor[nome_fornecedor], "Outros / Demais")
)

```

### 3. Deságio vs. Média Geral (p.p.)

Calcula a economia percentual comparando o desconto de cada modalidade contra a linha de base global:

```
Desagio vs Media Geral (p.p.) = 
VAR _DesagioModalidade = 
    DIVIDE(
        SUM(fato_item_contratado[valor_total_estimado]) - SUM(fato_item_contratado[valor_total_homologado]),
        SUM(fato_item_contratado[valor_total_estimado]),
        0
    )
VAR _MediaGeral = 
    CALCULATE(
        DIVIDE(
            SUM(fato_item_contratado[valor_total_estimado]) - SUM(fato_item_contratado[valor_total_homologado]),
            SUM(fato_item_contratado[valor_total_estimado]),
            0
        ),
        ALL(dim_modalidade)
    )
RETURN
(_DesagioModalidade - _MediaGeral) * 100

```

## Sprints (Metodologia Ágil)

O desenvolvimento deste painel foi planejado e executado em 3 Sprints de 1 semana cada, focando na entrega iterativa de valor para a Controladoria:

![Imagem resultado tratativa de dados](img/Sprints.png)

### 🟢 Sprint 1: Fundação, Ingestão e Modelo de Dados (Semana 1)

* **Objetivo:** Estabelecer a infraestrutura de dados e relacionamentos sem sobrecarregar a memória do Power BI.

* **Backlog Executado:**

  * Conexão e limpeza inicial das bases do PNCP.

  * Criação do modelo em estrela entre `dim_modalidade`, `dim_fornecedor` e `fato_item_contratado`.

  * Resolução de erros de capacidade através da otimização de medidas e exclusão de colunas calculadas redundantes.

* **Entregável:** Modelo de dados íntegro e testado contra estouros de memória.

### 🟡 Sprint 2: Métricas DAX e Construção dos Visuais (Semana 2)

* **Objetivo:** Desenvolver os cálculos centrais e estruturar o layout nos três níveis visuais.

* **Backlog Executado:**

  * Desenvolvimento da medida de `Volume Homologado`.

  * Criação da lógica otimizada para o Top 6 + "Outros / Demais" em `dim_fornecedor`.

  * Implementação da medida de `Desagio vs Media Geral (p.p.)` utilizando o delta entre valores estimados e homologados.

  * Montagem dos gráficos de barras horizontais e verticais na tela.

* **Entregável:** Dashboard funcional com todas as métricas calculadas e exibidas.

### 🔵 Sprint 3: Polimento Executivo, Identidade Visual e Homologação (Semana 3)

* **Objetivo:** Garantir a responsividade 16:9, aplicação do tema corporativo e validação com os stakeholders.

* **Backlog Executado:**

  * Importação e aplicação do tema corporativo customizado (`tema_executivo.json`).

  * Ativação e formatação de rótulos de dados (*Data Labels*) para leitura rápida.

  * Ajuste de margens e alinhamentos para assegurar ausência total de barras de rolagem.

  * Homologação final com a Controladoria.

* **Entregável:** Produto pronto para apresentação C-level e publicação no Power BI Service.

## Identidade Visual e Tema

O dashboard utiliza um tema de conformidade corporativa para assegurar sobriedade, formalidade e legibilidade imediata:

* **Fundo da Tela (Canvas):** Off-White / Cinza Gelo (`#F4F5F7`)

* **Elementos Primários:** Azul Marinho Executivo (`#0F172A`)

* **Elementos Secundários:** Azul Petróleo / Teal (`#0D9488` / `#0EA5E9`)

* **Métricas de Economia / Positivas:** Verde Corporativo (`#10B981`)

* **Agrupamento de Cauda ("Outros"):** Cinza Chumbo Suave (`#64748B`)
