"""
Módulo de conexão com o banco de dados MySQL via SQLAlchemy.
Lê as credenciais do ambiente (.env).
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "pncp_controladoria")


def get_engine_servidor():
    """
    Conecta diretamente ao servidor MySQL sem especificar o banco de dados.
    Necessário para criar o banco inicial (DDL).
    """
    url = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/?charset=utf8mb4"
    )
    return create_engine(url, echo=False)


def get_engine():
    """
    Conecta diretamente ao banco de dados pncp_controladoria.
    """
    url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    return create_engine(url, echo=False)


obter_engine = get_engine
criar_engine = get_engine
