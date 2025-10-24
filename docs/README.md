# Documentation

Complete documentation for the SQL + RAG AI Agent project.

## 📚 Quick Links

- **[Quick Start Guide](quickstart.md)** - Get up and running in 5 minutes
- **[Architecture Diagrams](architecture/)** - System design and evolution
- **[Model Optimization](model_optimization.md)** - Why we chose phi3:mini

## 🏗️ Architecture

The agent has evolved significantly from a simple SQL translator to a sophisticated multi-modal AI system:

### Evolution Timeline

1. **Initial**: Simple SQL translation (LLM → SQL Tool → Database)
2. **LangGraph**: Multi-node workflow with validation and error handling
3. **Multi-Provider**: Added Groq cloud support alongside Ollama
4. **RAG Integration**: Added document retrieval from PDF summaries
5. **Hybrid Queries**: Combined SQL statistics with RAG descriptions

See [architecture/](architecture/) for detailed diagrams.

## ✨ Features

### Query Types

**SQL Queries** - Database statistics and analytics
```
- "¿Cuántos usuarios tenemos?" / "How many users do we have?"
- "Top 10 contenidos más vistos" / "Top 10 most viewed content"
- "Promedio de rating por género" / "Average rating by genre"
```

**RAG Queries** - Content descriptions from PDFs
```
- "¿De qué trata Aventuras Galácticas?" / "What is Aventuras Galácticas about?"
- "Describe Terror Nocturno" / "Describe Terror Nocturno"
```

**HYBRID Queries** - Combines both
```
- "¿De qué trata la película más vista?" / "What is the most viewed movie about?"
- "Top 5 películas populares y sus descripciones" / "Top 5 popular movies with descriptions"
```

### Model Providers

**Ollama (Local)** - Privacy-focused, offline capable
- SQL: phi3:mini or sqlcoder:7b-q2_k
- Conversation: llama3.2:3b
- Embeddings: nomic-embed-text

**Groq (Cloud)** - Fast inference, no local GPU needed
- All tasks: llama-3.1-8b-instant

Switch providers via `MODEL_PROVIDER` environment variable.

## 🚀 Getting Started

### Prerequisites

- PostgreSQL with streaming database
- Ollama (local) OR Groq API key (cloud)
- Python 3.10+

### Quick Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cd agent
cp .env.example .env
# Edit .env with your settings

# Run CLI
python main.py

# Or run Streamlit GUI
streamlit run streamlit_app.py
```

See [quickstart.md](quickstart.md) for detailed instructions.

## 📊 Technical Stack

| Component | Technology |
|-----------|-----------|
| Orchestration | LangGraph |
| Database | PostgreSQL |
| Vector Store | ChromaDB |
| Models | Ollama / Groq |
| Embeddings | nomic-embed-text |
| GUI | Streamlit |

## 🔒 Security

- SELECT-only queries (read-only access)
- SQL injection prevention
- Query validation before execution
- No dangerous operations (DROP, DELETE, etc.)

## 📝 Model Selection

After extensive testing, **phi3:mini** was chosen as the primary SQL model:
- **4-10x faster** than sqlcoder (6-14s vs 60s+)
- **Excellent accuracy** for PostgreSQL
- **Smaller size** (2.2 GB vs 4.1 GB)
- **Great multilingual support** (Spanish + English)

See [model_optimization.md](model_optimization.md) for full analysis.

## 📖 Additional Resources

- Main project: [../README.md](../README.md)
- Database setup: [../database/README.md](../database/README.md)
- Groq integration: [../agent/GROQ_INTEGRATION.md](../agent/GROQ_INTEGRATION.md)
- Streamlit GUI: [../agent/STREAMLIT_README.md](../agent/STREAMLIT_README.md)

---

*For quick start, see [quickstart.md](quickstart.md)*
