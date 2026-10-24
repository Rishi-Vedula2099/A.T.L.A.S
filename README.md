# ATLAS AI-OS (Personal Cognitive Operating System)

> **Quick start:** run `./install` (macOS/Linux) or `install.bat` (Windows) from
> the repo root. The installer detects your OS/arch/GPU, installs Docker if
> needed, generates secrets, builds and starts the stack, waits for it to
> become healthy, and opens the dashboard. No manual setup. See
> [docs/deployment.md](docs/deployment.md) for details.
>
> Already have Docker? `python scripts/generate_env.py && docker compose -f
> infrastructure/docker/docker-compose.yml up -d`.

| What             | Where                                                |
|------------------|------------------------------------------------------|
| Install / run    | `./install` · `install.bat` · [installer/README.md](installer/README.md) |
| Deploy / profiles| [docs/deployment.md](docs/deployment.md)             |
| Operate / backup | [docs/operations.md](docs/operations.md)             |
| Diagnostics      | `python scripts/doctor.py`                           |
| System manual    | [docs/project_manual.md](docs/project_manual.md)     |

---

## Original Vision

Build a JARVIS-like downloadable desktop software that:

- Activates via a wake phrase (e.g., "Hey Atlas")
- Understands voice commands
- Reads and summarizes emails
- Sends images/documents to GPT/Claude for analysis
- Opens and controls applications
- Acts as a secondary brain
- Supports accessibility and disabled users
- Works while the user is busy on another PC

---

# Recommended Name

## A.T.L.A.S

**Autonomous Thinking Learning Assistance System**

Activation Phrase:

> Hey Atlas

Deactivation Phrase:

> Sleep Atlas

---

# Core Architecture

User  
→ Voice Input  
→ Wake Word Detection  
→ Speech-to-Text  
→ Brain Router  
→ Agents + Memory + Automation  
→ LLM Layer  
→ Text-to-Speech  
→ User  

---

# Recommended Tech Stack

## Desktop Application
- Tauri
- Next.js
- TypeScript
- TailwindCSS
- ShadCN

## Speech
- Faster-Whisper
- Porcupine Wake Word

## Agent Framework
- LangGraph

## LLM Layer
- GPT
- Claude
- Gemini
- Local LLMs

## Databases
- PostgreSQL
- Redis
- Qdrant

---

# Core Agents

- Planner Agent
- Research Agent
- Coding Agent
- Vision Agent
- Memory Agent
- Accessibility Agent
- Email Agent
- Browser Agent
- Teams Agent

---

# Core Features

## Email Agent
- Read emails
- Summarize emails
- Draft replies
- Send emails

## Research Agent
- Deep research
- Comparisons
- Documentation understanding

## Coding Agent
- Generate code
- Explain code
- Debug code

## Vision Agent
- OCR
- Screenshot understanding
- Error analysis

## Desktop Agent
- Open apps
- Control browser
- Execute workflows

---

# V2 Features

## Local LLM Mode
- Ollama
- Llama
- Qwen
- Mistral

Benefits:
- Offline mode
- Privacy
- Air-gapped environments

---

## Multi-Agent Orchestration

Using LangGraph

Atlas
- Planner Agent
- Research Agent
- Coding Agent
- Browser Agent
- Vision Agent
- Memory Agent
- Email Agent
- Accessibility Agent

---

## Screen Understanding

Capabilities:
- Read screen content
- Explain errors
- Analyze dashboards
- Understand PDFs

Stack:
- OpenCV
- Pillow
- OCR
- Vision Models

---

## Memory Graph

Traditional Memory:
- Preferences
- Facts

Graph Memory:
- Relationships
- Projects
- Technologies

Stack:
- PostgreSQL
- Qdrant
- Neo4j

---

## Voice Cloning

Modes:
- Jarvis Style
- Friday Style
- Professional
- Friendly
- Custom

Stack:
- Coqui TTS
- XTTS
- ElevenLabs

---

## Autonomous Task Planning

Example:

Prepare Azure Interview

→ Research
→ Notes
→ Schedule
→ Quiz
→ Revision

Stack:
- LangGraph
- Redis
- PostgreSQL

---

## Browser Agent

Capabilities:
- Open websites
- Search content
- Watch videos
- Perform tasks

Stack:
- Playwright

---

## WhatsApp Agent

Capabilities:
- Read messages
- Summarize chats
- Draft responses
- Send messages

---

## Microsoft Teams Agent

Capabilities:
- Read chats
- Meeting summaries
- Action items
- Meeting scheduling

---

## Azure AI Integration

Services:
- Azure OpenAI
- Azure AI Search
- Azure AI Foundry
- Azure AI Speech
- Azure AI Vision
- Azure Machine Learning

---

## Home Automation

Capabilities:
- Lights
- Devices
- IoT Control

Stack:
- Home Assistant
- MQTT

---

# Production Folder Structure

```
atlas-ai-os/
├── apps/
│   ├── desktop-client/
│   └── mobile-client/
├── services/
│   ├── stt-service/
│   ├── tts-service/
│   ├── wakeword-service/
│   ├── memory-service/
│   ├── graph-memory-service/
│   ├── vision-service/
│   ├── planner-service/
│   ├── automation-service/
│   ├── browser-service/
│   ├── email-service/
│   ├── teams-service/
│   ├── whatsapp-service/
│   └── rag-service/
├── agents/
│   ├── orchestrator-agent/
│   ├── planner-agent/
│   ├── research-agent/
│   ├── coding-agent/
│   ├── browser-agent/
│   ├── vision-agent/
│   ├── memory-agent/
│   ├── email-agent/
│   ├── teams-agent/
│   └── accessibility-agent/
├── llm/
│   ├── openai/
│   ├── claude/
│   ├── gemini/
│   └── ollama/
├── databases/
│   ├── postgres/
│   ├── redis/
│   ├── neo4j/
│   └── qdrant/
├── workflows/
├── prompts/
├── integrations/
├── observability/
├── infrastructure/
└── docs/
```

---

# Resume Value

Atlas demonstrates:

- Agentic AI
- Voice AI
- RAG
- Accessibility Engineering
- Desktop Automation
- Computer Vision
- Memory Systems
- Cloud AI
- Azure AI
- Multi-Agent Systems
- Local LLMs
- Enterprise Integrations

Result:

A complete AI Operating System rather than a simple chatbot.
