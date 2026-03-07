# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WebMedic is a voice-driven outpatient electronic medical record (EMR) generation demo system. It combines speech recognition (ASR), AI-powered structured extraction, and clinical decision support to assist doctors in creating medical records from voice conversations.

**⚠️ Important: This is a technical demo only - not for clinical use. LLM outputs cannot be used as final medical conclusions.**

## Technology Stack

- **Backend**: FastAPI (Python 3.11.5) + SQLAlchemy + MySQL 8.0+
- **Frontend**: Vue 3 + Vite + Pinia + Element Plus + Axios
- **AI Components**:
  - ASR: Dolphin (local) or OpenAI Whisper
  - LLM: DeepSeek API with Instructor for structured extraction
  - Document Indexing: PageIndex for similar case retrieval

## Development Commands

### Backend

```bash
# Navigate to backend
cd D:\webmedic\backend

# Activate virtual environment (recommended)
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your database password and API keys

# Start backend server (runs on port 8001)
python run.py

# API documentation available at:
# http://localhost:8001/docs
# http://localhost:8001/health
```

### Frontend

```bash
# Navigate to frontend
cd D:\webmedic\frontend

# Install dependencies
npm install

# Start development server (runs on port 5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Dolphin ASR (Local Speech Recognition)

```bash
# Navigate to backend
cd D:\webmedic\backend

# Start Dolphin ASR service (runs on port 8888)
start_dolphin.bat
```

**Note**:
- First-time startup downloads ~1.5GB model (5-15 minutes depending on network)
- **ffmpeg required**: Dolphin needs ffmpeg to process WebM audio from browsers
  - Download from: https://www.gyan.dev/ffmpeg/builds/
  - Add to system PATH: C:\ffmpeg\bin
  - Verify with: `ffmpeg -version`

## Architecture

### Backend Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/      # API route handlers
│   │   │   ├── asr.py           # Speech recognition endpoints
│   │   │   ├── sessions.py      # Session management
│   │   │   ├── extract.py       # Structured extraction
│   │   │   ├── documents.py     # Document management
│   │   │   ├── index.py         # Document indexing
│   │   │   ├── draft.py         # Draft generation
│   │   │   └── clinical_hints.py # Clinical hints
│   │   └── router.py       # Main API router
│   ├── core/
│   │   └── config.py       # Settings management (pydantic-settings)
│   ├── db/
│   │   ├── base.py         # Database base classes
│   │   └── session.py      # Database session management
│   ├── models/             # SQLAlchemy ORM models
│   │   ├── encounter_session.py
│   │   ├── transcript_segment.py
│   │   ├── structured_record.py
│   │   ├── medical_document.py
│   │   ├── similar_case_match.py
│   │   ├── emr_draft.py
│   │   └── clinical_hint.py
│   ├── schemas/            # Pydantic request/response models
│   ├── services/           # Business logic layer
│   │   ├── asr_service.py          # ASR integration (Whisper/Dolphin)
│   │   ├── llm_service.py          # DeepSeek LLM integration
│   │   ├── extract_service.py      # Structured extraction
│   │   ├── document_service.py     # Document processing
│   │   ├── index_service.py        # Document indexing
│   │   ├── draft_service.py        # Draft generation
│   │   ├── clinical_hint_service.py # Clinical hints
│   │   ├── session_service.py      # Session management
│   │   └── transcript_service.py   # Transcript management
│   ├── prompts/            # AI prompt templates (must be file-based)
│   └── utils/              # Utility functions
├── dolphin_server.py       # Custom Flask server for Dolphin ASR
├── dolphin_env/            # Virtual environment for Dolphin
├── medical_records/        # Medical record PDFs directory
├── uploads/                # Uploaded audio files
├── logs/                   # Application logs
└── run.py                  # Application entry point
```

### Frontend Structure

```
frontend/
├── src/
│   ├── api/            # API client modules
│   │   ├── http.js          # Axios instance with interceptors
│   │   ├── session.js       # Session management API
│   │   ├── asr.js           # Speech recognition API
│   │   ├── extract.js       # Structured extraction API
│   │   ├── documents.js     # Document management API
│   │   ├── draft.js         # Draft generation API
│   │   └── clinicalHints.js # Clinical hints API
│   ├── components/     # Reusable Vue components
│   │   └── workbench/       # Workbench-specific components
│   ├── views/          # Page components
│   │   ├── DoctorWorkbench.vue    # Main workbench view
│   │   └── DocumentManagement.vue # Document management view
│   ├── stores/         # Pinia state management
│   │   ├── app.js           # Global app state
│   │   └── workbench.js     # Workbench state
│   ├── router/         # Vue Router configuration
│   ├── composables/    # Composition API utilities
│   │   └── useRecorder.js   # Audio recording composable
│   ├── utils/          # Utility functions
│   │   └── wavEncoder.js    # WAV audio encoding
│   ├── assets/         # Static assets
│   ├── App.vue         # Root component
│   └── main.js         # Application entry point
└── vite.config.js      # Vite configuration (includes proxy to backend)
```

### API Architecture

All APIs use `/api/v1` prefix with unified response format:
```json
{
  "success": true,
  "message": "Success message",
  "data": {}
}
```

**Frontend Proxy**: The Vite dev server proxies `/api` requests to `http://localhost:8001` (configured in `vite.config.js`), allowing the frontend to make API calls without CORS issues during development.

Key API endpoints:
- `/api/v1/health` - Health check
- `/api/v1/sessions` - Session management
- `/api/v1/asr/transcribe` - Speech recognition
- `/api/v1/extract` - Structured extraction
- `/api/v1/documents` - Document management
- `/api/v1/index` - Document indexing
- `/api/v1/draft` - Draft generation
- `/api/v1/clinical-hints` - Clinical hints

### Service Layer Pattern

The backend follows a service-oriented architecture:
1. **API Endpoints** (`app/api/endpoints/`) - Handle HTTP requests/responses
2. **Services** (`app/services/`) - Contain business logic
3. **Models** (`app/models/`) - Define database schema
4. **Schemas** (`app/schemas/`) - Define API contracts

Services are responsible for:
- External API integration (DeepSeek, OpenAI, Dolphin)
- Business logic and data processing
- Database operations via SQLAlchemy models

### Configuration Management

All configuration is managed through `app/core/config.py` using pydantic-settings:
- Environment variables loaded from `.env` file
- Type-safe configuration with validation
- Computed properties for derived values (e.g., `database_url`, `cors_origins_list`)

Key configuration categories:
- App settings (host, port, environment)
- Database connection
- DeepSeek API
- OpenAI API (for Whisper)
- Dolphin ASR
- LLM/ASR mock modes
- Directory paths
- CORS origins

### ASR Engine Configuration

The system supports three ASR modes (configured in `.env`):

1. **Mock Mode** (for testing):
   ```env
   ASR_USE_MOCK=true
   ```

2. **OpenAI Whisper** (cloud-based, high accuracy):
   ```env
   ASR_ENGINE=whisper
   ASR_USE_MOCK=false
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Dolphin** (local, cost-free):
   ```env
   ASR_ENGINE=dolphin
   ASR_USE_MOCK=false
   DOLPHIN_API_URL=http://localhost:8888/asr
   ```

The ASR service (`app/services/asr_service.py`) abstracts these implementations behind a unified interface.

### LLM Integration

DeepSeek integration is handled by `app/services/llm_service.py`:
- Supports mock mode for testing (`LLM_USE_MOCK=true`)
- Uses Instructor library for structured extraction
- Implements retry logic with tenacity
- All prompts must be stored as `.txt` files in `app/prompts/`
- Current prompts:
  - `extract_structured_record.txt` - Structured data extraction
  - `generate_emr_draft.txt` - EMR draft generation
  - `generate_clinical_hints.txt` - Clinical hints generation

### Audio Recording System

The frontend implements a dual-mode audio recording system:

1. **WebM Mode (Primary)**:
   - Uses MediaRecorder API to generate WebM format
   - Smaller file size (~50KB for 10 seconds)
   - Requires ffmpeg on backend for conversion to WAV
   - Faster upload and processing

2. **WAV Mode (Fallback)**:
   - Uses Web Audio API to generate WAV format directly
   - Larger file size (~250KB for 10 seconds)
   - No conversion needed on backend
   - Automatically used if browser doesn't support WebM or WebM recording fails

The system automatically selects the best mode based on browser capabilities.

## Development Guidelines

1. **Follow the technical specification document** - Do not modify interface names, table names, or directory structure arbitrarily
2. **API naming** - All APIs must use `/api/v1` prefix
3. **Response format** - Use unified format: `{success, message, data}`
4. **Prompts** - All AI prompts must be stored as `.txt` files in `backend/app/prompts/`
5. **Vue 3 Patterns** - Use Composition API with `<script setup>` syntax
6. **State Management** - Use Pinia stores for shared state across components
7. **Fixed business settings**:
   - Doctor: Doctor Panython
   - Patient: 张三 (Zhang San), Male, 29 years old
   - Medical records directory: `D:\webmedic\backend\medical_records\`

## Known Issues and Solutions

### PyTorch DLL Loading Failure (Windows)
**Issue**: PyTorch 2.10.0+cpu fails to load c10.dll on Windows
**Solution**: Downgrade to PyTorch 2.5.1
```bash
pip install --upgrade --force-reinstall torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu
```

### Dolphin ASR Setup
- Custom Flask server (`dolphin_server.py`) replaces `funasr-server` command
- Uses FunASR AutoModel to load Paraformer model
- Provides `/health` and `/asr` endpoints
- Runs on port 8888 to avoid conflicts
- Requires ffmpeg for WebM audio format conversion

### .env File Encoding
**Issue**: Chinese comments in `.env` file can cause HTTP header latin-1 encoding errors
**Solution**: Remove Chinese comments from configuration lines, especially `DOLPHIN_API_KEY`

## Testing

### Backend Tests
Backend tests are located in `backend/tests/`. The system uses:
- Mock modes for rapid testing without external API calls
- Real API integration for production-like testing

### Complete Workflow Testing

The system supports a complete end-to-end workflow:

1. **Start Session** - Create a new consultation session
2. **Record Audio** - Capture doctor-patient conversation via voice
3. **Transcribe** - Convert audio to text using ASR (Dolphin/Whisper/Mock)
4. **Extract** - Generate structured medical record from transcript
5. **Search Similar Cases** - Find similar historical cases from indexed documents
6. **Generate Draft** - Create EMR draft based on structured data and similar cases
7. **Generate Clinical Hints** - Produce risk alerts, follow-up questions, and suggested tests

To test the complete workflow:
```bash
# 1. Start backend and frontend
cd D:\webmedic\backend && python run.py
cd D:\webmedic\frontend && npm run dev

# 2. (Optional) Start Dolphin ASR if using local ASR
cd D:\webmedic\backend && start_dolphin.bat

# 3. Access frontend at http://localhost:5173
# 4. Follow the workflow: Start Session → Record → Extract → Search → Generate Draft → Generate Hints
```

## Port Configuration

- **Backend API**: 8001 (not 8000 as in README - actual config uses 8001)
- **Frontend Dev Server**: 5173
- **Dolphin ASR**: 8888 (custom server) or 8000 (standard funasr-server)
- **MySQL**: 3306

## Database

MySQL 8.0+ required. Connection configured via environment variables:
- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- SQLAlchemy ORM with async support
- Models define the schema; migrations not currently implemented

## Important Notes

- The backend uses port 8001 (configured in `.env`), not 8000 as mentioned in README
- Dolphin virtual environment is separate: `backend/dolphin_env/`
- Main backend virtual environment: `backend/venv/`
- All file paths use Windows-style backslashes in configuration but Unix-style forward slashes in code
- The system is designed for single-doctor, single-patient demo scenarios
- **Project Status**: Stages 1-8 completed. Core workflow (session → transcription → extraction → similar cases → draft → hints) is functional.

## Current Development Stage

The project has completed the following stages:
- ✅ Stage 1-2: Project initialization and backend foundation
- ✅ Stage 3-4: Frontend workbench and session management
- ✅ Stage 5: Audio upload and ASR transcription
- ✅ Stage 6: Structured extraction
- ✅ Stage 7: PDF indexing and similar case retrieval
- ✅ Stage 8: EMR draft generation and clinical hints
- ⏳ Stage 9: System optimization (history replay, manual editing, export, logging)

## Troubleshooting

### Dolphin ASR Issues

**WebM format not supported**:
- Error: `Format not recognised` when processing browser audio
- Solution: Install ffmpeg and add to system PATH
- Verify: `ffmpeg -version`

**Dolphin service won't start**:
- Check if port 8888 is already in use
- Ensure `dolphin_env` virtual environment is activated
- Verify FunASR is installed: `pip list | grep funasr`

### Database Connection Issues

**Connection refused**:
- Verify MySQL is running
- Check credentials in `.env` file
- Ensure database `webmedic_demo` exists

### API Call Failures

**DeepSeek API errors**:
- Verify `DEEPSEEK_API_KEY` in `.env`
- Check network connectivity
- Consider using `LLM_USE_MOCK=true` for testing

**OpenAI Whisper errors**:
- Verify `OPENAI_API_KEY` in `.env`
- Consider switching to Dolphin: `ASR_ENGINE=dolphin`
- Use `ASR_USE_MOCK=true` for testing without API calls
