# AI-Based Multi-Agent System for Drug Repurposing

This mini project implements a small multi-agent pipeline to demonstrate literature retrieval, NLP-based entity extraction, knowledge graph construction, simple prediction, and a frontend visualization.

Features:
- Search input for disease name
- Display extracted entities per paper
- Visualize knowledge graph
- Show drug repurposing suggestions with confidence and evidence (paper ids)

Tech stack:
- Backend: FastAPI (Python)
- NLP: spaCy
- Graph: NetworkX
- Frontend: HTML/CSS/JS + vis-network

Run locally (Windows / VS Code):

1. Create a virtual environment and activate it

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

3. Start the app

```powershell
uvicorn backend.app:app --reload
```

4. Open http://127.0.0.1:8000 in your browser

## Deploy frontend and backend

Netlify only serves the static frontend; it does not run this FastAPI backend. Deploy the backend to Render and the frontend to Netlify:

1. In Render, create a Blueprint from this repository. `render.yaml` creates the `drug-repurposing-api` web service, installs the Python dependencies, generates a JWT secret, and configures `/health` as its health check.
2. In Netlify, import this repository. `netlify.toml` publishes `frontend/` and proxies `/api/*` requests to `https://drug-repurposing-api.onrender.com`.
3. If Render assigns a different service URL, update the API proxy target in `netlify.toml` and redeploy Netlify.
4. Open the Netlify site and use Register to create an account. No default administrator password is configured. Without SMTP settings, new accounts are automatically verified for this demo.

The Render free service may take a short time to wake up after inactivity. The JSON user store is intended for demonstration; use a persistent database before relying on account data in production.

Notes:
- This project uses a small mock dataset in `data/sample_papers.json`. You can replace retrieval logic in `backend/agents/retrieval_agent.py` to call PubMed or other APIs.
- The NLP agent uses spaCy's small English model for demonstration. For better biomedical extraction, swap to SciSpacy models.
- Set `SECRET_KEY` through the deployment platform's environment settings. Never commit `.env` or `data/users.json`.
