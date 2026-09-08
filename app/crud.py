"""
Camada de regras de negócio e acesso a dados.

Mantém a lógica separada dos endpoints (routers), facilitando testes e
manutenção — cada função aqui recebe uma sessão de banco (Session) e
retorna objetos ORM ou levanta exceções de negócio.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas

# ---------------------------------------------------------------------------
# Regras de negócio (limites que caracterizam uma leitura como "alerta")
# ---------------------------------------------------------------------------
TEMPERATURA_ALERTA_MIN = 0.0      # abaixo disso: risco de geada
TEMPERATURA_ALERTA_MAX = 40.0     # acima disso: onda de calor
VENTO_ALERTA_KMH = 80.0           # ventos fortes / possível tempestade


class NotFoundError(Exception):
    """Levantada quando um recurso não é encontrado."""


class BusinessRuleError(Exception):
    """Levantada quando uma regra de negócio é violada."""


# ---------------------------------------------------------------------------
# Estações
# ---------------------------------------------------------------------------

def criar_estacao(db: Session, dados: schemas.EstacaoCreate) -> models.Estacao:
    estacao = models.Estacao(**dados.model_dump())
    db.add(estacao)
    db.commit()
    db.refresh(estacao)
    return estacao


def listar_estacoes(
    db: Session,
    cidade: Optional[str] = None,
    status: Optional[models.StatusEstacao] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Estacao]:
    query = db.query(models.Estacao)
    if cidade:
        query = query.filter(models.Estacao.cidade.ilike(f"%{cidade}%"))
    if status:
        query = query.filter(models.Estacao.status == status)
    return query.offset(skip).limit(limit).all()


def buscar_estacao(db: Session, estacao_id: int) -> models.Estacao:
    estacao = db.query(models.Estacao).filter(models.Estacao.id == estacao_id).first()
    if not estacao:
        raise NotFoundError(f"Estação {estacao_id} não encontrada.")
    return estacao


def atualizar_estacao(
    db: Session, estacao_id: int, dados: schemas.EstacaoUpdate
) -> models.Estacao:
    estacao = buscar_estacao(db, estacao_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(estacao, campo, valor)
    db.commit()
    db.refresh(estacao)
    return estacao


def remover_estacao(db: Session, estacao_id: int) -> None:
    estacao = buscar_estacao(db, estacao_id)
    db.delete(estacao)
    db.commit()


def estatisticas_estacao(db: Session, estacao_id: int) -> dict:
    estacao = buscar_estacao(db, estacao_id)
    agregados = (
        db.query(
            func.count(models.Leitura.id),
            func.avg(models.Leitura.temperatura_c),
            func.min(models.Leitura.temperatura_c),
            func.max(models.Leitura.temperatura_c),
        )
        .filter(models.Leitura.estacao_id == estacao_id)
        .first()
    )
    total, media, minimo, maximo = agregados
    return {
        "estacao": estacao,
        "total_leituras": total or 0,
        "temperatura_media_c": round(media, 2) if media is not None else None,
        "temperatura_min_c": minimo,
        "temperatura_max_c": maximo,
    }


# ---------------------------------------------------------------------------
# Leituras
# ---------------------------------------------------------------------------

def _calcular_alerta(dados: schemas.LeituraCreate) -> bool:
    """Regra de negócio: marca a leitura como alerta se algum valor
    estiver fora da faixa considerada segura."""
    return (
        dados.temperatura_c <= TEMPERATURA_ALERTA_MIN
        or dados.temperatura_c >= TEMPERATURA_ALERTA_MAX
        or dados.velocidade_vento_kmh >= VENTO_ALERTA_KMH
    )


def registrar_leitura(
    db: Session, estacao_id: int, dados: schemas.LeituraCreate
) -> models.Leitura:
    estacao = buscar_estacao(db, estacao_id)  # 404 se não existir

    if estacao.status != models.StatusEstacao.ATIVA:
        raise BusinessRuleError(
            f"Estação {estacao_id} está com status '{estacao.status.value}' "
            "e não pode registrar novas leituras."
        )

    leitura = models.Leitura(
        estacao_id=estacao_id,
        alerta=_calcular_alerta(dados),
        **dados.model_dump(),
    )
    db.add(leitura)
    db.commit()
    db.refresh(leitura)
    return leitura


def listar_leituras(
    db: Session,
    estacao_id: Optional[int] = None,
    somente_alertas: bool = False,
    horas: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[models.Leitura]:
    query = db.query(models.Leitura)
    if estacao_id is not None:
        query = query.filter(models.Leitura.estacao_id == estacao_id)
    if somente_alertas:
        query = query.filter(models.Leitura.alerta.is_(True))
    if horas is not None:
        limite = datetime.utcnow() - timedelta(hours=horas)
        query = query.filter(models.Leitura.registrada_em >= limite)
    return (
        query.order_by(models.Leitura.registrada_em.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def buscar_leitura(db: Session, leitura_id: int) -> models.Leitura:
    leitura = db.query(models.Leitura).filter(models.Leitura.id == leitura_id).first()
    if not leitura:
        raise NotFoundError(f"Leitura {leitura_id} não encontrada.")
    return leitura


def remover_leitura(db: Session, leitura_id: int) -> None:
    leitura = buscar_leitura(db, leitura_id)
    db.delete(leitura)
    db.commit()


def ultima_leitura_por_estacao(db: Session, estacao_id: int) -> models.Leitura:
    buscar_estacao(db, estacao_id)  # garante 404 se a estação não existir
    leitura = (
        db.query(models.Leitura)
        .filter(models.Leitura.estacao_id == estacao_id)
        .order_by(models.Leitura.registrada_em.desc())
        .first()
    )
    if not leitura:
        raise NotFoundError(
            f"Estação {estacao_id} ainda não possui nenhuma leitura registrada."
        )
    return leitura
