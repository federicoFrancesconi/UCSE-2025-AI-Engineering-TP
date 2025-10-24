# Groq Integration Guide

## Overview
The agent now supports both **local Ollama models** and **remote Groq cloud models**. You can easily switch between them using an environment variable.

## Configuration

### Environment Variables (`.env` file)

```bash
# Model Provider: 'ollama' for local models, 'groq' for remote cloud models
MODEL_PROVIDER=groq

# Groq API Key (required when MODEL_PROVIDER=groq)
GROQ_API_KEY=your_groq_api_key_here

# Groq Model Configuration (used when MODEL_PROVIDER=groq)
GROQ_SQL_MODEL=llama-3.1-8b-instant
GROQ_CONVERSATION_MODEL=llama-3.1-8b-instant
GROQ_CLASSIFIER_MODEL=llama-3.1-8b-instant

# Ollama Configuration (used when MODEL_PROVIDER=ollama)
OLLAMA_BASE_URL=http://localhost:11434
SQL_MODEL=phi3:mini
CONVERSATION_MODEL=llama3.2:3b
CLASSIFIER_MODEL=phi3:mini
```

## Switching Between Providers

### Use Groq (Cloud - Fast)
Set in your `.env` file:
```bash
MODEL_PROVIDER=groq
```

### Use Ollama (Local - Private)
Set in your `.env` file:
```bash
MODEL_PROVIDER=ollama
```

## Benefits of Each Provider

### Groq (Cloud)
- ✅ **Much faster inference** - responses in seconds
- ✅ **No local GPU required**
- ✅ **No model downloads**
- ✅ **Consistent performance**
- ❌ Requires internet connection
- ❌ API calls are rate-limited

### Ollama (Local)
- ✅ **Complete privacy** - data stays local
- ✅ **No rate limits**
- ✅ **Works offline**
- ✅ **Free**
- ❌ Slower inference (depends on hardware)
- ❌ Requires model downloads
- ❌ Needs adequate RAM/GPU

## Testing

Run the Groq integration test:
```bash
python test_groq.py
```

Or run the full agent:
```bash
python main.py
```

## Model Information

### Groq Models Used
- **llama-3.1-8b-instant**: Fast, efficient model for all tasks
  - Classification: Determines query type (SQL/RAG/HYBRID)
  - SQL Generation: Converts natural language to SQL
  - Response Generation: Creates natural language responses

### Task-Specific Optimizations
- **Classification**: Temperature=0, max_tokens=10 (fast, deterministic)
- **SQL Generation**: Temperature=0, max_tokens=500 (precise, structured)
- **Response Generation**: Temperature=0.7, max_tokens=1000 (natural, creative)

## Implementation Details

The integration preserves all existing Ollama functionality while adding Groq as an alternative:

1. **Agent Initialization**: Accepts `model_provider` parameter
2. **Model Creation**: Automatically selects appropriate LLM class (Ollama vs ChatGroq)
3. **Prompt Formatting**: Optimized for each provider's requirements
4. **Response Handling**: Handles both string responses (Ollama) and message objects (Groq)

No code changes needed to switch - just update the environment variable!
