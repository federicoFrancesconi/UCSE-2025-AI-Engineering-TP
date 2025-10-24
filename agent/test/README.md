# Test Suite

Automated tests for the AI Agent functionality.

## Test Files

### `test_agent.py`
**Purpose:** Basic agent functionality test  
**Tests:**
- Agent initialization with current configuration
- SQL query generation
- Query execution
- Response formatting

**Usage:**
```bash
cd agent/test
python test_agent.py
```

### `test_rag.py`
**Purpose:** RAG (Retrieval Augmented Generation) functionality  
**Tests:**
1. RAG tool initialization and vector store setup
2. Query classification (SQL/RAG/HYBRID)
3. SQL queries (backward compatibility)
4. RAG queries (document retrieval)

**Usage:**
```bash
cd agent/test
python test_rag.py
```

### `test_groq.py`
**Purpose:** Groq cloud model integration  
**Tests:**
- Groq API connectivity
- Cloud model initialization
- Query processing with Groq models
- Bilingual query support

**Prerequisites:**
- `GROQ_API_KEY` set in `.env`
- `MODEL_PROVIDER=groq` in `.env`

**Usage:**
```bash
cd agent/test
python test_groq.py
```

### `test_classification_fix.py`
**Purpose:** Query classification accuracy  
**Tests:**
- SQL classification (database queries)
- RAG classification (content descriptions)
- HYBRID classification (combined queries)
- Edge cases and problematic queries

**Usage:**
```bash
cd agent/test
python test_classification_fix.py
```

### `test_hybrid_improvement.py`
**Purpose:** HYBRID query functionality  
**Tests:**
1. SQL generation includes `titulo` column
2. Title extraction from SQL results
3. RAG document retrieval by title
4. Combined response generation

**Usage:**
```bash
cd agent/test
python test_hybrid_improvement.py
```

## Running All Tests

```bash
cd agent/test

# Run all tests sequentially
python test_agent.py
python test_rag.py
python test_classification_fix.py
python test_hybrid_improvement.py

# For Groq testing (optional)
python test_groq.py
```

## Test Requirements

All tests require:
- PostgreSQL running with streaming database
- Environment variables configured in `.env`
- Model provider available (Ollama or Groq)

### Ollama Requirements
```bash
# Required models
ollama pull phi3:mini
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

### Groq Requirements
```bash
# Set in .env
MODEL_PROVIDER=groq
GROQ_API_KEY=your_api_key
```

## Expected Results

### All Tests Passing
```
✅ Agent initialized
✅ RAG Tool initialized successfully!
✅ Query classified correctly
✅ SQL query executed
✅ RAG documents retrieved
✅ All tests passed!
```

### Common Issues

**Database Connection Error:**
```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Verify credentials in .env
```

**Ollama Connection Error:**
```bash
# Check Ollama is running
ollama list

# Start if needed
ollama serve
```

**Groq API Error:**
```bash
# Verify API key in .env
echo $GROQ_API_KEY

# Check rate limits
```

**RAG Initialization Error:**
```bash
# Check summaries directory exists
ls ../summaries/

# Verify ChromaDB can be created
ls -la ./chroma_db/
```

## Test Configuration

Tests use the same `.env` configuration as the main agent:

```bash
# Database
DB_HOST=localhost
DB_NAME=streaming
DB_USER=your_user
DB_PASSWORD=your_password

# Model Provider
MODEL_PROVIDER=ollama  # or 'groq'

# Ollama Models
SQL_MODEL=phi3:mini
CONVERSATION_MODEL=llama3.2:3b
CLASSIFIER_MODEL=phi3:mini
EMBEDDING_MODEL=nomic-embed-text

# RAG
SUMMARIES_DIR=../summaries
CHROMA_DB_DIR=./chroma_db

# Groq (if MODEL_PROVIDER=groq)
GROQ_API_KEY=your_key
```

## Adding New Tests

1. Create new test file: `test_feature.py`
2. Add docstring explaining purpose
3. Import agent module:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   from agent import SQLAgent
   ```
4. Use standard configuration pattern
5. Document in this README

---

**For issues, check logs at `../agent.log`**
