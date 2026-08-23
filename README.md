# Clarafin AI

Clarafin AI is a financial document intelligence tool for small and medium businesses.

Upload financial documents such as bank statements, profit and loss reports, invoices, balance sheets, and cash-flow reports. The system automatically analyzes the uploaded documents and provides:

- Current state analysis
- Missing-document gap detection
- Forward-looking financial flags
- Source citations for financial claims

> Clarafin provides analysis only. It does not provide tax, legal, or investment advice.

## Features

- User signup and login
- Upload PDF, CSV, XLSX, and XLS files
- Automatic analysis after document upload
- Current state, gaps, and forward flags in separate sections
- Source-aware citation viewer
- Demo financial dataset for testing
- Groq AI integration

## Project Structure

```text
backend/       FastAPI backend
frontend/      React + Vite frontend
mock_data/     Demo financial documents
tests/         Backend test script
