# Evil Eye (EE)

A bilingual (English/Arabic) AI voice companion. React/Vite frontend, FastAPI backend.

## Stack

- **Chat**: Groq (`openai/gpt-oss-120b`), free tier, via its OpenAI-compatible endpoint.
- **Voice out**: English uses the browser's built-in Speech Synthesis (free, client-side). Arabic uses [edge-tts](https://github.com/rany2/edge-tts) on the backend (free, no API key, real male Egyptian-Arabic neural voice) since Windows/browsers typically only ship one, female, Arabic system voice.
- **Voice in**: local [faster-whisper](https://github.com/SYSTRAN/faster-whisper) on the backend, more accurate than the browser's built-in speech recognition, especially for Arabic.

## Local development

Backend:
```bash
cd server
python -m venv venv
./venv/Scripts/python.exe -m pip install -r requirements.txt
cp .env.example .env   # then fill in LLM_API_KEY
./venv/Scripts/python.exe -m uvicorn main:app --port 8000
```

Frontend:
```bash
cd client
npm install
npm run dev
```

## Deploying

**Frontend (Vercel):** import this repo, set the project's root directory to `client`, and add an environment variable `VITE_API_URL` pointing at the deployed backend's URL (see below). Vercel auto-detects the Vite build.

**Backend (Render):** import this repo as a new Web Service (or use the included `render.yaml` blueprint), with root directory `server`. Set these environment variables:

| Variable | Value |
|---|---|
| `LLM_API_KEY` | your Groq API key |
| `CORS_ORIGINS` | your deployed Vercel URL, e.g. `https://your-app.vercel.app` |
| `WHISPER_MODEL` | `base` (fits the free tier's memory; `small` is more accurate but needs more RAM) |

`CHAT_MODEL` and `LLM_BASE_URL` have working defaults and don't need to be set unless you want to change them.

Once the backend is deployed, copy its URL into the frontend's `VITE_API_URL` on Vercel and redeploy the frontend.
