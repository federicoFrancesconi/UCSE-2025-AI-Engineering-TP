# UCSE-2025-AI-Engineering-TP

Final Project for the Advanced AI Topics course at UCSE 2025.

## 📋 Project Description

AI Agent system based on LangGraph that translates natural language questions into SQL queries and retrieves content descriptions from PDF documents for a streaming platform database.

### Key Features

🤖 **Multi-Modal AI Agent**
- SQL query generation from natural language
- RAG (Retrieval Augmented Generation) for content descriptions
- Hybrid queries combining database statistics with document context

🔄 **Flexible Model Providers**
- **Ollama** (Local) - Privacy-focused, offline capable
- **Groq** (Cloud) - Fast inference, no GPU required

🎯 **Three Query Types**
- **SQL**: Database analytics ("How many users?", "Top 10 content")
- **RAG**: Content information ("What is Movie X about?")
- **HYBRID**: Combined queries ("What is the most viewed movie about?")

## 🏗️ Project Structure

```
UCSE-2025-AI-Engineering-TP/
├── agent/                          # AI Agent Module
│   ├── agent.py                   # LangGraph implementation
│   ├── sql_tool.py                # SQL Tool
│   ├── rag_tool.py                # RAG Tool (ChromaDB + embeddings)
│   ├── main.py                    # CLI interface
│   ├── streamlit_app.py           # Web GUI
│   ├── test/                      # Test scripts
│   ├── chroma_db/                 # Vector store (auto-generated)
│   ├── GROQ_INTEGRATION.md        # Groq setup guide
│   ├── STREAMLIT_README.md        # GUI documentation
│   └── .env.example               # Configuration template
├── database/                       # Database Module
│   ├── create_streaming_tables.sql
│   ├── insert_sample_data.sql
│   ├── generate_fake_data.py
│   ├── summaries_examples/        # Example PDFs (30 files) for RAG testing
│   └── README.md
├── docs/                          # Documentation
│   ├── README.md                  # Documentation index
│   ├── quickstart.md              # Quick start guide
│   ├── model_optimization.md      # Model selection analysis
│   └── architecture/              # Architecture diagrams
├── summaries/                     # PDF content summaries (copy from database/summaries_examples/)
├── requirements.txt               # Project dependencies
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

1. **PostgreSQL** installed and running
2. **Model Provider** (choose one):
   - **Ollama** (local) with models: `phi3:mini`, `llama3.2:3b`, `nomic-embed-text`
   - **Groq** (cloud) with API key
3. **Python 3.10+**

### Installation

```bash
# 1. Clone repository
git clone https://github.com/federicoFrancesconi/UCSE-2025-AI-Engineering-TP.git
cd UCSE-2025-AI-Engineering-TP

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
psql -U postgres -c "CREATE DATABASE streaming"
psql -U postgres -d streaming -f database/create_streaming_tables.sql
psql -U postgres -d streaming -f database/insert_sample_data.sql

# Optional: Generate more fake data (with PDF summaries)
# python database/generate_fake_data.py --users 1000 --content 500 --generate-pdfs

# 5. Setup RAG data (copy example PDFs for content descriptions)
mkdir -p summaries
cp database/summaries_examples/*.pdf summaries/

# 6. Configure environment
cd agent
cp .env.example .env
# Edit .env with your credentials and model provider

# 7. Run the agent
python main.py
# Or run GUI: streamlit run streamlit_app.py
```

### Configuration

Edit `agent/.env`:

```bash
# Database
DB_HOST=localhost
DB_NAME=streaming
DB_USER=your_user
DB_PASSWORD=your_password

# RAG - Directory with PDF summaries (default: ../summaries)
SUMMARIES_DIR=../summaries

# Model Provider: 'ollama' or 'groq'
MODEL_PROVIDER=ollama

# Ollama Configuration (if MODEL_PROVIDER=ollama)
SQL_MODEL=phi3:mini
CONVERSATION_MODEL=llama3.2:3b
EMBEDDING_MODEL=nomic-embed-text

# Groq Configuration (if MODEL_PROVIDER=groq)
GROQ_API_KEY=your_groq_api_key
GROQ_SQL_MODEL=llama-3.1-8b-instant
GROQ_CONVERSATION_MODEL=llama-3.1-8b-instant
```

## 📚 Documentation

- **[Quick Start Guide](docs/quickstart.md)** - Get running in 5 minutes
- **[Documentation Index](docs/README.md)** - Complete documentation
- **[Model Optimization](docs/model_optimization.md)** - Why we chose phi3:mini
- **[Architecture Diagrams](docs/architecture/)** - System design evolution
- **[Groq Integration](agent/GROQ_INTEGRATION.md)** - Cloud model setup
- **[Streamlit GUI](agent/STREAMLIT_README.md)** - Web interface guide

## 🎯 Features

### Query Processing
- ✅ Natural language to SQL translation (English & Spanish)
- ✅ Multi-node LangGraph workflow
- ✅ Intelligent query classification (SQL/RAG/HYBRID)
- ✅ SQL validation (SELECT-only queries)
- ✅ Database schema awareness
- ✅ Vector search in PDF documents
- ✅ Hybrid queries combining SQL + RAG

### Model Support
- ✅ Multi-provider architecture (Ollama/Groq)
- ✅ Automatic prompt adaptation per model
- ✅ LLM-based or embedding-based classification
- ✅ Optimized for phi3:mini (6-14s response time)

### User Experience
- ✅ CLI interface with rich formatting
- ✅ Streamlit web GUI
- ✅ Formatted table output
- ✅ Natural language responses
- ✅ Query type indicators
- ✅ Comprehensive logging

### Security
- ✅ Read-only database access
- ✅ SQL injection prevention
- ✅ Query validation before execution
- ✅ Dangerous operation blocking

## 💡 Usage Examples

### SQL Queries (Database Analytics)

```
English:
- "How many users do we have?"
- "Top 10 most viewed content"
- "Average rating by genre"

Spanish:
- "¿Cuántos usuarios tenemos?"
- "Top 10 contenidos más vistos"
- "Promedio de rating por género"
```

### RAG Queries (Content Descriptions)

```
English:
- "What is Aventuras Galácticas about?"
- "Describe Terror Nocturno"

Spanish:
- "¿De qué trata Aventuras Galácticas?"
- "Cuéntame sobre Terror Nocturno"
```

### HYBRID Queries (Combined)

```
English:
- "What is the most viewed movie about?"
- "Top 5 popular movies with descriptions"

Spanish:
- "¿De qué trata la película más vista?"
- "Top 5 películas populares y sus descripciones"
```

## � Example Output

```
💬 Your question: What is the most viewed movie about?

🤔 Thinking...

Query Type: HYBRID

======================================================================

📝 Generated SQL:
   SELECT c.titulo, COUNT(*) AS views
   FROM contenido c
   JOIN visualizaciones v ON c.id_contenido = v.id_contenido
   WHERE c.tipo = 'Película'
   GROUP BY c.titulo
   ORDER BY views DESC
   LIMIT 1

🤖 Response:
   The most viewed movie is "La Última Frontera" with 2 views.
   
   This 2001 action-drama follows a group of astronauts on humanity's
   first mission beyond our solar system. When their ship encounters
   a mysterious anomaly, they must make impossible choices...

📊 Query Results:
   ✓ Query returned 1 row(s):
   +-------------------+-------+
   | titulo            | views |
   +===================+=======+
   | La Última Frontera|     2 |
   +-------------------+-------+

📄 Retrieved Documents:
   ✓ La_Última_Frontera.pdf (similarity: 1.00)

======================================================================
```

## 🔧 Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Orchestration | LangGraph | 0.2.28 |
| LLM Framework | LangChain | 0.3.1 |
| SQL Model (Primary) | Ollama phi3:mini | 2.2 GB |
| SQL Model (Alt) | Ollama sqlcoder:7b-q2_k | 3.1 GB |
| Conversation | Ollama llama3.2:3b | 2.0 GB |
| Cloud Alternative | Groq llama-3.1-8b-instant | - |
| Embeddings | nomic-embed-text | 270 MB |
| Database | PostgreSQL | - |
| Vector Store | ChromaDB | 0.4.24 |
| GUI | Streamlit | - |
| SQL Parsing | sqlparse | - |
| Table Formatting | tabulate | - |

## 🎓 Model Selection

After extensive testing, **phi3:mini** was chosen as the primary SQL model:

| Model | Speed | Size | Quality | Multilingual |
|-------|-------|------|---------|--------------|
| phi3:mini ⭐ | 6-14s | 2.2 GB | ⭐⭐⭐⭐ | ✅ |
| sqlcoder:7b-q2_k | 14-22s | 3.1 GB | ⭐⭐⭐⭐⭐ | ✅ |
| sqlcoder:7b | 60s+ | 4.1 GB | ⭐⭐⭐⭐⭐ | ✅ |

**Advantages of phi3:mini:**
- 4-10x faster than sqlcoder:7b
- Excellent PostgreSQL syntax
- Great Spanish support
- Smaller memory footprint

See [docs/model_optimization.md](docs/model_optimization.md) for detailed analysis.

## 🏛️ Architecture

The system uses a sophisticated LangGraph workflow:

```
User Query
    ↓
[Classify Query] → SQL / RAG / HYBRID
    ↓
[SQL Path]              [RAG Path]
Generate SQL            Search Vector Store
Execute Query           Retrieve PDFs
    ↓                       ↓
[Format Response] ← Merge Results
    ↓
Natural Language Response
```

See [docs/architecture/](docs/architecture/) for detailed diagrams.

## 🛡️ Security

- **Read-Only Access**: Only SELECT statements allowed
- **SQL Validation**: Queries parsed and validated before execution
- **Injection Prevention**: Multi-layer protection against SQL injection
- **Operation Blocking**: DROP, DELETE, INSERT, UPDATE blocked
- **Single Statement**: Only one SQL statement per query

## 🧪 Testing

```bash
# Run all tests
cd agent/test
python test_agent.py
python test_rag.py
python test_groq.py

# Run specific test
python test_hybrid_improvement.py
```

## 📝 Project Info

**Course**: Tópicos Avanzados de IA  
**Institution**: UCSE (Universidad Católica de Santiago del Estero)  
**Year**: 2025  
**Author**: Federico Francesconi

## 📄 License

Academic project - UCSE 2025 - Advanced AI Topics

---

**For detailed setup instructions, see [docs/quickstart.md](docs/quickstart.md)**  
**For complete documentation, see [docs/README.md](docs/README.md)**
