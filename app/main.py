"""
Ponto de entrada da aplicação FastAPI - Sistema IoT Meteorológico.

Execução local:
    uvicorn app.main:app --reload

Documentação interativa:
    http://127.0.0.1:8000/docs      (Swagger UI)
    http://127.0.0.1:8000/redoc     (ReDoc)
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import estacoes, leituras

# Cria as tabelas no banco de dados, caso ainda não existam.
# (Em um projeto de produção, isso seria feito via ferramenta de migração,
# como Alembic; aqui usamos create_all para simplificar a correção do CP3.)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema IoT Meteorológico",
    description=(
        "API RESTful para coleta e persistência de dados de sensores de "
        "clima (temperatura, umidade, pressão e vento), com cadastro de "
        "estações meteorológicas e detecção automática de leituras em "
        "condições de alerta."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def erro_inesperado_handler(request: Request, exc: Exception):
    """Garante que qualquer erro não tratado retorne 500 com JSON padronizado,
    em vez de derrubar a aplicação sem resposta clara para o cliente."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Erro interno inesperado: {str(exc)}"},
    )


app.include_router(estacoes.router)
app.include_router(leituras.router)


@app.get("/", tags=["Status"], summary="Health check da API")
def raiz():
    return {"status": "ok", "mensagem": "API do Sistema IoT Meteorológico no ar 🌦️"}
