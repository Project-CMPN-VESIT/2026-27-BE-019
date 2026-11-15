# 🌙 Dione — Sentient Local AI Assistant

> **"Intelligence that lives with you, not above you."**

Dione is a **Local Large Action Model (LAM) Orchestration Engine** — a privacy-first, agentic AI personal assistant that runs entirely on your hardware. Unlike cloud-dependent assistants, Dione keeps your data sovereign, builds a living knowledge graph of your digital life, and understands the emotional context of your world.

## ✨ Star Factors

### 1. 🧠 Personal Knowledge Graph
Not flat-file memory — a **structured graph database** connecting people, events, documents, and preferences with typed relationships. When you say "send that thing to Alice," Dione traverses the graph and *knows* what you mean.

### 2. 💜 Sentiment Intelligence Engine
Every incoming message is analyzed for emotional weight — urgency, frustration, importance, tone. Dione dynamically prioritizes, escalates, or batches information based on how it *feels*, not just what it says.

### 3. 📱 Mobile Chat Companion
Dione lives on your PC (local LLM + engine). You talk to it through a beautiful mobile app — proactive notifications, contextual suggestions, and a conversational UI that makes it feel like texting a brilliant friend.

### 4. 🔒 Zero-Trust Local Intelligence
All reasoning happens on YOUR device. No data leaves your machine except the specific API calls YOU authorize (sending an email, posting a message). Your digital life stays yours.

## 🏗️ Architecture

```
┌──────────────────────────────────────────┐
│           YOUR PC (Dione's Home)          │
│                                           │
│  ┌──────────┐  ┌───────────────────────┐ │
│  │ Local LLM │  │   Knowledge Graph     │ │
│  │ (Mistral/ │  │ (People, Events,     │ │
│  │  Llama)   │  │  Docs, Relations)    │ │
│  └─────┬─────┘  └──────────┬───────────┘ │
│        │                   │              │
│  ┌─────▼───────────────────▼───────────┐ │
│  │      Dione Orchestration Engine      │ │
│  │   ReAct Loop · Plugin System ·       │ │
│  │   Sentiment Engine · Memory Manager  │ │
│  └──────────────┬──────────────────────┘ │
│                 │  FastAPI (REST + WS)    │
└─────────────────┼────────────────────────┘
                  │
     ┌────────────┼──────────────┐
     │            │              │
 ┌───▼────┐  ┌───▼────┐  ┌─────▼──────┐
 │ Mobile  │  │ PC CLI │  │  Plugins   │
 │  App    │  │ / Web  │  │ (WhatsApp, │
 │(Flutter)│  │   UI   │  │ Gmail ...) │
 └────────┘  └────────┘  └────────────┘
```

## 📂 Project Structure

```
dione/
├── server/                    # Python backend (Dione's brain)
│   ├── core/                  # Orchestration engine
│   │   ├── engine.py          # Main ReAct loop
│   │   ├── context.py         # Context manager (sliding window + RAG)
│   │   ├── safety.py          # Safety guardrails & validation
│   │   └── permissions.py     # Permission manifest system
│   ├── llm/                   # LLM adapter layer
│   │   ├── adapter.py         # Unified LLM interface
│   │   ├── ollama.py          # Ollama backend
│   │   └── llamacpp.py        # llama.cpp backend
│   ├── knowledge/             # Knowledge Graph system
│   │   ├── graph.py           # Graph database operations
│   │   ├── entities.py        # Entity definitions (Person, Event, Doc)
│   │   ├── relations.py       # Relationship types
│   │   └── query.py           # Graph query engine
│   ├── sentiment/             # Sentiment Intelligence Engine
│   │   ├── analyzer.py        # Sentiment analysis pipeline
│   │   ├── priority.py        # Priority scoring & escalation
│   │   └── models.py          # Sentiment data models
│   ├── memory/                # Persistent memory system
│   │   ├── manager.py         # Memory lifecycle management
│   │   ├── vectorstore.py     # ChromaDB vector store
│   │   └── embeddings.py      # Local embedding generation
│   ├── plugins/               # Plugin system
│   │   ├── registry.py        # Plugin loader & registry
│   │   ├── base.py            # Base plugin class + @dione_tool decorator
│   │   ├── sandbox.py         # Sandboxed execution environment
│   │   └── builtin/           # Built-in plugins
│   │       ├── gmail.py       # Gmail integration
│   │       ├── whatsapp.py    # WhatsApp reader
│   │       ├── calendar.py    # Calendar management
│   │       ├── filesystem.py  # Local file operations
│   │       └── browser.py     # Browser automation
│   ├── api/                   # API layer
│   │   ├── app.py             # FastAPI application
│   │   ├── routes/            # API routes
│   │   │   ├── chat.py        # Chat endpoints (REST + WebSocket)
│   │   │   ├── knowledge.py   # Knowledge graph endpoints
│   │   │   ├── plugins.py     # Plugin management endpoints
│   │   │   └── status.py      # System status & health
│   │   └── middleware.py      # Auth, CORS, rate limiting
│   ├── config/                # Configuration
│   │   ├── settings.py        # Pydantic settings model
│   │   └── defaults.py        # Default configuration values
│   ├── main.py                # Server entry point
│   ├── requirements.txt       # Python dependencies
│   └── pyproject.toml         # Project metadata
├── mobile/                    # Flutter mobile app
│   └── dione_app/             # Flutter project root
├── docs/                      # Documentation
│   ├── Synopsis .pdf          # Original synopsis
│   ├── ARCHITECTURE.md        # Detailed architecture document
│   └── STAR_FACTORS.md        # Star factor documentation
├── scripts/                   # Utility scripts
│   ├── setup.sh               # One-line setup script
│   └── start.py               # Start Dione server
├── data/                      # Local data directory (gitignored)
│   ├── knowledge/             # Knowledge graph storage
│   ├── vectors/               # ChromaDB vector storage
│   └── memory/                # Persistent memory files
├── .env.example               # Environment variable template
├── .gitignore                 # Git ignore rules
├── docker-compose.yml         # Docker setup (optional)
└── README.md                  # This file
```

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd dione

# 2. Install Python dependencies
cd server
pip install -r requirements.txt

# 3. Start Ollama with a local model
ollama pull mistral:7b-instruct

# 4. Configure
cp .env.example .env
# Edit .env with your settings

# 5. Run Dione
python main.py

# 6. Run the mobile app
cd ../mobile/dione_app
flutter run
```

## 👥 Project Team & Individual Contribution Matrix

Developed as **Capstone Project - I (2025–26)** at **Vivekanand Education Society's Institute of Technology (VESIT)**, Department of Computer Engineering, affiliated with the **University of Mumbai**.

**Project Guide:** Mrs. Geocey Shejy, Assistant Professor, Department of Computer Engineering, VESIT

### Comprehensive Work Distribution & Ownership (100% Breakdown)

| Contributor | Class & Roll No. | Project Role | Contribution % | Primary Modules & Code Ownership | Key Deliverables & Research Responsibilities |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **Jass Suraj Shivnani** | D12B, Roll 50 | **Lead System Architect & Core Runtime Lead** | **35%** | `server/core/engine.py`<br>`server/plugins/builtin/computer_use_plugin.py`<br>`server/core/safety.py`<br>`server/core/tool_repair.py`<br>`server/core/loop_detector.py` | • NousResearch Hermes ReAct Autonomous Execution Loop<br>• Win32 Dual `SendInput` / Ribbon Shape Diagonal Drag Engine<br>• Poset Permission Lattice & AST Command Sanitizer<br>• OpenClaw Tool-Call Repair & Arg Coercion Runtime<br>• System Architecture Section of Research Paper |
| **Riya Sanjay Khialani** | D12A, Roll 34 | **Live Multimodal Audio & Frontend Engineering Lead** | **30%** | `server/api/routes/audio.py`<br>`server/llm/gemini_live_orchestrator.py`<br>`client/src/App.tsx`<br>`client/src/services/neuralAudio.ts`<br>`server/api/routes/ag_ui.py`<br>`server/plugins/integrations/` | • Full-Duplex 16kHz Bidirectional Gemini Live WebSocket Audio Pipeline<br>• OpenClaw Two-Tier Frosted Glass UI & Live Demo Deck<br>• AG-UI SSE Real-Time Streaming Bridge & Action Approval Modals<br>• Multi-Channel Integrations (Gmail, Calendar, Drive, WhatsApp, Telegram)<br>• Methodology & Live Voice Benchmarking Section |
| **Khushi Sadhuramani** | D12B, Roll 44 | **Knowledge Graph & GraphRAG Memory Specialist** | **18%** | `server/knowledge/graph.py`<br>`server/knowledge/relations.py`<br>`server/knowledge/social_intelligence.py`<br>`server/api/routes/knowledge.py`<br>`client/src/components/KnowledgeGraphView.tsx` | • NetworkX 2-Hop Relational Multigraph Implementation<br>• Entity Disambiguation & Identity Resolution for Colliding Names<br>• Social Intelligence Engine & Contact Commitment Dossiers<br>• Knowledge Graph Visual REST Endpoints & UI Rendering<br>• Literature Review on GraphRAG & Entity Memory Models |
| **Ruchika Dingria** | D12B, Roll 70 | **Proactive Inactive Synthesis & Quality Assurance Specialist** | **17%** | `server/proactive/dream_engine.py`<br>`server/bin/dione_research_benchmark.py`<br>`server/personality/profile.py`<br>`server/api/routes/desktop.py`<br>`docs/` Black Book Reports | • Autonomous Inactive-State "Dream & Scout" Engine<br>• Win32 Idle-Time Tracker & Genuine Gmail Scouting Pipeline<br>• Empirical 100-Case Evaluation Test Harness & Metric Auditing<br>• IEEE Research Paper Documentation & Overleaf LaTeX Formatting<br>• Turnitin Similarity & Black Book Compliance Verification |

*Note: In accordance with project governance, primary engineering leads (Jass Shivnani & Riya Khialani, 65% combined) spearheaded the core execution kernel, native desktop automation, live multimodal streaming, and frontend interfaces, while secondary specialists (Khushi Sadhuramani & Ruchika Dingria, 35% combined) architected the relational memory multigraph, proactive background scout subsystem, empirical validation suite, and academic report compilation.*

## 📄 License

This project is developed as a Capstone Project (2025-26) at Vivekanand Education Society's Institute of Technology, Department of Computer Engineering.
