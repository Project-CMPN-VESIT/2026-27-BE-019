# University of Mumbai — Department of Computer Engineering
## Capstone Project – I (Semester VI, Academic Year 2025–2026)
### Project Group No. 19: Dione — Ambient Personal Assistant & Local LAM Orchestration Runtime
**Institution:** Vivekanand Education Society's Institute of Technology (VESIT), Chembur, Mumbai  
**Project Guide / Mentor:** Prof. Geocey Shejy, Assistant Professor, Department of Computer Engineering  
**Head of Department:** Dr. (Mrs.) Nupur Giri  
**Principal:** Dr. (Mrs.) J. M. Nair  

---

## 1. Executive Summary & Work Allocation Model

The Dione Autonomous Agent platform is an engineering capstone project designed, developed, and evaluated by a four-member student cohort from the Department of Computer Engineering at VESIT. The project architecture deliberately follows an uneven dual-lead and dual-specialist distribution model (100% total allocation), where two primary leads spearhead the core autonomous reasoning loop and live multimodal streaming pipelines, while two dedicated specialists engineer the relational multigraph memory system and proactive synthesis/QA benchmark infrastructure.

```
+--------------------------------------------------------------------------------------------------+
|                                    PROJECT GROUP 19 (100%)                                       |
+------------------------------------+-------------------------------------------------------------+
|  Primary Lead 1 (35%)              |  Primary Lead 2 (30%)                                       |
|  Jass Suraj Shivnani (D12B, 50)    |  Riya Sanjay Khialani (D12A, 34)                            |
|  Lead System Architect             |  Live Multimodal Audio & UI Lead                            |
|  - ReAct Execution Core            |  - 16kHz Gemini Live Full-Duplex Audio                      |
|  - Win32 CUA Actuation & Hardware  |  - OpenClaw Frosted Glass UI & AG-UI SSE                    |
|  - Poset Lattice Security Guard    |  - Multi-Channel Workspace Services (Gmail, Cal)            |
|  - AST Error Repair & Compactor    |  - Dynamic Mobile Auth QR & Protocol Bridge                 |
+------------------------------------+-------------------------------------------------------------+
|  Secondary Specialist 3 (18%)      |  Secondary Specialist 4 (17%)                               |
|  Khushi Sadhuramani (D12B, 44)     |  Ruchika Dingria (D12B, 70)                                 |
|  Knowledge Graph & Memory          |  Proactive Inactive Synthesis & QA                          |
|  - NetworkX 2-Hop Multigraph Engine|  - Win32 Idle Tracking & Touch-Wake Loop                    |
|  - Entity Resolution & Disambig.   |  - "Dream & Scout" Autonomous Offline Mail Reading          |
|  - ChromaDB Vector Synchronization |  - Multi-Axis Affective Sentiment Classifier                |
|  - Interactive Graph UI Endpoints  |  - 100-Case Empirical Benchmark & IEEE Audit                |
+------------------------------------+-------------------------------------------------------------+
```

---

## 2. Comprehensive Work Distribution Matrix

| Contributor | Class & Roll | Primary Responsibilities & Architectural Modules | Contribution % | Key Deliverables & Repositories |
| :--- | :--- | :--- | :---: | :--- |
| **Jass Suraj Shivnani** *(Lead System Architect)* | **D12B, Roll 50** | **Core Autonomous Runtime & OS Integration:**<br>• Core ReAct execution loop with step budgeting ($N_{\max} = 10$).<br>• Native CUA Win32 hardware simulation (`SendInput`, `mouse_event`, UIA).<br>• 5-Tier Poset Lattice Security Kernel & permission prompts.<br>• Tool Self-Healing AST Parser & Session Compactor.<br>• FastAPI server lifecycle and process management. | **35%** | `server/core/engine.py`<br>`server/hermes_computer_use/`<br>`server/core/compactor.py`<br>`server/security/safety.py`<br>`server/main.py` |
| **Riya Sanjay Khialani** *(Audio Pipeline & UI Lead)* | **D12A, Roll 34** | **Live Multimodal Audio & Frontend Services:**<br>• Full-Duplex 16kHz bidirectional Gemini Live audio bridge.<br>• OpenClaw frosted glass UI with AG-UI SSE streaming.<br>• Multi-channel Google Workspace integrations (OAuth2, Gmail, Calendar, Drive).<br>• Audio chunk buffering, PCM downsampling, and echo-cancellation.<br>• Mobile QR authentication bridge and remote control socket. | **30%** | `server/api/routes/audio.py`<br>`server/api/routes/chat.py`<br>`web/src/App.tsx`<br>`web/src/components/`<br>`server/plugins/builtin/email_plugin.py` |
| **Khushi Sadhuramani** *(Knowledge Graph Specialist)* | **D12B, Roll 44** | **Relational Multigraph & GraphRAG Memory:**<br>• NetworkX MultiDiGraph 2-Hop relational memory store.<br>• Contact disambiguation and entity resolution algorithms.<br>• Subgraph serialization and Knapsack prompt optimization.<br>• ChromaDB vector embeddings synchronization.<br>• Interactive D3/Canvas Knowledge Graph UI visualization endpoints. | **18%** | `server/knowledge/graph.py`<br>`server/knowledge/entities.py`<br>`server/knowledge/relations.py`<br>`server/knowledge/vector_store.py`<br>`server/api/routes/knowledge.py` |
| **Ruchika Dingria** *(Proactive Synthesis & QA Specialist)* | **D12B, Roll 70** | **Proactive Inactive Synthesis & Empirical QA:**<br>• Win32 idle state tracker (`GetLastInputInfo`) and touch wake detection.<br>• "Dream & Scout" autonomous sleep-state synthesis and real mail reading.<br>• Affective state modeling and multi-axis emotion classification.<br>• 100-Case empirical benchmark evaluation across GAIA & AgentBench.<br>• IEEE Transactions research paper drafting and Black Book formatting. | **17%** | `server/proactive/idle_tracker.py`<br>`server/proactive/dream_engine.py`<br>`server/sentiment/`<br>`docs/DIONE_IEEE_RESEARCH_PAPER.md`<br>`benchmarks/` |
| **Total Team Allocation** | **Group 19** | **Full System Integration, Testing, Demonstration, and Defense** | **100%** | **Dione Complete System** |

---

## 3. Subsystem Breakdown by Member

### 3.1 Jass Suraj Shivnani (35% — Lead System Architect & Core Autonomous Runtime Lead)
1. **ReAct Execution Engine (`server/core/engine.py`):**
   - Engineered the asynchronous Reason-Act-Observe dispatch loop that coordinates Gemini 2.5/3.5/3.8 function declarations.
   - Designed the deterministic step-budget system preventing small local models from infinite recursion.
   - Built the Tool Self-Healing AST parser that intercepts syntax errors and missing argument exceptions in real-time.
2. **Native Win32 Computer-Use Actuation (`server/hermes_computer_use/`):**
   - Implemented CUA driver bindings interfacing directly with Windows User32 and GDI subsystems.
   - Overcame the Windows Session 0 black-screen limitation via `OpenWindowStationW` and `OpenInputDesktop`.
   - Engineered smooth diagonal hardware drags using `mouse_event` and `SendInput` for UI automation (e.g., drawing in MS Paint).
3. **Poset Lattice Security & Safety Guardrails (`server/security/safety.py`):**
   - Implemented a 5-tier poset permission lattice ($\mathcal{L}_0 \prec \mathcal{L}_1 \prec \mathcal{L}_2 \prec \mathcal{L}_3 \prec \mathcal{L}_4$) enforcing strict confirmation gates for destructive OS operations (e.g., file deletion, shell execution).
   - Enforced the Zero Mock Policy across all backend tools.
4. **Session Compactor (`server/core/compactor.py`):**
   - Authored the context summarization routine that truncates historical turns while preserving crucial entity facts, preventing context buffer blowouts.

### 3.2 Riya Sanjay Khialani (30% — Live Multimodal Audio Pipeline & Frontend Lead)
1. **Gemini Live 16kHz Bidirectional Audio Pipeline (`server/api/routes/audio.py`):**
   - Developed the full-duplex WebSocket bridge between the client browser microphone and Google's Gemini Live bidirectional speech API.
   - Implemented client-side and server-side PCM 16kHz 16-bit linear audio resamplers, eliminating latency bottlenecks.
   - Integrated real-time barge-in detection (echo cancellation and voice activity detection) allowing the user to interrupt Dione mid-speech.
2. **OpenClaw Frosted Glass UI (`web/src/`):**
   - Designed and built the responsive, dark-mode frosted glass web interface in React + TypeScript + TailwindCSS.
   - Implemented the AG-UI Server-Sent Events (SSE) streaming protocol multiplexing tool cards, status pills, and markdown chat bubbles.
   - Created interactive approval modals for high-risk actions (e.g., email dispatch, hardware control).
3. **Multi-Channel Cloud Services & Tool Integrations (`server/plugins/`):**
   - Integrated Google Workspace OAuth2 endpoints (Gmail inbox reading, drafts, Calendar event creation, Google Drive search).
   - Designed the multi-modal tool calling cards that present visual feedback during email composing and calendar planning.

### 3.3 Khushi Sadhuramani (18% — Knowledge Graph & GraphRAG Memory Specialist)
1. **NetworkX 2-Hop Relational Multigraph (`server/knowledge/graph.py`):**
   - Architected the `MultiDiGraph` memory engine maintaining typed nodes (`EntityType`) and directed relationship edges (`RelationType`).
   - Implemented the 2-hop neighbor traversal algorithm returning localized subgraphs for prompt injection within 1.5ms.
2. **Entity Disambiguation & Social Dossiers (`server/knowledge/`):**
   - Developed the fuzzy entity matching and disambiguation engine that flags ambiguous contact names (e.g., "Alex from Figma" vs. "Alex from College") and prompts the agent for clarification.
   - Built the automatic conversational relation extractor capturing commitments, meetings, and project links from raw chat turns.
3. **GraphRAG & Vector Synchronization (`server/knowledge/vector_store.py`):**
   - Synchronized graph nodes with ChromaDB dense vector embeddings for hybrid dense-topological retrieval.
   - Authored the `/api/knowledge/graph` REST endpoints powering the dynamic visual graph canvas.

### 3.4 Ruchika Dingria (17% — Proactive Inactive Synthesis & Quality Assurance Specialist)
1. **Win32 Idle Tracking & Touch-Wake Loop (`server/proactive/idle_tracker.py`):**
   - Integrated native Windows `GetLastInputInfo` system calls to monitor workstation idle time without battery drain.
   - Created the adaptive heartbeat scheduler scaling from 30-second active polling to 900-second deep-sleep cycles.
2. **"Dream & Scout" Proactive Synthesis (`server/proactive/dream_engine.py`):**
   - Developed the background idle engine that activates when the PC is untouched, connects to real Gmail inboxes, extracts urgent emails, and drafts contextual replies.
   - Integrated touch-wake detection that immediately presents pending draft approval cards upon user return.
3. **Affective Persona Modeling (`server/sentiment/`):**
   - Built the multi-axis emotion and urgency detection pipeline prioritizing frustrated or urgent user queries over routine background jobs.
4. **Empirical Benchmarks & Academic Documentation (`docs/`, `benchmarks/`):**
   - Executed and documented the 100-case empirical evaluation across GAIA, AgentBench, and prompt-injection safety suites.
   - Formatted and refined the IEEE Transactions research paper and Mumbai University Black Book according to institutional requirements.

---

## 4. Academic Milestones & Verification Ledger

| Milestone | Target Date | Status | Lead Verifier | Mentor Approval |
| :--- | :---: | :---: | :---: | :---: |
| **Phase I: Architectural Proposal & SRS** | Oct 2025 | Completed | Jass Shivnani | Prof. Geocey Shejy |
| **Phase II: ReAct Loop & Poset Safety Lattice** | Dec 2025 | Completed | Jass Shivnani | Prof. Geocey Shejy |
| **Phase III: Gemini Live 16kHz Audio Bridge & UI** | Jan 2026 | Completed | Riya Khialani | Prof. Geocey Shejy |
| **Phase IV: NetworkX 2-Hop Multigraph & Disambiguation**| Feb 2026 | Completed | Khushi Sadhuramani | Prof. Geocey Shejy |
| **Phase V: Dream & Scout Proactive Synthesis & Idle Engine**| Mar 2026 | Completed | Ruchika Dingria | Prof. Geocey Shejy |
| **Phase VI: 100-Case Empirical Benchmark & Live Defense** | Apr 2026 | Completed | Ruchika Dingria / Jass Shivnani | Prof. Geocey Shejy |

---

## 5. Candidate Sign-Off & Attestation

We hereby certify that the work distribution detailed above reflects the genuine contributions, code authoring, and documentation ownership executed for Capstone Project – I (Group 19).

```
1. _____________________________          2. _____________________________
   Jass Suraj Shivnani                       Riya Sanjay Khialani
   Class D12B, Roll No. 50 (35%)             Class D12A, Roll No. 34 (30%)


3. _____________________________          4. _____________________________
   Khushi Sadhuramani                        Ruchika Dingria
   Class D12B, Roll No. 44 (18%)             Class D12B, Roll No. 70 (17%)


Date: 04 November 2026
Place: VESIT, Chembur, Mumbai

Verified & Forwarded by:
_____________________________
Prof. Geocey Shejy
Project Guide, Assistant Professor
Department of Computer Engineering, VESIT
```
