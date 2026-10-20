"""
Módulo de montagem e transformação dimensional das tabelas.
Aplica as decisões de negócio da Controladoria (Seção 4.2 do enunciado)
e valida os totais frente aos números de referência (Seção 8).

Execução:
    python -m src.montar_tabelas
"""

import os
import re

import numpy as np
import pandas as pd

from src.limpeza import (
    converter_data,
    converter_numero,
    eh_nulo,
    limpar_documento,
    limpar_texto,
    padronizar_nome,
    tirar_espacos,
)

# Mapeamento oficial UF -> Região (Seção 7.6)
TABELA_REGIOES = {
    "Norte": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MS", "MT"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"],
}
UF_PARA_REGIAO = {uf: reg for reg, ufs in TABELA_REGIOES.items() for uf in ufs}

# Mapeamento oficial de Modalidades (Seção 7.5)
TABELA_MODALIDADES = {
    4: "Concorrência - Eletrônica",
    5: "Concorrência - Presencial",
    6: "Pregão - Eletrônico",
    7: "Pregão - Presencial",
    8: "Dispensa",
    9: "Inexigibilidade",
    12: "Credenciamento",
}

PODER_NOMES = {
    "E": "Executivo",
    "L": "Legislativo",
    "J": "Judiciário",
    "N": "Não informado",
}


def carregar_dados_brutos():
    """Lê os 3 arquivos CSV da pasta data/raw/ como texto puro."""
    caminho_raw = os.path.join("data", "raw")
    compras = pd.read_csv(os.path.join(caminho_raw, "compras.csv"), dtype=str)
    itens = pd.read_csv(os.path.join(caminho_raw, "itens.csv"), dtype=str)
    resultados = pd.read_csv(os.path.join(caminho_raw, "resultados.csv"), dtype=str)
    return compras, itens, resultados


def processar_dados():
    compras, itens, resultados = carregar_dados_brutos()

    # Contagens brutas iniciais
    total_compras_raw = len(compras)
    total_itens_raw = len(itens)
    total_resultados_raw = len(resultados)

    # ---------------------------------------------------------
    # 1. Higienização de Compras
    # ---------------------------------------------------------
    compras["cnpj_orgao_limpo"] = compras["cnpj_orgao"].apply(
        lambda x: limpar_documento(x, tipo_pessoa="PJ")
    )
    compras["nome_orgao_limpo"] = compras["razao_social_orgao"].apply(padronizar_nome)
    compras["poder_nome"] = compras["poder_id"].map(PODER_NOMES).fillna("Não informado")

    compras["modalidade_id_num"] = (
        pd.to_numeric(compras["modalidade_id"], errors="coerce").fillna(0).astype(int)
    )
    compras["nome_modalidade"] = (
        compras["modalidade_id_num"].map(TABELA_MODALIDADES).fillna("Outros")
    )

    compras["uf_sigla_limpa"] = compras["uf_sigla"].apply(
        lambda x: tirar_espacos(x).upper() if tirar_espacos(x) else None
    )
    compras["uf_nome_limpo"] = compras["uf_nome"].apply(limpar_texto)
    compras["regiao"] = (
        compras["uf_sigla_limpa"].map(UF_PARA_REGIAO).fillna("Não informada")
    )

    compras["data_publicacao_limpa"] = compras["data_publicacao"].apply(converter_data)
    compras["objeto_compra_limpo"] = (
        compras["objeto_compra"].apply(limpar_texto).fillna("")
    )

    # ---------------------------------------------------------
    # 2. Regra 2: Um vencedor por item
    # Descartar data_cancelamento ANTES de ordenar SRP
    # ---------------------------------------------------------
    res_ativos = resultados[resultados["data_cancelamento"].apply(eh_nulo)].copy()

    # Ordem vazia conta como 1
    res_ativos["ordem_num"] = pd.to_numeric(
        res_ativos["ordem_classificacao_srp"], errors="coerce"
    ).fillna(1)
    res_ativos["seq_num"] = pd.to_numeric(
        res_ativos["sequencial_resultado"], errors="coerce"
    ).fillna(999999)

    res_ordenados = res_ativos.sort_values(
        by=["numero_controle_pncp", "numero_item", "ordem_num", "seq_num"]
    )
    vencedores = res_ordenados.drop_duplicates(
        subset=["numero_controle_pncp", "numero_item"], keep="first"
    ).copy()

    # ---------------------------------------------------------
    # 3. Regra 3: Só entram na fato itens com resultado
    # ---------------------------------------------------------
    itens_com_resultado = pd.merge(
        itens, vencedores, on=["numero_controle_pncp", "numero_item"], how="inner"
    )
    qtd_itens_sem_resultado = total_itens_raw - len(itens_com_resultado)

    # ---------------------------------------------------------
    # 4. Regra 5: Valores e Quantidades (feita ANTES da rejeição)
    # ---------------------------------------------------------
    itens_com_resultado["qtd_item_num"] = itens_com_resultado["quantidade"].apply(
        converter_numero
    )
    itens_com_resultado["qtd_hom_num"] = itens_com_resultado[
        "quantidade_homologada"
    ].apply(converter_numero)

    # Quantidade final: se quantidade homologada for vazia ou zero, usa quantidade do item
    itens_com_resultado["quantidade_final"] = np.where(
        itens_com_resultado["qtd_hom_num"].isna()
        | (itens_com_resultado["qtd_hom_num"] <= 0),
        itens_com_resultado["qtd_item_num"],
        itens_com_resultado["qtd_hom_num"],
    )

    itens_com_resultado["vu_estimado"] = itens_com_resultado[
        "valor_unitario_estimado"
    ].apply(converter_numero)
    itens_com_resultado["vu_homologado"] = itens_com_resultado[
        "valor_unitario_homologado"
    ].apply(converter_numero)

    itens_com_resultado["vt_estimado"] = (
        itens_com_resultado["vu_estimado"] * itens_com_resultado["quantidade_final"]
    ).round(2)
    itens_com_resultado["vt_homologado"] = (
        itens_com_resultado["vu_homologado"] * itens_com_resultado["quantidade_final"]
    ).round(2)

    # ---------------------------------------------------------
    # 5. Regra 4: Itens Rejeitados
    # ---------------------------------------------------------
    cond_sigiloso = itens_com_resultado["sigiloso"].str.lower().isin(["true", "1"])
    cond_qtd_inv = itens_com_resultado["quantidade_final"].isna() | (
        itens_com_resultado["quantidade_final"] <= 0
    )
    cond_vue_inv = itens_com_resultado["vu_estimado"].isna() | (
        itens_com_resultado["vu_estimado"] <= 0
    )
    cond_vuh_inv = itens_com_resultado["vu_homologado"].isna() | (
        itens_com_resultado["vu_homologado"] <= 0
    )
    cond_vte_min = itens_com_resultado["vt_estimado"] < 1.0
    cond_vth_ext = itens_com_resultado["vt_homologado"] > (
        1000 * itens_com_resultado["vt_estimado"]
    )
    cond_estouro = (itens_com_resultado["vt_estimado"] > 1e12) | (
        itens_com_resultado["vt_homologado"] > 1e12
    )

    mascara_rejeitados = (
        cond_sigiloso
        | cond_qtd_inv
        | cond_vue_inv
        | cond_vuh_inv
        | cond_vte_min
        | cond_vth_ext
        | cond_estouro
    )
    qtd_rejeitados = mascara_rejeitados.sum()

    fato = itens_com_resultado[~mascara_rejeitados].copy()

    # Cruzamento com Compras para herdar datas, órgão, modalidade e localidade
    fato = pd.merge(
        fato,
        compras[
            [
                "numero_controle_pncp",
                "cnpj_orgao_limpo",
                "modalidade_id_num",
                "uf_sigla_limpa",
                "data_publicacao_limpa",
                "objeto_compra_limpo",
            ]
        ],
        on="numero_controle_pncp",
        how="inner",
    )

    # ---------------------------------------------------------
    # 6. Regra 7: Cronologia e dias de ciclo
    # Homologação anterior à publicação anula a data e o ciclo
    # ---------------------------------------------------------
    fato["data_resultado_limpa"] = fato["data_resultado"].apply(converter_data)

    cond_cronologia_valida = (
        fato["data_resultado_limpa"].notna()
        & fato["data_publicacao_limpa"].notna()
        & (fato["data_resultado_limpa"] >= fato["data_publicacao_limpa"])
    )

    fato["data_homologacao"] = np.where(
        cond_cronologia_valida, fato["data_resultado_limpa"], pd.NaT
    )
    fato["dias_ciclo"] = np.where(
        cond_cronologia_valida,
        (
            pd.to_datetime(fato["data_homologacao"])
            - pd.to_datetime(fato["data_publicacao_limpa"])
        ).dt.days,
        np.nan,
    )

    # ---------------------------------------------------------
    # 7. Regra 6: Comparabilidade e Economia
    # ---------------------------------------------------------
    razao_valores = fato["vt_homologado"] / fato["vt_estimado"]
    fato["comparavel"] = np.where(
        (fato["modalidade_id_num"] != 12)
        & (razao_valores >= 0.1)
        & (razao_valores <= 10.0),
        1,
        0,
    )
    fato["economia_valor"] = np.where(
        fato["comparavel"] == 1, fato["vt_estimado"] - fato["vt_homologado"], np.nan
    )

    # ---------------------------------------------------------
    # 8. Regra 8: Perfil do gasto (\b regex de obras)
    # ---------------------------------------------------------
    padrao_obras = re.compile(
        r"\b(obra|construcao|construção|reforma|engenharia)\b", re.IGNORECASE
    )

    def classificar_perfil(row):
        texto = f"{row.get('descricao', '')} {row.get('objeto_compra_limpo', '')}"
        if padrao_obras.search(texto):
            return "Obras e engenharia"
        mat_serv = str(row.get("material_ou_servico", "")).strip().title()
        if mat_serv == "Serviço":
            return "Serviços"
        return "Bens"

    fato["perfil_gasto"] = fato.apply(classificar_perfil, axis=1)

    # ---------------------------------------------------------
    # Higienização de campos do fornecedor para a dimensão
    # ---------------------------------------------------------
    fato["tipo_pessoa_limpo"] = fato["tipo_pessoa"].apply(limpar_texto)
    fato["ni_fornecedor_limpo"] = fato.apply(
        lambda r: limpar_documento(
            r["ni_fornecedor"], tipo_pessoa=r["tipo_pessoa_limpo"]
        ),
        axis=1,
    )
    fato["nome_fornecedor_limpo"] = fato["nome_fornecedor"].apply(limpar_texto)
    fato["porte_fornecedor_limpo"] = (
        fato["porte"].apply(limpar_texto).fillna("Não informado")
    )

    # ---------------------------------------------------------
    # Cálculos para a Conferência (Prova Real)
    # ---------------------------------------------------------
    itens_fato = len(fato)
    contratacoes_distintas = fato["numero_controle_pncp"].nunique()
    fornecedores_distintos = fato["ni_fornecedor_limpo"].dropna().nunique()
    unidades_compradoras = fato["cnpj_orgao_limpo"].dropna().nunique()

    soma_homologado = fato["vt_homologado"].sum()
    soma_estimado_total = fato["vt_estimado"].sum()

    base_comp = fato[fato["comparavel"] == 1]
    itens_comparaveis = len(base_comp)
    soma_estimado_comp = base_comp["vt_estimado"].sum()
    economia_nominal = base_comp["economia_valor"].sum()
    economia_pct = (
        (economia_nominal / soma_estimado_comp) * 100 if soma_estimado_comp > 0 else 0
    )

    itens_sobrepreco = (fato["vt_homologado"] > fato["vt_estimado"]).sum()

    itens_com_ciclo = fato["dias_ciclo"].notna().sum()
    ciclo_medio = fato["dias_ciclo"].mean()
    ciclo_maximo = fato["dias_ciclo"].max()
    itens_sem_ciclo = itens_fato - itens_com_ciclo

    perfil_shares = (
        fato.groupby("perfil_gasto")["vt_homologado"].sum() / soma_homologado * 100
    )
    perfil_counts = fato["perfil_gasto"].value_counts()

    # ---------------------------------------------------------
    # Exibição do Relatório de Conferência
    # ---------------------------------------------------------
    print("\n" + "=" * 80)
    print("PROVA REAL - CONFERÊNCIA COM O GABARITO DO PROFESSOR (SEÇÃO 8)")
    print("=" * 80)
    print(f"{'Métrica / Indicador':<45} | {'Esperado':<16} | {'Obtido'}")
    print("-" * 80)
    print(
        f"{'Contratações (compras.csv)':<45} | 2.042            | {total_compras_raw}"
    )
    print(f"{'Itens (itens.csv)':<45} | 7.077            | {total_itens_raw}")
    print(
        f"{'Itens sem resultado homologado':<45} | 852              | {qtd_itens_sem_resultado}"
    )
    print(
        f"{'Resultados (resultados.csv)':<45} | 15.896           | {total_resultados_raw}"
    )
    print(f"{'Itens na Fato':<45} | 6.126            | {itens_fato}")
    print(f"{'Itens rejeitados (inválidos)':<45} | 99               | {qtd_rejeitados}")
    print(
        f"{'Contratações distintas na Fato':<45} | 1.962            | {contratacoes_distintas}"
    )
    print(
        f"{'Fornecedores distintos':<45} | ~2.652           | {fornecedores_distintos}"
    )
    print(
        f"{'Unidades compradoras (CNPJs)':<45} | 363              | {unidades_compradoras}"
    )
    print(
        f"{'Soma do valor homologado':<45} | R$ 8.044.498.805 | R$ {soma_homologado:,.2f}".replace(
            ",", "X"
        )
        .replace(".", ",")
        .replace("X", ".")
    )
    print(
        f"{'Soma estimado (comparável)':<45} | R$ 6.867.663.469 | R$ {soma_estimado_comp:,.2f}".replace(
            ",", "X"
        )
        .replace(".", ",")
        .replace("X", ".")
    )
    print(f"{'Itens na base comparável':<45} | 5.457            | {itens_comparaveis}")
    print(
        f"{'Economia nominal':<45} | R$ 992.861.686,95| R$ {economia_nominal:,.2f}".replace(
            ",", "X"
        )
        .replace(".", ",")
        .replace("X", ".")
    )
    print(
        f"{'Economia % na base comparável':<45} | 14,46%           | {economia_pct:.2f}%"
    )
    print(f"{'Itens com sobrepreço':<45} | 27               | {itens_sobrepreco}")
    print(f"{'Itens com ciclo válido':<45} | 5.896            | {itens_com_ciclo}")
    print(f"{'Ciclo médio (dias)':<45} | 48,1             | {ciclo_medio:.1f}")
    print(f"{'Ciclo máximo (dias)':<45} | 611              | {int(ciclo_maximo)}")
    print(f"{'Itens sem ciclo':<45} | 230              | {itens_sem_ciclo}")
    print("-" * 80)
    print("Perfil de gastos:")
    for perf in ["Obras e engenharia", "Serviços", "Bens"]:
        pct = perfil_shares.get(perf, 0)
        cnt = perfil_counts.get(perf, 0)
        print(f"  * {perf:<20}: {pct:.1f}% ({cnt} itens)")
    print("=" * 80 + "\n")

    return compras, fato


if __name__ == "__main__":
    processar_dados()
