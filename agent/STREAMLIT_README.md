# Streamlit GUI for SQL AI Agent

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install streamlit pandas
```

Or update from requirements.txt:

```bash
pip install -r ../requirements.txt
```

### 2. Run the Application

```bash
streamlit run streamlit_app.py
```

The app will open automatically in your browser at `http://localhost:8501`

## 📋 Features

### Current Implementation (v1)

- ✅ **Chat Interface**: Interactive chat with message history
- ✅ **Query Type Badges**: Visual indicators for SQL, RAG, HYBRID, and AUTO modes
- ✅ **Collapsible SQL**: View generated SQL queries (hidden by default)
- ✅ **Collapsible RAG Sources**: View retrieved documents with similarity scores
- ✅ **Results Table**: View query results in a formatted table
- ✅ **Example Queries**: Click-to-use example questions
- ✅ **Copy Response**: Copy responses to clipboard
- ✅ **Clear Chat**: Reset conversation history
- ✅ **Minimal Design**: Clean, focused interface

### Configuration

The app uses the same `.env` configuration as the CLI:

- Database connection settings
- Model provider (Ollama/Groq)
- Model names
- RAG configuration

No additional configuration needed!

## 🎨 UI Overview

### Main Interface
- **Example Questions**: Pre-defined queries you can click to run
- **Chat History**: All questions and responses
- **Input Box**: Type your questions here

### Response Components
Each response shows:
1. **Natural Language Answer**: Human-friendly response
2. **Query Type Badge**: Shows how the query was processed (SQL/RAG/HYBRID/AUTO)
3. **SQL Query** (expandable): Generated SQL query
4. **RAG Sources** (expandable): Retrieved documents with similarity scores
5. **Query Results** (expandable): Database results in table format
6. **Copy Button**: Copy the response text

### Sidebar
- **Clear Conversation**: Reset chat history
- **Info Panel**: Model provider and message count

## 🔧 Troubleshooting

### App doesn't start
```bash
# Make sure you're in the agent directory
cd /path/to/UCSE-2025-AI-Engineering-TP/agent

# Check that .env file exists
ls -la .env

# Run with verbose output
streamlit run streamlit_app.py --logger.level=debug
```

### Agent fails to initialize
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure Ollama is running (if using local models)
- Verify Groq API key (if using Groq)

### Port already in use
```bash
# Use a different port
streamlit run streamlit_app.py --server.port 8502
```

## 📝 Notes

- The app maintains conversation history in the session (cleared on page refresh)
- All queries are logged to `agent.log`
- Same security restrictions as CLI (SELECT queries only)

## 🔜 Future Enhancements

- [ ] Conversation history persistence (save/load)
- [ ] Export results to CSV/JSON
- [ ] Statistics dashboard
- [ ] Advanced sidebar with model selection
- [ ] Query history search
