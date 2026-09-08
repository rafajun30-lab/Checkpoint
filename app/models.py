"""
Modelos ORM (SQLAlchemy) que representam as tabelas do banco de dados.

Entidades:
- Estacao: representa um dispositivo/estação meteorológica IoT instalado
  em algum local, responsável por coletar dados de clima.
- Leitura: representa uma medição pontual enviada por uma Estação
  (temperatura, umidade, pressão, vento etc.).
"""

import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Enum as SqlEnum,
)
from sqlalchemy.orm import relationship

from app.database import Base


class StatusEstacao(str, enum.Enum):
    ATIVA = "ATIVA"
    INATIVA = "INATIVA"
    MANUTENCAO = "MANUTENCAO"


class Estacao(Base):
    __tablename__ = "estacoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cidade = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(SqlEnum(StatusEstacao), default=StatusEstacao.ATIVA, nullable=False)
    criada_em = Column(DateTime, default=datetime.utcnow)

    leituras = relationship(
        "Leitura", back_populates="estacao", cascade="all, delete-orphan"
    )


class Leitura(Base):
    __tablename__ = "leituras"

    id = Column(Integer, primary_key=True, index=True)
    estacao_id = Column(Integer, ForeignKey("estacoes.id"), nullable=False)

    temperatura_c = Column(Float, nullable=False)  # graus Celsius
    umidade_pct = Column(Float, nullable=False)  # % (0 a 100)
    pressao_hpa = Column(Float, nullable=False)  # hectopascal
    velocidade_vento_kmh = Column(Float, default=0.0)
    direcao_vento_graus = Column(Float, nullable=True)  # 0 a 360

    alerta = Column(Boolean, default=False)  # calculado automaticamente
    registrada_em = Column(DateTime, default=datetime.utcnow)

    estacao = relationship("Estacao", back_populates="leituras")
