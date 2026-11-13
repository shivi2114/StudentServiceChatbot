# CampusAI – Production Multi-Agent Student Assistance Platform

> An enterprise-grade, multi-agent student assistance system transforming campus service navigation through LangGraph agent orchestration, ChromaDB RAG grounding, persistent PostgreSQL/SQLite memory, human-in-the-loop governance, and a React + Tailwind CSS collegiate dashboard.

---

## 1. System Overview

**CampusAI** is an agentic AI university platform where multiple specialized agents collaborate to understand complex student inquiries, perform grounded document retrieval, verify student fee records, track and escalate grievance tickets, and guide career/placement journeys.

### Key Capabilities

- **LangGraph Multi-Agent Orchestration**: Dynamic query decomposition and routing between 7 specialized agents.
- **RAG Knowledge Base**: Instant semantic retrieval across official college notices, examination ordinances, fee schedules, scholarship manuals, and placement policies using ChromaDB and vector cosine ranking.
- **Real Task Execution & Database Tools**: Directly queries and updates persistent student records, attendance ledgers, fee statuses, and grievance tickets.
- **Human-in-the-Loop Governance**: Mandatory user confirmation before consequential actions (e.g. filing formal complaint tickets or creating deadline reminders).
- **Multi-Tier LLM Resilience**:
  - **Tier 1**: Google Gemini API (`gemini-2.5-flash` / `gemini-1.5-pro`)
  - **Tier 2**: Groq Cloud Fallback (`qwen/qwen3.8-27b`)
  - **Tier 3**: Verified Institutional Safety Knowledge Base (zero downtime guarantee)
- **Role-Based Access Control (RBAC)**: Secure JWT authentication separating Student and Administrator experiences.
- **Bilingual Communication**: Seamless bilingual inquiry handling in English and Hindi.
- **100% Backward Compatibility**: Original Streamlit chatbot (`app.py`, 48-intent ML model, and dataset) is fully preserved.

---

## 2. Multi-Agent Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │               React + Tailwind Frontend                │
                    │   (Student Dashboard, Multi-Agent Chat, Admin Portal)   │
                    └───────────────────────────┬────────────────────────────┘
                                                │ REST / Bearer JWT
                                                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                FastAPI Backend Service                                 │
│                                                                                        │
│  ┌────────────────────┐   ┌─────────────────────────────────────────────────────────┐  │
│  │ JWT Authentication │   │                   LangGraph Supervisor                  │  │
│  │  & RBAC Middleware │   │                   (Orchestrator Agent)                  │  │
│  └────────────────────┘   └────────────────────────────┬────────────────────────────┘  │
│                                                        │                               │
│       ┌──────────────────┬─────────────────┬───────────┴───────┬──────────────────┐    │
│       ▼                  ▼                 ▼                   ▼                  ▼    │
│  ┌──────────┐     ┌─────────────┐   ┌─────────────┐     ┌─────────────┐    ┌─────────┐ │
│  │ Academic │     │ Admission & │   │  Complaint  │     │ Scholarship │    │ Notif.  │ │
│  │  Agent   │     │  Fee Agent  │   │  Mgt Agent  │     │ & Placement │    │  Agent  │ │
│  └────┬─────┘     └──────┬──────┘   └──────┬──────┘     └──────┬──────┘    └────┬────┘ │
│       │                  │                 │                   │                │      │
│       ▼                  ▼                 ▼                   ▼                ▼      │
│  ┌──────────┐     ┌─────────────┐   ┌─────────────┐     ┌─────────────┐    ┌─────────┐ │
│  │ RAG Tool │     │ Fee DB Tool │   │ Ticket Tool │     │ Schemes DB  │    │ Alert   │ │
│  │ (Chroma) │     │ (Postgres)  │   │ (Postgres)  │     │ (Postgres)  │    │ Service │ │
│  └────┬─────┘     └──────┬──────┘   └──────┬──────┘     └──────┬──────┘    └────┬────┘ │
└───────┼──────────────────┼─────────────────┼───────────────────┼────────────────┼──────┘
        ▼                  ▼                 ▼                   ▼                ▼       
 ┌──────────────┐   ┌──────────────────────────────────────────────────────────────────┐  
 │   ChromaDB   │   │                     PostgreSQL / SQLite Database                 │  
 │ (Embeddings  │   │   (Users, Students, Fees, Attendance, Complaints, Announcements) │  
 │  & Notices)  │   └──────────────────────────────────────────────────────────────────┘  
 └──────────────┘                                                                         
```

### Specialized Agents

| Agent | Responsibility | Real Tools / DB Integration | Human Confirmation |
| :--- | :--- | :--- | :---: |
| **Orchestrator Agent** | Analyzes intent, coordinates specialized agents, aggregates citations, crafts final response. | LangGraph State Graph, Intent Router. | No |
| **Academic Agent** | 75% attendance rule, condonations (up to 15%), passing marks, revaluation, back-papers. | `rag_store.search`, `get_student_academic_summary`. | No |
| **Admission & Fee Agent** | Tuition fees (₹65,000/sem), hostel dues, online ERP payments, late fee fines, refunds. | `rag_store.search`, `get_student_fee_summary`. | No |
| **Complaint Agent** | Grievance collection, ticket generation (`CMP-2026-XXXX`), tracking, Proctorial escalation. | `create_complaint_ticket_in_db`, `escalate_complaint_in_db`. | **Yes** (Required before ticket registration) |
| **Scholarship Agent** | UP Post-Matric scheme, AICTE Pragati, Campus Merit-cum-Means (MCM) 25%/50% waiver matching. | `rag_store.search`, student CGPA matcher. | No |
| **Placement Agent** | Placement tiers (Dream > 10 LPA, Core 6-10 LPA, Mass 3.5-5.5 LPA), 8th-sem NOC, upcoming drives. | `rag_store.search`, student CGPA cutoff checker. | No |
| **Notification Agent** | Examination alerts, assignment due dates, fee due warnings. | `create_student_reminder_in_db`. | **Yes** (Required before scheduling alerts) |

---

## 3. Technology Stack

- **Frontend**: React 18, Tailwind CSS, Lucide React, Axios, Vite
- **Backend API**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **Agent Orchestration**: LangGraph, LangChain Core
- **LLMs**: Google Gemini (`google-genai`) with Groq Cloud fallback
- **Vector Database**: ChromaDB + Dense Local Embedding Function
- **Main Database**: PostgreSQL (production) with automatic zero-config SQLite fallback
- **Security**: JWT Authentication (HS256), Bcrypt password hashing
- **Deployment**: Render (`render.yaml`), Railway (`railway.json`), Dockerfile

---

## 4. Quick Start & Setup

### A. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Set your credentials in `.env`:

```env
# Primary LLM
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Fallback LLM (Optional, resilience fallback)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=qwen/qwen3.8-27b

# Database (Leave default for instant SQLite, or provide PostgreSQL URI)
DATABASE_URL=sqlite:///./campusai.db
SECRET_KEY=campusai-secret-key-production-grade-2026
```

### B. Python Virtual Environment Setup

```bash
# Activate existing virtual environment
.\venv\Scripts\activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### C. Launch Unified CampusAI Application (Single Command)

The FastAPI server mounts and serves the pre-built React frontend and Swagger API documentation together:

```bash
python backend/app/main.py
```

- **Web Dashboard & Chatbot**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`
- **System Health**: `http://localhost:8000/health`

### D. Optional: Run Decoupled Vite Dev Server

For active frontend development with hot-module replacement (HMR):

```bash
# Terminal 1: Backend
python backend/app/main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open `http://localhost:5173`. Requests to `/api` are automatically proxied to the backend.

---

## 5. Demo Credentials

The database automatically initializes with sample campus data upon first launch:

| User Type | Email | Password | Details & Profile |
| :--- | :--- | :--- | :--- |
| **Demo Student** | `student@campusai.edu` | `student123` | **Aarav Sharma** (Roll: `2026CS1042`, B.Tech CSE Sem 6, CGPA 8.72, Hostel B-304, ₹20,000 fee due, 81.4% attendance) |
| **Campus Admin** | `admin@campusai.edu` | `admin123` | **Dr. Sunita Verma** (Dean Student Welfare & Proctorial Desk) |

*You can also use the **"One-Click Evaluator Access"** buttons on the login screen.*

---

## 6. Running Integration Tests

To run the automated multi-agent test suite:

```bash
python test_agents.py
```

This verifies:
1. Student authentication and JWT generation
2. Academic Agent execution with ChromaDB RAG citations
3. Admission & Fee Agent personal fee balance lookup
4. Complaint Agent action confirmation and database ticket registration
5. Scholarship Agent MCM fellowship eligibility matching
6. Placement Agent Dream drive cutoff verification

---

## 7. Legacy Streamlit Application

Your original Streamlit chatbot is fully preserved in the root directory:

```bash
python -m streamlit run app.py
```

Runs on `http://localhost:8501`.
