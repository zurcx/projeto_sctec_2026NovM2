"""
montar_tabelas.py  -  DOS CSVs BRUTOS ATE A FATO E AS 4 DIMENSOES   (voce completa os trechos com ____)
========================================================================================================
Aqui voce usa as funcoes do src/limpeza.py e aplica as regras de negocio do enunciado (secao 4.2), UMA ETAPA POR VEZ.
Cada etapa tem o numero da regra. O que vem depois de "COMPLETE:" explica o que fazer.

COMO RODAR:   python -m src.montar_tabelas
Ele grava os arquivos em data/processed/ e imprime numeros de conferencia: compare com o anexo 8 do enunciado
(totais de conferencia). Se um numero nao bate, o erro esta na etapa logo acima dele.
"""

import pandas as pd

from src import config, limpeza

# Tabelas de apoio (estao no anexo do enunciado, secao 7)
MODALIDADES = {4: "Concorrência - Eletrônica", 5: "Concorrência - Presencial", 6: "Pregão - Eletrônico",
               7: "Pregão - Presencial", 8: "Dispensa", 9: "Inexigibilidade", 12: "Credenciamento"}
REGIAO = {"AC": "Norte", "AM": "Norte", "AP": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
          "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste", "PE": "Nordeste",
          "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste", "DF": "Centro-Oeste", "GO": "Centro-Oeste",
          "MS": "Centro-Oeste", "MT": "Centro-Oeste", "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
          "PR": "Sul", "RS": "Sul", "SC": "Sul"}
PODER = {"E": "Executivo", "L": "Legislativo", "J": "Judiciário", "N": "Não informado"}


def ler(nome):
    """PRONTA. Le o CSV TUDO COMO TEXTO (dtype=str): assim o CNPJ nao perde o zero da esquerda e nada vira NaN sozinho."""
    return pd.read_csv(config.PASTA_RAW / f"{nome}.csv", dtype=str, keep_default_na=False)


def main():
    compras, itens, resultados = ler("compras"), ler("itens"), ler("resultados")
    print(f"Linhas lidas: compras={len(compras)}  itens={len(itens)}  resultados={len(resultados)}   (prova real: 2042 / 7077 / 15896)")

    # =========================================================================================
    # ETAPA 1 - LIMPAR OS 3 ARQUIVOS  (use as funcoes do src/limpeza.py com .map)
    # =========================================================================================
    # --- compras.csv ---
    # .map(funcao) aplica a funcao em cada linha da coluna.   Regra 10: o CNPJ do orgao e de pessoa juridica ("PJ")
    # COMPLETE: o segundo argumento de limpar_documento e o tipo de pessoa; aqui e sempre "PJ"
    compras["cnpj_orgao"] = compras["cnpj_orgao"].map(lambda v: limpeza.limpar_documento(v, ____))
    # COMPLETE: o nome do orgao deve ser padronizado (maiusculas etc.): passe a funcao limpeza.padronizar_nome (sem parenteses)
    compras["nome_orgao"] = compras["razao_social_orgao"].map(____)
    compras["uf_sigla"] = compras["uf_sigla"].map(limpeza.padronizar_nome)
    compras["uf_nome"] = compras["uf_nome"].map(limpeza.padronizar_nome)
    # Regra 11: o arquivo nao traz a regiao; busque no dicionario REGIAO pela sigla da UF
    # COMPLETE: .map(REGIAO) troca cada sigla (ex.: "DF") pela regiao ("Centro-Oeste")
    compras["regiao"] = compras["uf_sigla"].map(____)
    compras["poder"] = compras["poder_id"].map(PODER).fillna("Não informado")
    compras["modalidade_id"] = compras["modalidade_id"].astype(int)
    # Regra 9: o nome da modalidade vem do codigo (modalidade_id), nao do texto do arquivo
    # COMPLETE: use .map(MODALIDADES) na coluna modalidade_id
    compras["nome_modalidade"] = compras["modalidade_id"].map(____)
    # COMPLETE: converta a data de publicacao com a sua funcao limpeza.converter_data
    compras["data_publicacao"] = compras["data_publicacao"].map(____)
    compras["objeto_compra"] = compras["objeto_compra"].map(limpeza.limpar_texto)

    # --- itens.csv ---
    itens["descricao_item"] = itens["descricao"].map(limpeza.padronizar_nome)
    itens["material_ou_servico"] = itens["material_ou_servico"].map(limpeza.limpar_texto)
    # Regra 12: numeros em texto -> numero. COMPLETE: use limpeza.converter_numero
    for coluna in ["quantidade", "valor_unitario_estimado"]:
        itens[coluna] = itens[coluna].map(____)
    # "sigiloso" vem como texto "True"/"False". COMPLETE: compare o texto em minusculas (.str.lower()) com "true"
    itens["sigiloso"] = itens["sigiloso"].str.lower() == ____
    itens["numero_item"] = itens["numero_item"].astype(int)

    # --- resultados.csv ---
    resultados["numero_item"] = resultados["numero_item"].astype(int)
    resultados["nome_fornecedor"] = resultados["nome_fornecedor"].map(limpeza.padronizar_nome)
    resultados["porte"] = resultados["porte"].map(limpeza.limpar_texto)
    # O CNPJ/CPF do fornecedor depende do tipo da pessoa, que esta na coluna tipo_pessoa (PJ, PF ou PE)
    # COMPLETE: passe o tipo da linha (a variavel tipo) como segundo argumento
    resultados["ni_fornecedor"] = [limpeza.limpar_documento(ni, ____)
                                   for ni, tipo in zip(resultados["ni_fornecedor"], resultados["tipo_pessoa"])]
    for coluna in ["quantidade_homologada", "valor_unitario_homologado"]:
        resultados[coluna] = resultados[coluna].map(limpeza.converter_numero)
    resultados["data_resultado"] = resultados["data_resultado"].map(limpeza.converter_data)
    # Resultado cancelado = a coluna data_cancelamento esta preenchida. COMPLETE: compare com o texto vazio ""
    resultados["cancelado"] = resultados["data_cancelamento"].str.strip() != ____

    # =========================================================================================
    # ETAPA 2 - UM VENCEDOR POR ITEM  (regra 2)
    # =========================================================================================
    # COMPLETE: fique so com os resultados que NAO estao cancelados. O til (~) inverte True/False: ~resultados["cancelado"]
    resultados = resultados[____].copy()
    # ordem 1 = vencedor. Quando a ordem vem vazia, ela vale 1. COMPLETE: preencha os vazios (fillna) com 1
    resultados["ordem"] = pd.to_numeric(resultados["ordem_classificacao_srp"], errors="coerce").fillna(____)
    resultados["sequencial"] = pd.to_numeric(resultados["sequencial_resultado"], errors="coerce").fillna(1)
    # Ordena para o vencedor ficar em primeiro: por item, depois pela ordem, depois pelo sequencial (desempate)
    resultados = resultados.sort_values(["numero_controle_pncp", "numero_item", "ordem", "sequencial"])
    # COMPLETE: mantenha so a PRIMEIRA linha de cada item. Metodo: resultados.drop_duplicates([colunas que identificam o item])
    resultados = resultados.____(["numero_controle_pncp", "numero_item"])

    # =========================================================================================
    # ETAPA 3 - JUNTAR OS 3 ARQUIVOS: SO ENTRAM ITENS COM RESULTADO  (regra 3)
    # =========================================================================================
    # merge junta tabelas pelas colunas em comum. how="inner" fica so com o que existe nos DOIS lados.
    # COMPLETE: escreva how="inner" na primeira junção (itens que nao tem resultado ficam de fora)
    fato = itens.merge(resultados, on=["numero_controle_pncp", "numero_item"], how=____)
    fato = fato.merge(compras, on="numero_controle_pncp")
    print(f"Itens com resultado, antes de rejeitar: {len(fato)}")

    # =========================================================================================
    # ETAPA 4 - VALORES  (regra 5)
    # =========================================================================================
    # Usa-se a quantidade HOMOLOGADA, tanto no estimado quanto no homologado, para a comparacao ser justa.
    qtd_homologada = fato["quantidade_homologada"]
    # COMPLETE: .where(condicao, outro) mantem o valor onde a condicao e verdadeira e usa "outro" onde e falsa.
    # Queremos a quantidade homologada quando ela for maior que 0; senao a quantidade do item. Condicao: qtd_homologada > 0
    fato["quantidade"] = qtd_homologada.where(____, fato["quantidade"])
    # COMPLETE: valor total estimado = valor unitario estimado x quantidade (round(2) arredonda em centavos)
    fato["valor_total_estimado"] = (____).round(2)
    fato["valor_total_homologado"] = (fato["valor_unitario_homologado"] * fato["quantidade"]).round(2)

    # =========================================================================================
    # ETAPA 5 - ITENS REJEITADOS  (regra 4)   (nao precisa criar arquivo: so nao entram na fato)
    # =========================================================================================
    est, hom = fato["valor_total_estimado"], fato["valor_total_homologado"]
    # Dica: ~(coluna > 0) e verdadeiro quando o valor e <= 0 OU esta vazio (NaN). Os sinais: | = "ou"
    rejeitado = (
        ~(fato["quantidade"] > 0)                          # quantidade vazia ou <= 0
        # COMPLETE: valor unitario ESTIMADO ausente ou <= 0
        | ____
        | ~(fato["valor_unitario_homologado"] > 0)         # valor unitario homologado ausente ou <= 0
        | fato["sigiloso"]                                 # orcamento sigiloso
        # COMPLETE: valor total estimado menor que R$ 1  (use est)
        | ____
        # COMPLETE: valor total homologado mais de 1000 vezes o estimado (use hom e est)
        | ____
        | (est > 1e12) | (hom > 1e12)                      # valores acima de R$ 1 trilhao (estouram o DECIMAL do banco)
    )
    print(f"Itens rejeitados (nao entram na fato): {rejeitado.sum()}   (prova real: 99)")
    # COMPLETE: fique so com os itens NAO rejeitados (use ~rejeitado)
    fato = fato[____].copy()

    # =========================================================================================
    # ETAPA 6 - COMPARAVEL E ECONOMIA  (regra 6)
    # =========================================================================================
    est, hom = fato["valor_total_estimado"], fato["valor_total_homologado"]
    razao = hom / est
    # Comparavel = NAO e Credenciamento (modalidade 12) E a razao homologado/estimado esta entre 0,1 e 10.
    # COMPLETE: modalidade diferente de 12;  razao.between(0.1, 10) ja esta escrito logo depois
    fato["comparavel"] = ((fato["modalidade_id"] != ____) & razao.between(____)).astype(int)
    # Economia = estimado - homologado, so nos itens comparaveis (nos demais vale 0)
    # COMPLETE: estimado menos homologado (use est e hom)
    fato["economia_valor"] = (____).where(fato["comparavel"] == 1, 0.0).round(2)

    # =========================================================================================
    # ETAPA 7 - CRONOLOGIA  (regra 7)
    # =========================================================================================
    fato["data_homologacao"] = fato["data_resultado"]
    # Homologar ANTES de publicar e impossivel: a data de homologacao vira vazia (o item continua na fato)
    # COMPLETE: antes = a data de homologacao e menor que a data de publicacao
    antes = ____
    # COMPLETE: nas linhas "antes", coloque None (vazio) na data de homologacao
    fato.loc[antes, "data_homologacao"] = ____
    # ciclo = dias entre a publicacao e a homologacao (so quando existe homologacao)
    # COMPLETE: subtrair duas datas da um "intervalo"; o numero de dias esta em .days
    fato["dias_ciclo"] = [(h - p).____ if h is not None and not pd.isna(h) else None
                          for h, p in zip(fato["data_homologacao"], fato["data_publicacao"])]

    # =========================================================================================
    # ETAPA 8 - PERFIL DO GASTO  (regra 8)
    # =========================================================================================
    # Se o texto cita obra/construcao/reforma/engenharia, e "Obras e engenharia" (essa regra manda sobre as outras)
    texto = fato["descricao_item"].fillna("") + " " + fato["objeto_compra"].fillna("").str.upper()
    eh_obra = texto.str.contains(r"\b(?:OBRAS?|CONSTRUÇÃO|CONSTRUCAO|REFORMA|ENGENHARIA)\b", regex=True)
    fato["perfil_gasto"] = "Bens"
    # COMPLETE: se o campo material_ou_servico comeca com "SERVI" (Servico), o perfil e "Serviços"
    fato.loc[fato["material_ou_servico"].fillna("").str.upper().str.startswith(____), "perfil_gasto"] = "Serviços"
    # COMPLETE: nas linhas eh_obra, o perfil e "Obras e engenharia"
    fato.loc[eh_obra, "perfil_gasto"] = ____

    # =========================================================================================
    # ETAPA 9 - AS 4 DIMENSOES, COM CHAVE SUBSTITUTA (sk_)  (secao 4.3 do enunciado)
    # =========================================================================================
    # Cada dimensao tem UMA linha por valor distinto da chave natural, e a coluna sk_ numera as linhas (1, 2, 3...).
    # dim_orgao: e o EXEMPLO pronto. Leia como funciona e repita o raciocinio nas outras tres.
    dim_orgao = fato.drop_duplicates("cnpj_orgao")[["cnpj_orgao", "nome_orgao", "poder"]].reset_index(drop=True)
    dim_orgao.insert(0, "sk_orgao", dim_orgao.index + 1)

    fato["ni_fornecedor"] = fato["ni_fornecedor"].fillna("NAO-INFORMADO")
    # COMPLETE: uma linha por fornecedor: drop_duplicates pela chave natural "ni_fornecedor"
    dim_fornecedor = fato.____("ni_fornecedor")[["ni_fornecedor", "nome_fornecedor", "tipo_pessoa", "porte"]].reset_index(drop=True)
    dim_fornecedor.insert(0, "sk_fornecedor", dim_fornecedor.index + 1)
    # COMPLETE: uma linha por modalidade: drop_duplicates pela chave natural "modalidade_id"
    dim_modalidade = fato.drop_duplicates(____)[["modalidade_id", "nome_modalidade"]].reset_index(drop=True)
    dim_modalidade.insert(0, "sk_modalidade", dim_modalidade.index + 1)
    # COMPLETE: uma linha por UF: drop_duplicates pela chave natural "uf_sigla"
    dim_localidade = fato.drop_duplicates(____)[["uf_sigla", "uf_nome", "regiao"]].reset_index(drop=True)
    dim_localidade.insert(0, "sk_localidade", dim_localidade.index + 1)

    # Troca a chave natural (CNPJ, sigla...) pela chave substituta (sk_) dentro da fato.
    # dict(zip(a, b)) monta um dicionario {chave natural: sk}; .map usa esse dicionario para trocar os valores.
    for dim, chave, sk in [(dim_orgao, "cnpj_orgao", "sk_orgao"), (dim_fornecedor, "ni_fornecedor", "sk_fornecedor"),
                           (dim_modalidade, "modalidade_id", "sk_modalidade"), (dim_localidade, "uf_sigla", "sk_localidade")]:
        # COMPLETE: fato[sk] recebe a coluna chave da fato trocada pelo dicionario: fato[chave].map(dict(zip(dim[chave], dim[sk])))
        fato[sk] = ____

    colunas = ["numero_controle_pncp", "numero_item", "sk_orgao", "sk_fornecedor", "sk_modalidade", "sk_localidade",
               "data_publicacao", "data_homologacao", "descricao_item", "perfil_gasto", "quantidade",
               "valor_unitario_estimado", "valor_total_estimado", "valor_unitario_homologado", "valor_total_homologado",
               "comparavel", "economia_valor", "dias_ciclo"]
    fato = fato[colunas]

    # =========================================================================================
    # ETAPA 10 - SALVAR E CONFERIR (pronto)
    # =========================================================================================
    config.PASTA_PROCESSED.mkdir(parents=True, exist_ok=True)
    for nome, tabela in [("fato_item_contratado", fato), ("dim_orgao", dim_orgao), ("dim_fornecedor", dim_fornecedor),
                         ("dim_modalidade", dim_modalidade), ("dim_localidade", dim_localidade)]:
        tabela.to_csv(config.PASTA_PROCESSED / f"{nome}.csv", index=False, encoding="utf-8")

    comp = fato["comparavel"] == 1
    est_comp = fato.loc[comp, "valor_total_estimado"].sum()
    print("\n=== CONFERENCIA com o anexo 8 do enunciado (prova real) ===")
    print(f"itens na fato ............ {len(fato)}      (6126)")
    print(f"contratacoes distintas ... {fato['numero_controle_pncp'].nunique()}      (1962)")
    print(f"fornecedores ............. {len(dim_fornecedor)}      (2652)")
    print(f"orgaos (CNPJ) ............ {len(dim_orgao)}       (363)")
    print(f"volume homologado ........ R$ {fato['valor_total_homologado'].sum():,.2f}      (8.044.498.805,74 no formato brasileiro)")
    print(f"itens comparaveis ........ {comp.sum()}      (5457)")
    print(f"economia ................. {100 * fato['economia_valor'].sum() / est_comp:.2f}%      (14,46%)")
    print(f"ciclo medio / maximo ..... {fato['dias_ciclo'].mean():.1f} / {fato['dias_ciclo'].max():.0f} dias      (48,1 / 611)")
    print(f"itens sem ciclo .......... {fato['dias_ciclo'].isna().sum()}      (230)")
    print("perfil (% do volume) ..... ", (100 * fato.groupby("perfil_gasto")["valor_total_homologado"].sum()
                                         / fato["valor_total_homologado"].sum()).round(1).to_dict(), "    (referência: Obras 60,8 | Serviços 36,6 | Bens 2,6)")


if __name__ == "__main__":
    main()
