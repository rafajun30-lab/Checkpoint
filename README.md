# Sistema IoT Meteorológico — CP1

API RESTful para **coleta e persistência de dados de sensores de clima**
(temperatura, umidade, pressão atmosférica e vento), com cadastro de
estações meteorológicas IoT e detecção automática de leituras em condição
de alerta.

**Tema escolhido:** 10 — Sistema IoT Meteorológica (Coleta e persistência de
dados de sensores de clima).

## Integrantes do grupo

- Guilherme Orugian — RM 572882
- Lucas Henrique — RM 571901
- Rafael Jun Aita Hirata — RM 569708

## Metodologia ágil

O desenvolvimento seguiu **Scrum/Kanban simplificado**, organizado em um
quadro no **Trello/Notion** (link abaixo), com as tarefas divididas em:

`Backlog → A Fazer → Em Progresso → Em Revisão → Concluído`

O trabalho foi dividido em uma única Sprint (referente à CP3), com reuniões
rápidas (daily) entre os integrantes para alinhar o progresso da modelagem
do banco, das regras de negócio e dos endpoints.

**Link do quadro (Trello/Notion):** https://trello.com/invite/b/6a9f7fbf3f79e95e7bbf0354/ATTI6707631dd6b4d5a7eca9ff352735c17aEA56E903/challenge-sprint

## Arquitetura do projeto

```
iot-meteorologica/
├── app/
│   ├── main.py          # Instância FastAPI, middlewares e rotas raiz
│   ├── database.py       # Configuração da conexão com o banco (SQLAlchemy)
│   ├── models.py         # Modelos ORM (tabelas: Estacao, Leitura)
│   ├── schemas.py        # Schemas Pydantic (validação/serialização)
│   ├── crud.py            # Regras de negócio e acesso a dados
│   └── routers/
│       ├── estacoes.py    # Endpoints REST de Estações
│       └── leituras.py    # Endpoints REST de Leituras
├── scripts/
│   └── seed.py            # Popula o banco com dados de exemplo
├── requirements.txt
└── README.md
```

## Modelagem do banco de dados

**Estacao** (estação meteorológica IoT)
| Campo       | Tipo      | Descrição                                |
|-------------|-----------|-------------------------------------------|
| id          | int (PK)  | Identificador                              |
| nome        | string    | Nome/identificação da estação              |
| cidade      | string    | Cidade onde está instalada                 |
| latitude    | float     | Latitude da localização                    |
| longitude   | float     | Longitude da localização                   |
| status      | enum      | ATIVA / INATIVA / MANUTENCAO               |
| criada_em   | datetime  | Data de cadastro                           |

**Leitura** (medição enviada por uma estação) — relação **1:N** com Estacao
| Campo                  | Tipo      | Descrição                              |
|------------------------|-----------|------------------------------------------|
| id                      | int (PK)  | Identificador                            |
| estacao_id              | int (FK)  | Estação que originou a leitura           |
| temperatura_c           | float     | Temperatura em °C                        |
| umidade_pct             | float     | Umidade relativa (%)                     |
| pressao_hpa             | float     | Pressão atmosférica (hPa)                |
| velocidade_vento_kmh    | float     | Velocidade do vento (km/h)               |
| direcao_vento_graus     | float     | Direção do vento (0–360°)                |
| alerta                  | bool      | Calculado automaticamente (regra abaixo) |
| registrada_em           | datetime  | Data/hora da leitura                     |

## Regras de negócio implementadas

1. **Detecção automática de alerta**: toda leitura registrada é avaliada
   automaticamente; é marcada como `alerta = true` quando a temperatura é
   ≤ 0 °C, ≥ 40 °C, ou o vento é ≥ 80 km/h.
2. **Estação inativa não recebe leituras**: uma estação com status
   `INATIVA` ou `MANUTENCAO` não pode registrar novas leituras
   (retorna `400 Bad Request`).
3. **Integridade referencial**: leituras só podem ser criadas para
   estações existentes (retorna `404 Not Found` caso contrário); ao
   remover uma estação, suas leituras são removidas em cascata.
4. **Estatísticas agregadas** por estação: total de leituras, temperatura
   média, mínima e máxima.
5. **Filtros de consulta**: leituras podem ser filtradas por estação,
   apenas alertas, e por janela de tempo (últimas N horas).

## Endpoints principais

| Método | Rota                                   | Descrição                                   |
|--------|-----------------------------------------|-----------------------------------------------|
| POST   | `/estacoes`                              | Cadastrar estação                             |
| GET    | `/estacoes`                              | Listar estações (filtros: `cidade`, `status`) |
| GET    | `/estacoes/{id}`                         | Buscar estação por ID                         |
| PUT    | `/estacoes/{id}`                         | Atualizar estação                             |
| DELETE | `/estacoes/{id}`                         | Remover estação                               |
| GET    | `/estacoes/{id}/estatisticas`            | Estatísticas de temperatura da estação        |
| POST   | `/estacoes/{id}/leituras`                | Registrar leitura de sensor                   |
| GET    | `/estacoes/{id}/leituras`                | Listar leituras de uma estação                |
| GET    | `/estacoes/{id}/leituras/ultima`         | Última leitura da estação                     |
| GET    | `/leituras`                              | Listar todas as leituras (filtros)            |
| GET    | `/leituras/{id}`                         | Buscar leitura por ID                         |
| DELETE | `/leituras/{id}`                         | Remover leitura                               |

Todas as respostas seguem os códigos HTTP apropriados: `200`, `201`,
`400`, `404` e `500` (tratado globalmente em `main.py`).

## Como executar

O projeto usa **PostgreSQL**. A forma mais rápida de ter um banco local é
via Docker (não precisa instalar Postgres na máquina); mas também funciona
com uma instalação local do Postgres.

```bash
# 1. Subir o PostgreSQL (usando o docker-compose fornecido)
docker compose up -d

# 2. Criar e ativar um ambiente virtual (opcional, mas recomendado)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. (Opcional) copiar o .env.example para .env e ajustar credenciais
cp .env.example .env

# 5. (Opcional) Popular o banco com dados de exemplo
python -m scripts.seed

# 6. Rodar a aplicação
uvicorn app.main:app --reload
```

A API sobe por padrão em `http://127.0.0.1:8000`.

- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

### Sem Docker

Se preferir usar uma instalação local do PostgreSQL, crie o banco manualmente:

```sql
CREATE DATABASE meteo_db;
```

E defina as credenciais via variáveis de ambiente (ou um arquivo `.env`,
baseado em `.env.example`):

```bash
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=meteo_db
```

Ou, alternativamente, definir a URL completa de uma vez:

```bash
export DATABASE_URL="postgresql+psycopg2://usuario:senha@localhost:5432/meteo_db"
```

As tabelas são criadas automaticamente na primeira execução da aplicação
(via `Base.metadata.create_all`, em `app/main.py`).

## Exemplo rápido de uso (curl)

```bash
# Cadastrar uma estação
curl -X POST http://127.0.0.1:8000/estacoes \
  -H "Content-Type: application/json" \
  -d '{"nome":"Estação Butantã","cidade":"São Paulo","latitude":-23.57,"longitude":-46.70}'

# Registrar uma leitura (estacao_id = 1)
curl -X POST http://127.0.0.1:8000/estacoes/1/leituras \
  -H "Content-Type: application/json" \
  -d '{"temperatura_c":27.5,"umidade_pct":60,"pressao_hpa":1012,"velocidade_vento_kmh":10}'
```

## Tecnologias utilizadas

- **Python 3.12**
- **FastAPI** — framework web e geração automática de documentação OpenAPI
- **SQLAlchemy** — ORM para persistência dos dados
- **Pydantic** — validação de schemas de entrada/saída
- **PostgreSQL** — banco de dados relacional (via `psycopg2`)
- **Docker Compose** — sobe um Postgres local para desenvolvimento
- **Uvicorn** — servidor ASGI
