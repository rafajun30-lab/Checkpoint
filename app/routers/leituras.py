"""Endpoints REST para o recurso Leitura (medições enviadas pelos sensores)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(tags=["Leituras"])


@router.post(
    "/estacoes/{estacao_id}/leituras",
    response_model=schemas.LeituraOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar uma nova leitura de sensor para uma estação",
)
def registrar_leitura(
    estacao_id: int, dados: schemas.LeituraCreate, db: Session = Depends(get_db)
):
    try:
        return crud.registrar_leitura(db, estacao_id, dados)
    except crud.NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except crud.BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/estacoes/{estacao_id}/leituras",
    response_model=List[schemas.LeituraOut],
    summary="Listar leituras de uma estação específica",
)
def listar_leituras_da_estacao(
    estacao_id: int,
    somente_alertas: bool = Query(False, description="Retorna apenas leituras em alerta"),
    horas: Optional[int] = Query(None, ge=1, description="Filtra pelas últimas N horas"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    try:
        crud.buscar_estacao(db, estacao_id)  # garante 404 se a estação não existir
    except crud.NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return crud.listar_leituras(
        db,
        estacao_id=estacao_id,
        somente_alertas=somente_alertas,
        horas=horas,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/estacoes/{estacao_id}/leituras/ultima",
    response_model=schemas.LeituraOut,
    summary="Obter a leitura mais recente de uma estação",
)
def ultima_leitura(estacao_id: int, db: Session = Depends(get_db)):
    try:
        return crud.ultima_leitura_por_estacao(db, estacao_id)
    except crud.NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/leituras",
    response_model=List[schemas.LeituraOut],
    summary="Listar todas as leituras do sistema (com filtros opcionais)",
)
def listar_todas_as_leituras(
    somente_alertas: bool = Query(False),
    horas: Optional[int] = Query(None, ge=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud.listar_leituras(
        db, somente_alertas=somente_alertas, horas=horas, skip=skip, limit=limit
    )


@router.get(
    "/leituras/{leitura_id}",
    response_model=schemas.LeituraOut,
    summary="Buscar uma leitura pelo ID",
)
def buscar_leitura(leitura_id: int, db: Session = Depends(get_db)):
    try:
        return crud.buscar_leitura(db, leitura_id)
    except crud.NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/leituras/{leitura_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remover uma leitura",
)
def remover_leitura(leitura_id: int, db: Session = Depends(get_db)):
    try:
        crud.remover_leitura(db, leitura_id)
    except crud.NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
