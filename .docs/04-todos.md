# RAG Agent Platform - Development Todos

## Document Info

| | |
|--|--|
| **Version** | 1.0 |
| **Date** | December 2024 |
| **Status** | In Progress |

---

## Current Progress Overview

| Component | Status | Notes |
|-----------|--------|-------|
| LiteLLM Proxy | ✅ Done | Running on port 4000, UI available |
| Frontend (SvelteKit) | 🟡 Skeleton | Basic setup + Tailwind |
| Backend (FastAPI) | ❌ Not Started | Empty folder |
| PostgreSQL | ✅ Done | Running in docker (for LiteLLM) |
| Redis | ✅ Done | Running for LiteLLM cache |
| ChromaDB | ❌ Not Started | - |
| Auth System | ❌ Not Started | - |
| RAG Pipeline | ❌ Not Started | - |
| Agent System | ❌ Not Started | - |

---

## Phase 1: Foundation (Infrastructure & Basic App)

### 1.1 Infrastructure Setup
- [x] Setup LiteLLM Docker Compose
- [x] Create LiteLLM config (Gemini + Groq models)
- [x] Generate environment variables script
- [x] Test LiteLLM proxy connection
- [x] Setup PostgreSQL in docker-compose
- [x] Setup Redis (for LiteLLM cache)
- [x] Verify all containers run together
- [x] Setup LiteLLM UI credentials

### 1.2 Backend Setup (FastAPI)
- [ ] Initialize FastAPI project structure
- [ ] Setup project dependencies (requirements.txt / pyproject.toml)
- [ ] Create main.py entrypoint
- [ ] Setup CORS middleware
- [ ] Create health check endpoint
- [ ] Setup database connection (SQLAlchemy + PostgreSQL)
- [ ] Create Alembic migrations setup
- [ ] Create base database models (User, Project, Conversation)
- [ ] Setup environment configuration (pydantic-settings)

### 1.3 Authentication System
- [ ] Create User model & schema
- [ ] Implement password hashing (bcrypt)
- [ ] Create JWT token utilities
- [ ] Implement register endpoint
- [ ] Implement login endpoint
- [ ] Implement logout endpoint
- [ ] Create auth middleware
- [ ] Implement /me endpoint (get current user)
- [ ] Add refresh token support

### 1.4 Frontend Setup (SvelteKit)
- [x] Initialize SvelteKit project
- [x] Setup Tailwind CSS
- [x] Setup i18n (paraglide)
- [ ] Create base layout component
- [ ] Create navigation/header component
- [ ] Create sidebar component
- [ ] Setup API client (fetch wrapper)
- [ ] Create auth store (Svelte stores)
- [ ] Implement login page
- [ ] Implement register page
- [ ] Add protected route logic

### 1.5 Basic Chat Integration
- [ ] Create LiteLLM client wrapper in backend
- [ ] Implement /chat endpoint (non-streaming)
- [ ] Implement /chat/stream endpoint (SSE streaming)
- [ ] Create chat UI component
- [ ] Implement message input component
- [ ] Implement message display (markdown support)
- [ ] Add code syntax highlighting
- [ ] Connect frontend to backend chat API
- [ ] Test end-to-end chat flow

**Phase 1 Deliverable**: User can register, login, and chat with AI

---

## Phase 2: RAG Core (Document & Retrieval)

### 2.1 Document Processing
- [ ] Setup ChromaDB in docker-compose
- [ ] Create document upload endpoint
- [ ] Implement file validation (PDF, DOCX, TXT, MD, CSV)
- [ ] Integrate PDF text extraction (PyMuPDF / pdfplumber)
- [ ] Integrate DOCX text extraction (python-docx)
- [ ] Create text chunking service (recursive splitter)
- [ ] Add metadata extraction

### 2.2 Embedding & Vector Store
- [ ] Setup sentence-transformers
- [ ] Download multilingual-e5-base model
- [ ] Create embedding service
- [ ] Implement ChromaDB collection per project
- [ ] Create document indexing pipeline
- [ ] Implement document deletion (remove from vector store)

### 2.3 Retrieval Pipeline
- [ ] Implement dense search (embedding similarity)
- [ ] Implement hybrid search (Dense + BM25) - optional
- [ ] Create query preprocessing
- [ ] Implement context assembly
- [ ] Add re-ranking (optional)
- [ ] Create RAG prompt template

### 2.4 Source Citations
- [ ] Track source documents in retrieval
- [ ] Include sources in LLM response
- [ ] Parse and display sources in frontend
- [ ] Link to original document/page

### 2.5 Document Management UI
- [ ] Create document list component
- [ ] Implement document upload UI (drag & drop)
- [ ] Show upload progress
- [ ] Display document status (processing, ready, error)
- [ ] Implement document delete UI

**Phase 2 Deliverable**: User can upload documents and ask questions with RAG

---

## Phase 3: Agent System

### 3.1 Agent Core
- [ ] Create base Agent class
- [ ] Implement agent configuration loader (YAML)
- [ ] Create agent registry
- [ ] Implement agent execution engine
- [ ] Add tool execution framework

### 3.2 Built-in Tools
- [ ] Create RAG search tool
- [ ] Create summarize tool
- [ ] Create calculator tool
- [ ] Create web search tool (optional)

### 3.3 Pre-built Agents
- [ ] Create General agent (general.yaml)
- [ ] Create HR agent (hr.yaml)
- [ ] Create Legal agent (legal.yaml)
- [ ] Create Finance agent (finance.yaml)
- [ ] Create Research agent (research.yaml)

### 3.4 Agent UI
- [ ] Create agent selector modal
- [ ] Display agent info (name, description, icon)
- [ ] Implement agent switching per project
- [ ] Add agent thinking display (step-by-step)
- [ ] Show tool execution visualization

**Phase 3 Deliverable**: User can select different agents for different tasks

---

## Phase 4: Project System

### 4.1 Project Backend
- [ ] Create Project model & schema
- [ ] Implement project CRUD API
- [ ] Setup per-project document storage
- [ ] Setup per-project ChromaDB collections
- [ ] Implement project settings storage

### 4.2 Conversation Management
- [ ] Create Conversation model
- [ ] Create Message model
- [ ] Implement conversation CRUD API
- [ ] Add conversation history retrieval
- [ ] Implement context window management
- [ ] Add conversation summarization (for long chats)

### 4.3 Project UI
- [ ] Create project list in sidebar
- [ ] Implement create project modal
- [ ] Implement project settings modal
- [ ] Add project switching
- [ ] Show project-specific documents
- [ ] Show project-specific conversations

**Phase 4 Deliverable**: User can organize work into isolated projects

---

## Phase 5: User Control & Polish

### 5.1 Usage Tracking
- [ ] Create usage tracking service
- [ ] Track token usage per user
- [ ] Track request count per user
- [ ] Calculate cost per user
- [ ] Store usage history

### 5.2 Limits & Quotas
- [ ] Implement user tier system (Free/Pro/Enterprise)
- [ ] Add token quota (monthly)
- [ ] Add rate limiting (requests/minute)
- [ ] Add document upload limit
- [ ] Add project count limit
- [ ] Implement 80% usage warning
- [ ] Implement limit reached blocking

### 5.3 Debug Panel
- [ ] Create debug panel component (collapsible)
- [ ] Show retrieved chunks
- [ ] Display similarity scores
- [ ] Show retrieval latency
- [ ] Display token count
- [ ] Show cost estimation

### 5.4 Admin Panel
- [ ] Create admin routes (protected)
- [ ] Implement user list view
- [ ] Add user edit (tier, limits)
- [ ] Add user suspend/ban
- [ ] Create usage dashboard
- [ ] Add system metrics view

### 5.5 Polish & Optimization
- [ ] Add comprehensive error handling
- [ ] Implement retry logic
- [ ] Add loading states throughout
- [ ] Optimize database queries
- [ ] Add caching where appropriate
- [ ] Performance testing

**Phase 5 Deliverable**: Production-ready application

---

## Phase 6: Advanced Features (Optional)

### 6.1 Enhanced RAG
- [ ] Implement re-ranking with cross-encoder
- [ ] Add query expansion
- [ ] Implement multi-query retrieval

### 6.2 Multi-Model
- [ ] Add model selector dropdown
- [ ] Implement per-conversation model switching
- [ ] Add A/B model comparison mode

### 6.3 Voice Features
- [ ] Add voice input (STT - Speech to Text)
- [ ] Add voice output (TTS - Text to Speech)

### 6.4 Collaboration
- [ ] Implement team/workspace feature
- [ ] Add project sharing
- [ ] Add member roles (owner, editor, viewer)

### 6.5 Custom Agents
- [ ] Create agent builder UI
- [ ] Allow custom tool creation
- [ ] Enable agent sharing/marketplace

---

## Technical Debt & Improvements

- [ ] Add comprehensive unit tests
- [ ] Add integration tests
- [ ] Setup CI/CD pipeline (GitHub Actions)
- [ ] Add API documentation (OpenAPI/Swagger)
- [ ] Create deployment documentation
- [ ] Setup monitoring (Prometheus + Grafana)
- [ ] Add logging infrastructure
- [ ] Security audit

---

## Notes

### Priority Order
1. **Phase 1** - Must complete first (foundation)
2. **Phase 2** - Core differentiator (RAG)
3. **Phase 3** - Key feature (Agents)
4. **Phase 4** - Organization (Projects)
5. **Phase 5** - Production-ready (Polish)
6. **Phase 6** - Nice to have (Advanced)

### Current Focus
> **Next Step**: Complete Phase 1.2 (Backend Setup)

### Blockers
- None currently

---

*Last updated: December 2024*
