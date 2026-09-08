"""Endpoints REST para o recurso Estação (dispositivo IoT)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db

router = APIRouter(prefix="/estacoes", tags=["Estações"])


@router.post(
    "",
    response_model=schemas.EstacaoOut,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar uma nova estação meteorológica",
)
def criar_estacao(dados: schemas.EstacaoCreate, db: Session = Depends(get_db)):
    return crud.criar_estacao(db, dados)


@router.get(
    "",
    response_model=List[schemas.EstacaoOut],
    summary="Listar estações (com filtros opcionais)",
)
def listar_estacoes(
    cidade: Optional[str] = Query(None, description="Filtra por cidade (parcial)"),
    status_filtro: Optional[models.StatusEstacao] = Query(
        None, alias="status", description="Filtra por status da estação"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud.listar_estacoes(db, cidade=cidade, status=status_filtro, skip=skip, limit=limit)


@router.get(
    "/{estacao_id}",
    response_model=schemas.EstacaoOut,
    summary="Buscar uma estação pelo ID",
)
def buscar_estacao(estacao_id: int, db: Session = Depends(get_db)):
    try:
        return crud.buscar_estacao(db, estacao_id)
    except crud.NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/{estacao_id}/estatisticas",
    response_model=schemas.EstacaoComEstatisticas,
    summary="Estatísticas agregadas das leituras de uma estação",
)
def estatisticas_estacao(estacao_id: int, db: Session = Depends(get_db)):
    try:
        dados = crud.estatisticas_estacao(db, estacao_id)
    except crud.NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    estacao = dados.pop("estacao")
    return schemas.EstacaoComEstatisticas(
        **schemas.EstacaoOut.model_validate(estacao).model_dump(),
        **dados,
    )


@router.put(
    "/{estacao_id}",
    response_model=schemas.EstacaoOut,
    summary="Atualizar dados de uma estação",
)
def atualizar_estacao(
    estacao_id: int, dados: schemas.EstacaoUpdate, db: Session = Depends(get_db)
):
    try:
        return crud.atualizar_estacao(db, estacao_id, dados)
    except crud.NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{estacao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover uma estação (e suas leituras)",
)
def remover_estacao(estacao_id: int, db: Session = Depends(get_db)):
    try:
        crud.remover_estacao(db, estacao_id)
    except crud.NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
