# Unicorn AI — Backend

Lightweight backend for the Rentout hackathon project. Provides file-backed listings, simple cross-platform integration stubs, n8n hooks, and a set of autonomous agent MVPs (calendar, pricing, guest-comm, ops, review).

This README covers: quick setup, environment variables, local run, agents, and Cloud Run deployment notes.

## Quickstart

1. Copy or create a `.env` file in `backend/` (see `backend/.env.example` for variables).
2. Install dependencies and run locally (recommended in a virtualenv):

```bash
cd backend
python -m pip install -r requirements.txt
# run dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

3. API base: `http://127.0.0.1:8000` — health: `GET /health`.

## Important files

- `backend/app/services/listing_service.py` — file-backed CRUD for `backend/data/listings.json`.
- `backend/app/services/integrations_service.py` — mocked adapters for Airbnb/Booking/Vrbo.
- `backend/app/services/n8n_service.py` — helpers to send webhooks and call n8n API.
- `backend/app/services/agents/` — autonomous agent MVPs.
- `backend/app/api/v1/listing.py` — REST endpoints for listings and pricing.
- `backend/Dockerfile` and `backend/start.sh` — container entry used for Cloud Run.

## Environment variables

Put these in `backend/.env` or set in Cloud Run service:

- `LLM_PROVIDER` (optional)
- `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `HUGGINGFACE_API_KEY`
- `N8N_WEBHOOK_URL` (default `http://n8n:5678/webhook`)
- `N8N_API_URL`, `N8N_API_KEY`

See `backend/.env.example` for more variables.

## Running the container locally

```bash
cd backend
docker build -t rentout:local .
docker run --rm -e PORT=8080 -p 8080:8080 rentout:local
curl http://localhost:8080/health
```

## Agents (MVP)

Each agent lives under `backend/app/services/agents/` and exposes async functions:

- Pricing Agent: rule-based competitor pricing and suggestion persisted to `listings.json`.
- Calendar Agent: checks remote availability and updates listings.
- Guest Communication Agent: generates replies using LLM and escalates via n8n.
- Ops Agent: schedules cleaning via n8n webhook.
- Review Agent: crafts review requests via LLM and sends via n8n.

## Deploy to Cloud Run

Build and deploy with Cloud Build / Cloud Run:

```bash
cd backend
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rentout:latest
gcloud run deploy rentout --image gcr.io/YOUR_PROJECT_ID/rentout:latest --region YOUR_REGION --platform managed --allow-unauthenticated
```

Notes:
- Ensure your Cloud Build trigger builds the `backend/Dockerfile` or uses a `cloudbuild.yaml` that references it.
- Cloud Run sets a `PORT` env var; the container honors `${PORT:-8080}`.

## Next steps

- Implement real platform adapters (OAuth, proper endpoints).
- Add Celery workers and persistent queue for agents.
- Persist remote IDs and audit logs to a database.

## Contributing

Keep secrets out of commits — use `.env` and `.gitignore`.

---
If you want, I can add agent trigger endpoints or scaffold Celery tasks next.
