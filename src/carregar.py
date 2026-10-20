"""
carregar.py  -  CARGA NO MYSQL   (voce completa os trechos com ____)
====================================================================
Passos:  1) cria o banco e as tabelas (executa o sql/01_criar_banco.sql)
         2) carrega as 4 DIMENSOES   3) carrega a FATO (as dimensoes vem primeiro!)   4) confere as contagens
Usa so o que o kit ja traz: src/config.py e src/banco.py (conectar, executar_script, inserir_em_lote, consultar).
O sql/01_criar_banco.sql e o SEU script (veja a secao 4.3 do enunciado): crie esse arquivo antes de rodar a carga.
Ele deve comecar com CREATE DATABASE IF NOT EXISTS pncp_controladoria; e USE pncp_controladoria;
Dica: veja a carga em lote do 1_extrair.py do Desafio Transparencia (banco.inserir_em_lote).

COMO RODAR (depois do montar_tabelas):   python -m src.carregar
"""

import pandas as pd

from src import banco, config


def ler(nome, **opcoes):
    """PRONTA. Le um CSV de data/processed. Campo vazio vira NaN (que mais abaixo vira None = NULL no banco)."""
    return pd.read_csv(config.PASTA_PROCESSED / f"{nome}.csv", keep_default_na=False, na_values=[""], **opcoes)


def tuplas(tabela, colunas):
    """PRONTA. Transforma o DataFrame em uma lista de tuplas simples, que e o que o banco entende.
    Valor vazio (NaN) vira None, que o banco grava como NULL."""
    dados = tabela[colunas].astype(object)
    dados = dados.where(dados.notna(), None)
    return [tuple(linha) for linha in dados.itertuples(index=False, name=None)]


def inserir(con, tabela, colunas, dados):
    """Monta o INSERT INTO ... VALUES (%s, %s, ...) e envia todas as linhas de uma vez."""
    # Um %s para cada coluna. COMPLETE: monte uma lista com "%s" repetido len(colunas) vezes:  ["%s"] * len(colunas)
    marcadores = ", ".join(____)
    sql = f"INSERT INTO {tabela} ({', '.join(colunas)}) VALUES ({marcadores})"
    # COMPLETE: envie em lote com banco.inserir_em_lote(conexao, sql, linhas)
    banco.____(con, sql, tuplas(dados, colunas))
    print(f"   {tabela}: {len(dados)} linhas")


def main():
    # 1) Banco e tabelas. O script cria o banco, por isso conectamos sem escolher o database.
    con = banco.conectar(com_database=False)
    # COMPLETE: execute o arquivo SQL de criacao: banco.executar_script(conexao, caminho_do_arquivo)
    banco.____(con, config.PASTA_SQL / "01_criar_banco.sql")
    con.close()
    con = banco.conectar()

    # 2) Dimensoes PRIMEIRO: a fato tem chave estrangeira para elas, entao elas precisam existir antes.
    print("Carga:")
    for nome, colunas in [("dim_orgao", ["sk_orgao", "cnpj_orgao", "nome_orgao", "poder"]),
                          ("dim_fornecedor", ["sk_fornecedor", "ni_fornecedor", "nome_fornecedor", "tipo_pessoa", "porte"]),
                          ("dim_modalidade", ["sk_modalidade", "modalidade_id", "nome_modalidade"]),
                          ("dim_localidade", ["sk_localidade", "uf_sigla", "uf_nome", "regiao"])]:
        # dtype=str: o CNPJ nao pode perder o zero da esquerda ao ser lido
        inserir(con, nome, colunas, ler(nome, dtype=str))

    # 3) Fato (depois das dimensoes)
    fato = ler("fato_item_contratado")
    # dias_ciclo vem como 48.0 (decimal) porque tem vazios; o banco quer inteiro. COMPLETE: converta para o tipo "Int64"
    fato["dias_ciclo"] = fato["dias_ciclo"].astype(____)
    colunas = ["numero_controle_pncp", "numero_item", "sk_orgao", "sk_fornecedor", "sk_modalidade", "sk_localidade",
               "data_publicacao", "data_homologacao", "descricao_item", "perfil_gasto", "quantidade",
               "valor_unitario_estimado", "valor_total_estimado", "valor_unitario_homologado", "valor_total_homologado",
               "comparavel", "economia_valor", "dias_ciclo"]
    # COMPLETE: o nome da tabela da fato
    inserir(con, ____, colunas, fato)

    # 4) Conferencia: o que esta no banco tem que bater com a prova real (anexo 8 do enunciado)
    print("Conferencia:")
    for tabela, esperado in [("fato_item_contratado", 6126), ("dim_orgao", 363), ("dim_fornecedor", 2652),
                             ("dim_modalidade", 7), ("dim_localidade", 27)]:
        # COMPLETE: conte as linhas da tabela com SELECT COUNT(*)
        n = banco.consultar(con, f"SELECT ____ FROM {tabela}")[0][0]
        print(f"   {tabela}: {n} (esperado {esperado}) -> {'OK' if n == esperado else 'DIVERGENTE'}")
    con.close()


if __name__ == "__main__":
    main()
