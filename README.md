# Synthetic Biology Promoter Designer

A Python CLI/API project with a browser-based **generic threshold evaluation demo**. The repository name reflects its intended biological domain; its implemented rules are not yet a validated promoter-design model.

## What is implemented

- Three numerical/descriptor checks: primary metric >25, secondary metric >12 or critical flag, and a configurable set of anomaly words in status descriptors.
- Task-level alert classification and HMAC-SHA256-signed, hash-chained audit entries in the Python `agents/` workflow.
- CSV batch evaluation, REST endpoints, and a self-contained static demonstration in `web/`.
- A separate legacy `synbio_promoter/` evaluator with different thresholds (primary >25, secondary >10). It remains available for compatibility, but is not the default API.

**Limitations:** No PWM scanning, motif-based sequence generation, sequence-specific binding calculation, thermodynamic promoter prediction, SBOL conformance validator, or experimental calibration is implemented. Rule thresholds are illustrative. Do not interpret classifications as safety assessments or validated biological predictions.

## Browser demo

The `web/index.html` page operates completely in the browser without a backend. Open it locally or serve the `web/` directory with any static HTTP server. It computes illustrative threshold classifications and supports downloading the JSON result. No biological sequence is generated and no cryptographic signing occurs in the browser.

GitHub Pages deployment is defined in `.github/workflows/pages.yml`. The live link should be added only after the Pages workflow succeeds and the published site is verified. GitHub Pages must be configured to use **GitHub Actions** as the build source.

## Local installation

Python 3.10+:

```bash
python -m pip install -e ".[api,test]"
python -m pytest -q
```

Run the main CLI:

```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --status DISCORDANT
python cli.py batch -i sample.csv -o results.csv
python cli.py verify-audit
python cli.py serve --host 127.0.0.1 --port 8000
```

The installed console command (`synthetic-biology-promoter-designer`) starts the legacy `synbio_promoter/` CLI; use `python cli.py` for the main audited implementation.

## REST API

After starting the server, open `http://127.0.0.1:8000/docs`. Endpoints in the main API: `GET /health`, `GET /metrics`, `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`. The metrics endpoint provides JSON counters, not Prometheus exposition text.

```bash
curl -X POST http://127.0.0.1:8000/api/audit \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"T1","target_identifier":"KEY-01","primary_metric":10,"secondary_metric":3,"status_descriptor":"NOMINAL"}'
```

The browser demo does not call these endpoints. For development use `python -m http.server 8080 --directory web` then open `http://localhost:8080`.

## Security and privacy

The server-side audit trail signs chain links using HMAC-SHA256. Set `AUDIT_SECRET_KEY` to a private, cryptographically random secret before deployment; otherwise the application uses an ephemeral key, preventing verification after restart. The key is never needed in browser code. `docker compose up --build` requires this environment variable. See `.env.example` for setup.

The server rejects several patterns resembling sensitive patient identifiers before processing. This guard is heuristic and **not** a guarantee of de-identification, HIPAA compliance, or secure handling of protected health information. Do not submit real patient data to the demo. Static browser values stay in memory and are not transmitted or placed in persistent browser storage. The backend holds in-memory task dossiers and audit logs; restarting discards them.

## Test, deployment and compatibility

```bash
python -m pytest -q
node --test tests/web.test.cjs
docker build -t synthetic-biology-promoter-designer .
```

CI tests Python 3.10–3.12 and Node.js 22. The static demo uses standard browser APIs supported by current Chromium, Firefox and Safari; no external packages or fonts are required.

Technology: Python, Pydantic, FastAPI, Uvicorn, JavaScript, HTML/CSS, Docker, GitHub Actions. License: [MIT](LICENSE).
