# Quick Start Guide

Get the SQL + RAG AI Agent running in 5 minutes.

## Prerequisites

✅ **PostgreSQL** running with streaming database  
✅ **Ollama** (local) OR **Groq API key** (cloud)  
✅ **Python 3.10+**

### Check Prerequisites

```bash
# PostgreSQL
sudo systemctl status postgresql

# Database populated
psql -U your_user -d streaming -c "SELECT COUNT(*) FROM usuarios"

# Ollama (if using local models)
ollama list
# Should show: phi3:mini, llama3.2:3b, nomic-embed-text
```

## Installation

```bash
# 1. Clone and navigate
cd UCSE-2025-AI-Engineering-TP

# 2. Virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database and RAG data
# Database setup
cd database
psql -U your_user -c "CREATE DATABASE streaming"
psql -U your_user -d streaming -f create_streaming_tables.sql
psql -U your_user -d streaming -f insert_sample_data.sql

# Copy example PDFs for RAG functionality
cd ..
mkdir -p summaries
cp database/summaries_examples/*.pdf summaries/

# Optional: Generate additional data with PDF summaries
# cd database
# python generate_fake_data.py --users 100 --content 100 --actors 200 --generate-pdfs
# cd ..

# 5. Configure
cd agent
cd agent
cp .env.example .env
# Edit .env with your settings
```

## Configuration

Edit `agent/.env`:

```bash
# Database
DB_HOST=localhost
DB_NAME=streaming
DB_USER=your_user
DB_PASSWORD=your_password

# RAG - Directory with PDF summaries
SUMMARIES_DIR=../summaries

# Model Provider: 'ollama' or 'groq'
MODEL_PROVIDER=ollama

# Ollama (if MODEL_PROVIDER=ollama)
SQL_MODEL=phi3:mini
CONVERSATION_MODEL=llama3.2:3b
EMBEDDING_MODEL=nomic-embed-text

# Groq (if MODEL_PROVIDER=groq)
GROQ_API_KEY=your_key_here
GROQ_SQL_MODEL=llama-3.1-8b-instant
GROQ_CONVERSATION_MODEL=llama-3.1-8b-instant
```

## Running

### CLI Mode

```bash
cd agent
python main.py
```

### Streamlit GUI

```bash
cd agent
streamlit run streamlit_app.py
```

## Example Queries

**SQL (Database statistics):**
- ¿Cuántos usuarios tenemos? / How many users do we have?
- Top 10 contenidos más vistos / Top 10 most viewed content
- Promedio de rating por género / Average rating by genre
- ¿Cuáles son los usuarios más activos? / Which are the most active users?

**RAG (Content descriptions):**
- ¿De qué trata Aventuras Galácticas? / What is Aventuras Galácticas about?
- Describe Terror Nocturno / Describe Terror Nocturno
- Cuéntame sobre Historia de la Humanidad / Tell me about Historia de la Humanidad

**HYBRID (Both combined):**
- ¿De qué trata la película más vista? / What is the most viewed movie about?
- Top 5 películas populares y sus descripciones / Top 5 popular movies with descriptions
- Mejor película y su descripción / Best rated movie and its description

## Troubleshooting

### Database connection fails
```bash
# Check PostgreSQL
sudo systemctl start postgresql

# Test connection
psql -U your_user -d streaming -c "\dt"
```

### Ollama connection fails
```bash
# Check Ollama
ollama list

# Pull models
ollama pull phi3:mini
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### Module not found
```bash
# Activate venv
source .venv/bin/activate

# Reinstall
pip install -r requirements.txt
```

### Groq API errors
```bash
# Check API key in .env
echo $GROQ_API_KEY

# Set MODEL_PROVIDER=groq in .env
```

## Logs

Check `agent/agent.log` for detailed information:

```bash
# Watch logs
tail -f agent/agent.log

# Find errors
grep ERROR agent/agent.log
```

## Next Steps

- See [README.md](README.md) for full documentation
- Check [architecture/](architecture/) for system design
- Read [model_optimization.md](model_optimization.md) for model details

---

**Need help?** Check the logs or review [README.md](README.md)
