# Synthetic Biology Promoter Designer

> **Domain:** Synthetic Biology & Genetic Circuit Design
> **Standards:** Synthetic Biology Open Language (SBOL 3.0)

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

**Synthetic Biology Promoter Designer** is a computational platform for designing synthetic genetic logic gates using position weight matrices (PWMs) and thermodynamic transcriptional models. It provides multi-agent evaluation of promoter designs with cryptographic audit trails.

---

## Key Capabilities

- **Thermodynamic Models**: Transcription factor binding affinity evaluation using PWM scoring
- **Multi-Agent Evaluation**: Specialized sub-agents for parameter verification, safety conformance, and protocol compliance
- **HMAC-SHA256 Audit Trail**: Cryptographically chained, tamper-evident logging for every evaluation
- **PHI Outbound Guard**: Active pattern detection blocking sensitive identifiers from outbound data
- **FastAPI REST API**: OpenAPI 3.1 endpoints for programmatic access
- **Prometheus Metrics**: Operational telemetry export

---

## Installation

```bash
pip install -e .
```

### Optional Dependencies
```bash
pip install fastapi uvicorn  # For REST API server
pip install pytest           # For running tests
```

---

## CLI Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Interactive Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Argument | Description | Default |
|:---------|:------------|:--------|
| `--task-id` | Unique task identifier | TASK-2026-001 |
| `--target` | Target key or identifier | KEY-TARGET-01 |
| `--primary` | Primary metric value (float) | 28.5 |
| `--secondary` | Secondary metric value (float) | 14.2 |
| `--critical` | Flag critical intervention | False |
| `--status` | Status descriptor | DISCORDANT |

---

## REST API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| POST | `/api/audit` | Submit task for evaluation |
| POST | `/api/chat` | Query supervisor |
| GET | `/api/audit/logs` | Get audit trail |

---

## Security

- **Audit Trail Key**: Set `AUDIT_SECRET_KEY` environment variable for persistent HMAC signing across restarts. Without it, an ephemeral runtime key is generated (with a warning).
- **PHI Guard**: Automatic detection and blocking of SSNs, MRNs, phone numbers, emails, and patient names in outbound data.

---

## Testing

```bash
pytest -v
```

---

## Container Deployment

```bash
docker build -t synthetic-biology-promoter-designer .
docker run -p 8000:8000 synthetic-biology-promoter-designer
```

---

## Project Structure

```
synthetic-biology-promoter-designer/
├── agents/                    # Enterprise multi-agent system
│   ├── api.py                 # FastAPI REST server
│   ├── base.py                # Security, PHI guard, audit trail
│   ├── models.py              # Pydantic schemas
│   ├── supervisor.py          # Orchestrator
│   └── workers.py             # Specialized evaluation agents
├── synbio_promoter/           # Core synthetic biology engine
│   ├── agents.py              # Sub-agent implementations
│   ├── engine.py              # Domain evaluation logic
│   ├── models.py              # Data models
│   ├── cli.py                 # CLI entry point
│   └── server.py              # FastAPI app factory
├── tests/                     # Test suite
├── cli.py                     # Main CLI entry point
├── enrichment.py              # Enrichment feature suite
├── simulator.py               # High-throughput simulation
└── pyproject.toml             # Project configuration
```
