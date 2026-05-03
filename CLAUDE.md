# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent Y is a decision support system based on top-case thinking patterns. It helps users find the optimal action plan in complex decision scenarios through systematic knowledge retrieval, multi-scenario analysis, and probability-based recommendations.

**Key Feature: Dynamic Domain Expansion**
- System starts with 5 seed domains (互联网产品, 职业发展, 医疗健康, 教育培训, 制造业)
- When user query doesn't match existing domains, system uses LLM to suggest a new domain
- New domains are automatically created in the database
- Knowledge base grows with user queries

## Tech Stack

- **Frontend**: React 18, TypeScript, TailwindCSS, Zustand, Vite
- **Backend**: Python, FastAPI, SQLAlchemy, Pydantic
- **Database**: SQLite (schema in `database/schema.sql`)

## Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Run tests
python -m pytest tests/ -v --tb=short
```

### Frontend
```bash
cd frontend
npm install
npm run dev      # development
npm run build    # production build
npm test         # vitest tests (also: npm test -- --run)
```

### Database
```bash
cd database/seed_data
python seed_db.py    # initialize database
python init_knowledge.py
```

## Testing

### Backend Tests (pytest)
```bash
cd backend && python -m pytest tests/ -v
```

### Frontend Tests (vitest)
```bash
cd frontend && npm test -- --run
```

### CI Pipeline
GitHub Actions runs on every push/PR (`.github/workflows/ci.yml`):
- Backend: Python 3.11 + pytest
- Frontend: Node 18 + vitest + build check

## Architecture

### Core Logic (`backend/app/core/`)

- **agent.py** - `AgentY` class is the main orchestration engine. It:
  - Identifies domain from user query using keyword matching against database domains + default domains
  - If no match found, uses LLM to suggest a new domain name from the query
  - Creates new domain records in database when needed
  - Retrieves relevant knowledge from the knowledge base
  - Generates dynamic questions when more info is needed
  - Produces full analysis with scenarios, probabilities, recommendations, and leading indicators
  - Optionally calls LLM (`MiniMaxClient`) for enhanced analysis and question generation

- **scenario.py** - `ScenarioEngine` generates 3 scenarios (high/medium/low probability). Uses domain-specific templates when available, falls back to generic scenarios for new domains
- **knowledge.py** - `KnowledgeBase` handles retrieval from the knowledge database
- **llm_client.py** - `MiniMaxClient` provides optional LLM enhancement (can operate in fallback mode without API key)

### Domain Identification Flow
```
User Query → Keyword Match (existing domains in DB + DEFAULT_DOMAINS)
                  ↓
            Match found? → Yes → Use existing domain
                  ↓ No
            LLM suggests domain name from query
                  ↓
            Create new domain record in DB → Use new domain
```

### API Routes (`backend/app/api/`)
- `consultation.py` - Main analysis endpoint
- `industries.py` - Domain listing (domains grow dynamically)
- `knowledge.py` - Knowledge base queries
- `feedback.py` - User feedback on recommendations
- `conversations.py` - Conversation history

### Data Flow
```
Query → Domain Identification → Knowledge Retrieval
                                    ↓
                          Sufficient info?
                         No → Generate dynamic questions
                        Yes → Full Analysis
                                    ↓
                    ┌───────────────────────────────┐
                    ↓                               ↓
            Scenarios + Probabilities    LLM Enhancement (optional)
                    ↓                               ↓
            ┌───────┴───────┐                       ↓
            ↓               ↓              Natural language recommendation
     Recommendations    Leading Indicators
```

### Frontend Structure (`frontend/src/`)
- `pages/` - HomePage, ConsultationPage, KnowledgePage, HistoryPage
- `components/` - Layout, ProbabilityChart, RequiredInfoForm, Skeleton
- `services/api.ts` - Backend API calls
- `store/appStore.ts` - Zustand state management

## Key Design Notes

- Agent Y uses a "probability-first" approach rather than seeking perfect solutions - it recommends the highest win-rate action based on current information
- The LLM is optional - if no API key is configured, the system falls back to keyword-based scenarios and static question templates
- Domain identification: first tries keyword matching against DB + DEFAULT_DOMAINS; if no match, uses LLM to suggest a new domain name from the query
- New domains are automatically created in the database when LLM suggests one
- Scenario engine uses domain-specific templates for the 5 seed domains, falls back to generic "稳妥推进/积极探索/借力合作" patterns for new domains
- The agent uses async SQLAlchemy for database operations