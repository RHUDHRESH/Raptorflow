# RaptorFlow Backend

The intelligent core of the RaptorFlow Marketing Operating System.

## ≡ƒÅù∩╕Å Architecture

The backend is built with **FastAPI** and orchestrates complex AI workflows using **LangGraph** and **Vertex AI**.

### Key Components

- **Cognitive Engine**: Stateful LangGraph application for generating comprehensive business context.
  - Located in `backend/services/business_context_graph.py`.
  - Uses **Gemini 1.5 Pro** for deep analysis.
  - Implements nodes for Profile, Market, Competitors, SWOT, PESTEL, Value Chain, Brand Archetypes, and Messaging.
- **Service Layer**: Coordinates between the API and the cognitive engine.
- **Infrastructure**:
  - **Redis (Upstash)**: Used for connection pooling, rate limiting, and state management.
  - **Google Cloud Storage**: For document storage and evidence vault.
  - **Vertex AI**: Main AI provider.

## ≡ƒÜÇ Getting Started

### Prerequisites

- Python 3.12+
- GCP Project with Vertex AI enabled
- Upstash Redis account

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### Running Tests

```bash
pytest backend/tests/unit
```

### ≡ƒºá Cognitive Engine (LangGraph)
- **Stateful Workflows**: Multi-node business analysis using LangGraph.
- **Deep Insights**: Automated SWOT, PESTEL, Value Chain, and Brand Archetype analysis.
- **Enhanced ICPs**: AI-generated behavioral architecture for target segments.
- **Safe Generation**: Strict Pydantic validation with safe fallbacks and retry logic.
- **Model**: Gemini 1.5 Pro via Vertex AI.

### ≡ƒôü Document Service
- **Secure Storage**: Integrated with Google Cloud Storage.
- **Safe Processing**: libmagic-based validation and virus scanning (optional).
- **Asynchronous**: Fully async/await implementation for high performance.
