# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WebMedic is a voice-driven outpatient EMR generation demo system. It combines ASR, AI-powered structured extraction, vector similarity search, and clinical decision support to assist doctors in creating medical records from voice conversations.

**⚠️ Technical demo only — not for clinical use. LLM outputs cannot be used as final medical conclusions.**

Fixed demo settings: Doctor "Panython", Patient "张三" (Male, 29), medical records at `D:\webmedic\backend\medical_records\`.

## Technology Stack

- **Backend**: FastAPI (Python 3.11.5) + SQLAlchemy (sync) + MySQL 8.0+
- **Frontend**: Vue 3 + Vite + Pinia + Element Plus + Axios
- **AI/ML**:
  - ASR: Dolphin/FunASR (local) or OpenAI Whisper
  - LLM: DeepSeek API + Instructor (structured extraction) or LangExtract
  - Embeddings: BGE-M3 (`BAAI/bge-m3`, 1024-dim vectors)
  - Vector DB: Qdrant (embedded mode by default)

## Development Commands

### Backend
```bash
cd D:\webmedic\backend
venv\Scripts\activate
pip install -r requirements.txt
python run.py                  # Starts on port 8001
# Docs: http://localhost:8001/docs
```

### Frontend
```bash
cd D:\webmedic\frontend
npm install
npm run dev                    # Starts on port 5173
npm run build
```

### Dolphin ASR (local speech recognition)
```bash
cd D:\webmedic\backend
start_dolphin.bat              # Starts on port 8888
# First run downloads ~1.5GB model
# Requires ffmpeg in PATH for WebM→WAV conversion
```

## Architecture

### Core Workflow
Session → ASR Transcription → Structured Extraction → Vector Search (similar cases) → EMR Draft → Clinical Hints

### Backend Service Layer

All business logic lives in `backend/app/services/`. Endpoints in `app/api/endpoints/` are thin wrappers.

**Key services:**
- `asr_service.py` — Whisper/Dolphin/Mock ASR dispatch
- `extract_service.py` — Structured extraction, delegates to extractor plugins
- `index_service.py` — PDF ingestion, embedding, Qdrant upsert
- `embedding_service.py` — BGE-M3 embedding (lazy-loaded singleton, CPU by default)
- `vocabulary_service.py` — Medical vocabulary (ICD codes, surgery codes, symptoms)
- `llm_service.py` — DeepSeek API client with Instructor, retry logic
- `draft_service.py` / `clinical_hint_service.py` / `session_service.py` — workflow steps

**Extractor plugin system** (`app/services/extractors/`):
- `base.py` — `BaseExtractor` interface
- `instructor_extractor.py` — DeepSeek + Instructor (default, `EXTRACTOR_TYPE=instructor`)
- `langextract_extractor.py` — LangExtract library wrapper (`EXTRACTOR_TYPE=langextract`)
- `factory.py` — instantiates the correct extractor from config

**Vector DB abstraction** (`app/services/vector/`):
- `base.py` — `BaseVectorDB` interface with `VectorSearchResult`
- `qdrant_impl.py` — Qdrant client (embedded or server mode)
- `factory.py` — builds from `VECTOR_DB_TYPE` config

### New Models (beyond original schema)
- `medical_vocabulary.py` — symptom/body-part/disease terms
- `icd_code.py` / `surgery_code.py` — code lookup tables
- `doctor.py` / `patient.py` — entity records

### New API Endpoints
- `/api/v1/vocabulary` — medical vocabulary CRUD
- `/api/v1/master-data` — ICD/surgery code lookup
- `/api/v1/system` — system info/status

### Configuration (`app/core/config.py`)

Key env vars beyond database/ASR:

| Variable | Default | Purpose |
|---|---|---|
| `VECTOR_DB_TYPE` | `qdrant` | Vector DB backend |
| `QDRANT_MODE` | `embedded` | `embedded` or `server` |
| `QDRANT_PATH` | `./qdrant_storage` | Embedded storage path |
| `QDRANT_COLLECTION` | `medical_cases` | Collection name |
| `QDRANT_VECTOR_SIZE` | `1024` | Must match BGE-M3 output |
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | HuggingFace model or local path |
| `EMBEDDING_MODEL_PATH` | `""` | Local path overrides `EMBEDDING_MODEL` |
| `EMBEDDING_DEVICE` | `cpu` | `cpu` or `cuda` |
| `EXTRACTOR_TYPE` | `instructor` | `instructor` or `langextract` |
| `LLM_USE_MOCK` | `true` | Skip real LLM calls |
| `ASR_USE_MOCK` | `false` | Skip real ASR calls |

### API Contract

All responses use:
```json
{"success": true, "message": "...", "data": {}}
```
All routes use `/api/v1` prefix. Frontend Vite dev proxy forwards `/api` → `http://localhost:8001`.

### Prompts

All AI prompts must be `.txt` files in `backend/app/prompts/`:
- `extract_structured_record.txt`
- `generate_emr_draft.txt`
- `generate_clinical_hints.txt`

### Audio Recording

Frontend `useRecorder.js` tries WebM (MediaRecorder, ~50KB/10s) first, falls back to WAV (Web Audio API, ~250KB/10s). Backend converts WebM→WAV via ffmpeg when needed.

## Development Guidelines

- All APIs must use `/api/v1` prefix with unified `{success, message, data}` response
- New AI prompts must be `.txt` files in `backend/app/prompts/`, never inline strings
- Use Composition API with `<script setup>` in Vue components; Pinia for shared state
- SQLAlchemy ORM is **synchronous** (not async) — use `db: Session` in endpoints
- Do not modify table names, endpoint paths, or directory structure without updating this file

## Port Configuration

| Service | Port |
|---|---|
| Backend API | 8001 |
| Frontend Dev | 5173 |
| Dolphin ASR | 8888 |
| MySQL | 3306 |

## Known Issues and Solutions

### PyTorch DLL Loading Failure (Windows)
PyTorch 2.10.0+cpu fails to load `c10.dll`. Fix: downgrade to 2.5.1.
```bash
pip install --upgrade --force-reinstall torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu
```

### Dolphin ASR Setup
`funasr-server` command doesn't exist — use the custom `dolphin_server.py` Flask server instead. Uses FunASR `AutoModel` to load Paraformer. Requires ffmpeg for WebM conversion.

### .env File Encoding
Chinese comments on config lines cause latin-1 HTTP header errors. Keep config values comment-free, especially `DOLPHIN_API_KEY`.

### BGE-M3 Embedding Model
- Default: downloads from HuggingFace on first use
- Local path: set `EMBEDDING_MODEL_PATH` to skip download
- CPU-only: `use_fp16=False` is set automatically when `EMBEDDING_DEVICE=cpu`

## Testing

Mock modes bypass all external dependencies:
```env
LLM_USE_MOCK=true
ASR_USE_MOCK=true
```

Manual integration test scripts are in `backend/scripts/` (e.g., `test_vector_db.py`, `test_local_model.py`).

## Database

MySQL 8.0+, database name `webmedic_demo`. No migration framework — schema is defined by SQLAlchemy models and created via `Base.metadata.create_all()`. Two separate venvs: `backend/venv/` (main) and `backend/dolphin_env/` (FunASR/Dolphin only).
