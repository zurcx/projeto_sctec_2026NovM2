"""
Módulo de ingestão automatizada e carga em lote no MySQL.
Cria o banco se não existir, executa o DDL (sql/01_criar_banco.sql),
popula as 4 dimensões e a fato com integridade referencial.

Execução:
    python -m src.carregar
"""

import os

import pandas as pd
from sqlalchemy import text

from src.banco import get_engine, get_engine_servidor
from src.montar_tabelas import processar_dados


def executar_ddl():
    """Lê e executa o script SQL de criação do banco e tabelas no servidor."""
    engine_server = get_engine_servidor()
    caminho_sql = os.path.join("sql", "01_criar_banco.sql")
    print(f"Executando DDL: {caminho_sql}...")

    with open(caminho_sql, "r", encoding="utf-8") as f:
        comandos_sql = f.read()

    comandos = [c.strip() for c in comandos_sql.split(";") if c.strip()]

    with engine_server.begin() as conn:
        for cmd in comandos:
            conn.execute(text(cmd))
    print("✔ Banco de dados, tabelas e restrições criados com sucesso!")


def carregar_dados():
    # 1. Cria o banco e as tabelas conectando ao servidor MySQL raiz
    executar_ddl()

    # 2. Conecta ao banco de dados pncp_controladoria recém-criado
    engine = get_engine()

    # 3. Processa o pipeline de limpeza e regras de negócio
    print("\nProcessando dados com regras de negócio...")
    compras, fato = processar_dados()

    with engine.begin() as conn:
        # Limpa dados existentes para recarga idempotente (ordem inversa de FK)
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        conn.execute(text("TRUNCATE TABLE fato_item_contratado;"))
        conn.execute(text("DELETE FROM dim_orgao WHERE sk_orgao != -1;"))
        conn.execute(text("DELETE FROM dim_fornecedor WHERE sk_fornecedor != -1;"))
        conn.execute(text("TRUNCATE TABLE dim_modalidade;"))
        conn.execute(text("TRUNCATE TABLE dim_localidade;"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

        # -------------------------------------------------------------
        # 4. Carga da dim_localidade (27 UFs)
        # -------------------------------------------------------------
        print("\nCarregando dim_localidade...")
        dim_localidade = (
            compras[["uf_sigla_limpa", "uf_nome_limpo", "regiao"]]
            .dropna(subset=["uf_sigla_limpa"])
            .drop_duplicates(subset=["uf_sigla_limpa"])
            .copy()
        )
        dim_localidade.columns = ["uf_sigla", "uf_nome", "regiao"]
        dim_localidade.to_sql(
            "dim_localidade", con=conn, if_exists="append", index=False
        )
        print(f"✔ dim_localidade: {len(dim_localidade)} linhas inseridas.")

        # -------------------------------------------------------------
        # 5. Carga da dim_modalidade (7 modalidades)
        # -------------------------------------------------------------
        print("Carregando dim_modalidade...")
        dim_modalidade = (
            compras[["modalidade_id_num", "nome_modalidade"]]
            .drop_duplicates(subset=["modalidade_id_num"])
            .copy()
        )
        dim_modalidade.columns = ["modalidade_id", "nome_modalidade"]
        dim_modalidade.to_sql(
            "dim_modalidade", con=conn, if_exists="append", index=False
        )
        print(f"✔ dim_modalidade: {len(dim_modalidade)} linhas inseridas.")

        # -------------------------------------------------------------
        # 6. Carga da dim_orgao (363 CNPJs distintos)
        # -------------------------------------------------------------
        print("Carregando dim_orgao...")
        dim_orgao = (
            compras[["cnpj_orgao_limpo", "nome_orgao_limpo", "poder_nome"]]
            .dropna(subset=["cnpj_orgao_limpo"])
            .drop_duplicates(subset=["cnpj_orgao_limpo"])
            .copy()
        )
        dim_orgao.columns = ["cnpj_orgao", "nome_orgao", "poder"]
        dim_orgao.to_sql("dim_orgao", con=conn, if_exists="append", index=False)
        print(f"✔ dim_orgao: {len(dim_orgao)} linhas inseridas.")

        # -------------------------------------------------------------
        # 7. Carga da dim_fornecedor (~2.652 fornecedores)
        # -------------------------------------------------------------
        print("Carregando dim_fornecedor...")
        dim_fornecedor = (
            fato[
                [
                    "ni_fornecedor_limpo",
                    "nome_fornecedor_limpo",
                    "tipo_pessoa_limpo",
                    "porte_fornecedor_limpo",
                ]
            ]
            .dropna(subset=["ni_fornecedor_limpo"])
            .drop_duplicates(subset=["ni_fornecedor_limpo"])
            .copy()
        )
        dim_fornecedor.columns = [
            "ni_fornecedor",
            "nome_fornecedor",
            "tipo_pessoa",
            "porte",
        ]
        dim_fornecedor.to_sql(
            "dim_fornecedor", con=conn, if_exists="append", index=False
        )
        print(f"✔ dim_fornecedor: {len(dim_fornecedor)} linhas inseridas.")

        # -------------------------------------------------------------
        # 8. Mapear Surrogate Keys (sk_*) para a Fato
        # -------------------------------------------------------------
        print("\nMapeando chaves substitutas para a fato_item_contratado...")
        map_orgao = pd.read_sql("SELECT sk_orgao, cnpj_orgao FROM dim_orgao", con=conn)
        map_fornecedor = pd.read_sql(
            "SELECT sk_fornecedor, ni_fornecedor FROM dim_fornecedor", con=conn
        )
        map_modalidade = pd.read_sql(
            "SELECT sk_modalidade, modalidade_id FROM dim_modalidade", con=conn
        )
        map_localidade = pd.read_sql(
            "SELECT sk_localidade, uf_sigla FROM dim_localidade", con=conn
        )

        fato_carga = fato.merge(
            map_orgao, left_on="cnpj_orgao_limpo", right_on="cnpj_orgao", how="left"
        )
        fato_carga = fato_carga.merge(
            map_fornecedor,
            left_on="ni_fornecedor_limpo",
            right_on="ni_fornecedor",
            how="left",
        )
        fato_carga = fato_carga.merge(
            map_modalidade,
            left_on="modalidade_id_num",
            right_on="modalidade_id",
            how="left",
        )
        fato_carga = fato_carga.merge(
            map_localidade, left_on="uf_sigla_limpa", right_on="uf_sigla", how="left"
        )

        # Se houver alguma ausência, usa a contingência -1
        fato_carga["sk_orgao"] = fato_carga["sk_orgao"].fillna(-1).astype(int)
        fato_carga["sk_fornecedor"] = fato_carga["sk_fornecedor"].fillna(-1).astype(int)
        fato_carga["sk_modalidade"] = fato_carga["sk_modalidade"].fillna(-1).astype(int)
        fato_carga["sk_localidade"] = fato_carga["sk_localidade"].fillna(-1).astype(int)

        colunas_fato = {
            "numero_controle_pncp": "numero_controle_pncp",
            "numero_item": "numero_item",
            "sk_orgao": "sk_orgao",
            "sk_fornecedor": "sk_fornecedor",
            "sk_modalidade": "sk_modalidade",
            "sk_localidade": "sk_localidade",
            "data_publicacao_limpa": "data_publicacao",
            "data_homologacao": "data_homologacao",
            "descricao": "descricao_item",
            "perfil_gasto": "perfil_gasto",
            "quantidade_final": "quantidade",
            "vu_estimado": "valor_unitario_estimado",
            "vu_homologado": "valor_unitario_homologado",
            "vt_estimado": "valor_total_estimado",
            "vt_homologado": "valor_total_homologado",
            "comparavel": "comparavel",
            "economia_valor": "economia_valor",
            "dias_ciclo": "dias_ciclo",
        }

        df_fato_final = fato_carga[list(colunas_fato.keys())].rename(
            columns=colunas_fato
        )

        # -------------------------------------------------------------
        # 9. Carga em lote da Fato (chunksize de 1000)
        # -------------------------------------------------------------
        print("Carregando fato_item_contratado em lote...")
        df_fato_final.to_sql(
            "fato_item_contratado",
            con=conn,
            if_exists="append",
            index=False,
            chunksize=1000,
        )
        print(
            f"✔ fato_item_contratado: {len(df_fato_final)} linhas inseridas com sucesso!"
        )

    print("\n" + "=" * 50)
    print("CARGA CONCLUÍDA COM SUCESSO NO MYSQL!")
    print("=" * 50)


if __name__ == "__main__":
    carregar_dados()
