"""
Schemas Pydantic usados para validar requisições (entrada) e formatar
respostas (saída) da API. Também são usados pelo FastAPI para gerar
automaticamente a documentação Swagger/OpenAPI.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict

from app.models import StatusEstacao


# ---------------------------------------------------------------------------
# Estação
# ---------------------------------------------------------------------------

class EstacaoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, examples=["Estação Butantã"])
    cidade: str = Field(..., min_length=2, max_length=100, examples=["São Paulo"])
    latitude: float = Field(..., ge=-90, le=90, examples=[-23.5505])
    longitude: float = Field(..., ge=-180, le=180, examples=[-46.6333])


class EstacaoCreate(EstacaoBase):
    status: StatusEstacao = StatusEstacao.ATIVA


class EstacaoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    cidade: Optional[str] = Field(None, min_length=2, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    status: Optional[StatusEstacao] = None


class EstacaoOut(EstacaoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: StatusEstacao
    criada_em: datetime


class EstacaoComEstatisticas(EstacaoOut):
    total_leituras: int
    temperatura_media_c: Optional[float] = None
    temperatura_min_c: Optional[float] = None
    temperatura_max_c: Optional[float] = None


# ---------------------------------------------------------------------------
# Leitura
# ---------------------------------------------------------------------------

class LeituraBase(BaseModel):
    temperatura_c: float = Field(..., ge=-90, le=60, examples=[24.5])
    umidade_pct: float = Field(..., ge=0, le=100, examples=[65.0])
    pressao_hpa: float = Field(..., ge=800, le=1100, examples=[1013.25])
    velocidade_vento_kmh: float = Field(0.0, ge=0, le=500, examples=[12.3])
    direcao_vento_graus: Optional[float] = Field(None, ge=0, le=360, examples=[180.0])


class LeituraCreate(LeituraBase):
    pass


class LeituraOut(LeituraBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    estacao_id: int
    alerta: bool
    registrada_em: datetime


class EstacaoComLeituras(EstacaoOut):
    leituras: List[LeituraOut] = []
