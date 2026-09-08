"""
Script utilitário para popular o banco de dados com dados de exemplo,
útil para testar a API rapidamente após o clone do repositório.

Uso:
    python -m scripts.seed
"""

import random
from datetime import datetime, timedelta

from app.database import Base, engine, SessionLocal
from app import models

Base.metadata.create_all(bind=engine)

ESTACOES_EXEMPLO = [
    {"nome": "Estação Butantã", "cidade": "São Paulo", "latitude": -23.5711, "longitude": -46.7095},
    {"nome": "Estação Copacabana", "cidade": "Rio de Janeiro", "latitude": -22.9711, "longitude": -43.1825},
    {"nome": "Estação Batel", "cidade": "Curitiba", "latitude": -25.4372, "longitude": -49.2891},
]


def seed():
    db = SessionLocal()
    try:
        if db.query(models.Estacao).count() > 0:
            print("Banco já possui dados. Nada a fazer.")
            return

        estacoes = []
        for dados in ESTACOES_EXEMPLO:
            estacao = models.Estacao(**dados, status=models.StatusEstacao.ATIVA)
            db.add(estacao)
            estacoes.append(estacao)
        db.commit()

        agora = datetime.utcnow()
        for estacao in estacoes:
            db.refresh(estacao)
            for i in range(10):
                temperatura = round(random.uniform(10, 38), 1)
                leitura = models.Leitura(
                    estacao_id=estacao.id,
                    temperatura_c=temperatura,
                    umidade_pct=round(random.uniform(30, 95), 1),
                    pressao_hpa=round(random.uniform(1000, 1025), 1),
                    velocidade_vento_kmh=round(random.uniform(0, 40), 1),
                    direcao_vento_graus=round(random.uniform(0, 360), 1),
                    alerta=temperatura <= 0 or temperatura >= 40,
                    registrada_em=agora - timedelta(hours=i),
                )
                db.add(leitura)
        db.commit()
        print(f"Seed concluído: {len(estacoes)} estações e leituras de exemplo criadas.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
