# Clarafin

Clarafin is a financial-document workspace for SMEs. Upload PDF, CSV, XLSX, or XLS files, select the relevant documents, and run a source-aware analysis.

## Run locally

Open two PowerShell windows in this project folder.

**Backend (first window)**

```powershell
.\run_backend.bat
```

The API is available at `http://127.0.0.1:8001` and its interactive API page is at `http://127.0.0.1:8001/docs`.

**Frontend (second window)**

```powershell
cd frontend
npm run dev
```

Open `http://localhost:3000`.

## Test the product

1. Select **Try the demo account** (`demo@sme-agent.com` / `demo1234`).
2. Upload one or more files from `mock_data`.
3. Tick the uploaded documents and select **Analyze documents**.
4. Copy `.env.example` to `.env`, set `GROQ_API_KEY` to your Groq key, then restart the backend. You can also supply the key in the workspace; it is retained only for the current browser session.
5. Check the current-state cards, gaps, forward flags, and citation pop-ups.

## Verification commands

```powershell
cd frontend
npm run lint
npm run build
```

With the backend running, execute `python tests/test_backend.py` from the project root to exercise signup, login, upload, listing, and analysis polling.

## Notes

- AI output is analysis only; it is not tax, legal, or investment advice.
- Every financial claim should be checked against its cited source document.
- The backend uses Groq's `llama-3.3-70b-versatile` model by default. Set `GROQ_MODEL` to use another supported Groq model.
