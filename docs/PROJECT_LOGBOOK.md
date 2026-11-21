# 📓 Capstone Project Logbook

**Department of Computer Engineering**  
**Vivekanand Education Society's Institute of Technology (VESIT)**  
*(An Autonomous Institute Affiliated to University of Mumbai)*  

---

## 📌 Project Information

* **Project Title:** Dione: A Privacy-Preserving Local Large Action Model (LAM) Orchestration Engine for Ambient Personal Assistance
* **Project Group ID:** Group 19 (A.Y. 2026–2027)
* **Semester:** Semester VII & VIII (B.E. Computer Engineering)
* **Project Guide / Mentor:** Dr. Geocey Shejy (Associate Professor, Department of Computer Engineering)
* **Head of Department:** Dr. (Mrs.) Nupur Giri

---

## 👥 Student Cohort & Roll Numbers

| Sr. No. | Student Name | Roll No. | Division | Core Responsibilities |
| :---: | :--- | :---: | :---: | :--- |
| 1 | **Jass Shivnani** *(Lead)* | 50 | D17B | System Architecture, ReAct Loop Core, Win32 CUA Actuator |
| 2 | **Riya Khialani** | 34 | D17A | Sovereign Workspace UI, Multimodal Communications, Tool Adapters |
| 3 | **Khushi Sadhuramani** | 44 | D17B | Deterministic Safety Kernel, 5-Tier Permission Lattice, Audit Logging |
| 4 | **Ruchika Dingria** | 70 | D17B | Dual-Tier Memory (NetworkX Graph + ChromaDB), Evaluation Benchmarks |

---

## 🗓️ Weekly Meeting & Milestone Progress Ledger

### Milestone 1: Problem Identification & Literature Survey
* **Dates:** 15th July 2026 – 31st July 2026
* **Objectives:** Analyze architectural bottlenecks in contemporary cloud-centric personal assistants (Siri, Alexa, Copilot) regarding local privacy, action execution, and memory degradation.
* **Activities Completed:**
  - Surveyed 24 foundational research papers spanning Large Action Models (LAM), ReAct loops, and Computer-Use Agents (Anthropic, OSWorld, GAIA).
  - Drafted formal problem definition and capstone project scope.
  - Formulated Group 19 work breakdown structure and component separation.
* **Guide Remarks & Guidance:** Focus on client-side sovereignty and ensure privacy guarantees are mathematically and architecturally verifiable. Approved for Stage 1.

---

### Milestone 2: System Architecture Design & Formal Modeling
* **Dates:** 1st August 2026 – 20th August 2026
* **Objectives:** Formulate runtime architecture, bounded reasoning loop, and dual-tier memory subsystem.
* **Activities Completed:**
  - Designed component architecture separating the LLM Reasoning Core from deterministic execution guards.
  - Modeled the Dual-Tier Memory Subsystem: NetworkX MultiDiGraph for 2-hop relational fact lookup combined with ChromaDB MiniLM-L6 vector embeddings for fuzzy conversational context.
  - Defined the 5-tier safety permission lattice (Read, Write, Network, System Actuation, Elevated Denial).
* **Guide Remarks & Guidance:** Decouple safety verification from the stochastic LLM output to prevent prompt injection escapes. Architecture approved.

---

### Milestone 3: Core Reasoning Loop & Safety Kernel Implementation
* **Dates:** 21st August 2026 – 15th September 2026
* **Objectives:** Implement backend engine in Python FastAPI and build the safety interceptor.
* **Activities Completed:**
  - Built bounded ReAct execution cycle (`server/app/agent/`) with strict step-budget constraints.
  - Implemented the Deterministic Safety Kernel (`server/app/security/`) with cryptographic SQLite audit logging (`audit_ledger.db`).
  - Implemented hard-coded denial filters for sensitive OS directories (`System32`, `Windows`, `Registry`, credential caches).
* **Guide Remarks & Guidance:** Ensure all intercepted actions produce structured rejection explanations in the user telemetry drawer.

---

### Milestone 4: Native Win32 Computer-Use Actuator (CUA)
* **Dates:** 16th September 2026 – 5th October 2026
* **Objectives:** Build client-side desktop automation adapter using native Windows APIs.
* **Activities Completed:**
  - Developed coordinate normalization pipeline translating normalized $1000 \times 1000$ spatial grids to physical monitor pixel coordinates across variable DPI scaling.
  - Built Win32 mouse/keyboard injection adapters via `ctypes` and `pywin32`.
  - Implemented autonomous GUI interaction workflows (tested on MS Paint geometric rendering and Windows Settings).
* **Guide Remarks & Guidance:** Include fallback mechanisms when targeted UI elements are occluded or minimized.

---

### Milestone 5: Sovereign Workspace Frontend & Real-Time Telemetry
* **Dates:** 6th October 2026 – 25th October 2026
* **Objectives:** Create responsive client workspace with live execution traces and state visualization.
* **Activities Completed:**
  - Built React/Vite web workspace with dark-mode glassmorphic aesthetics.
  - Implemented Server-Sent Events (SSE) telemetry feed streaming live agent thoughts, tool calls, and hardware resource utilization.
  - Built visual Knowledge Graph Explorer rendering live entity nodes and relational subgraphs.
* **Guide Remarks & Guidance:** Ensure interface clearly displays model status, active memory nodes, and explicit user-confirmation modals for elevated actions.

---

### Milestone 6: Empirical Benchmarking & 100-Case Evaluation
* **Dates:** 26th October 2026 – 10th November 2026
* **Objectives:** Perform comprehensive quantitative evaluation across latency, memory recall, and safety enforcement.
* **Activities Completed:**
  - Executed 100 automated test scenarios across diverse task categories (desktop automation, web research, email delivery, system telemetry).
  - Recorded empirical results: **1.158 ms** mean 2-hop graph traversal latency, **93.2%** multi-session fact recall at Session 5, **75%** prompt token reduction via relational graph retrieval, and **100%** interception of unauthorized system modifications.
  - Verified 20/20 unit and integration tests passing.
* **Guide Remarks & Guidance:** Consolidate empirical distributions into LaTeX comparative tables and radar capability figures for the final paper and Black Book.

---

### Milestone 7: Academic Research Paper & Black Book Documentation
* **Dates:** 11th November 2026 – 20th November 2026
* **Objectives:** Finalize departmental Black Book report, research paper, and demonstration video.
* **Activities Completed:**
  - Authored IEEE-compliant research paper and submitted for peer review (ID: `EAI-26-0653`).
  - Formatted and generated the final Capstone Project Black Book (Chapters 1 to 8 + Front Matter + Appendix I) adhering to University of Mumbai guidelines.
  - Recorded and produced the 1m 35s synchronized demonstration video with studio neural audio.
  - Deployed source code, test suites, and documentation to the official VESIT repository (`Project-CMPN-VESIT/2026-27-BE-019`).
* **Guide Remarks & Guidance:** Deliverables reviewed and approved for the Capstone Oral Examination on 21st November 2026.

---

## ✍️ Verification & Certification Sign-Off

* **Project Guide:** Dr. Geocey Shejy (Department of Computer Engineering, VESIT)
* **Date of Evaluation:** 21st November 2026
* **Examination:** Final Capstone Project Oral Examination (B.E. Computer Engineering)
