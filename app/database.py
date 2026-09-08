"""
Configuração da conexão com o banco de dados usando SQLAlchemy.

O projeto usa PostgreSQL como banco de dados relacional. A string de
conexão pode ser definida de duas formas:

1. Diretamente via variável de ambiente DATABASE_URL, por exemplo:
       DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/meteo_db

2. Ou através das variáveis individuais abaixo (usadas para montar a URL
   caso DATABASE_URL não seja definida), que já batem com o
   docker-compose.yml fornecido no projeto:
       POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB

Para rodar rapidamente com Docker: `docker compose up -d`
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "meteo_db")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}",
)

# connect_args só seria necessário para SQLite; mantido vazio para Postgres.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency do FastAPI: cria e fecha a sessão do banco a cada requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
