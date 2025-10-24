#!/usr/bin/env python3
"""
Query classification test.
Verifies that queries are correctly classified as SQL, RAG, or HYBRID.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add parent directory to path to import agent module
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import SQLAgent

print("\n🔬 Testing Classification Fix")
print("="*60)

db_config = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

rag_config = {
    "summaries_dir": os.getenv("SUMMARIES_DIR"),
    "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
    "chroma_db_dir": os.getenv("CHROMA_DB_DIR", "./chroma_db")
}

model_provider = os.getenv("MODEL_PROVIDER", "ollama")

print("Initializing agent...")
agent = SQLAgent(
    db_config=db_config,
    ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    sql_model=os.getenv("SQL_MODEL", "phi3:mini"),
    conversation_model=os.getenv("CONVERSATION_MODEL", "llama3.2:3b"),
    classifier_model=os.getenv("CLASSIFIER_MODEL", "phi3:mini"),
    rag_config=rag_config,
    model_provider=model_provider,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    groq_sql_model=os.getenv("GROQ_SQL_MODEL", "llama-3.1-8b-instant"),
    groq_conversation_model=os.getenv("GROQ_CONVERSATION_MODEL", "llama-3.1-8b-instant"),
    groq_classifier_model=os.getenv("GROQ_CLASSIFIER_MODEL", "llama-3.1-8b-instant")
)

# Focus on the problematic cases
test_queries = [
    # These should be SQL (just want data/names)
    ("Cual es el usuario mas activo?", "SQL"),
    ("Which is the most viewed movie?", "SQL"),
    ("Top 10 movies", "SQL"),
    ("Most active user", "SQL"),
    ("Película más vista", "SQL"),
    
    # These should be RAG (specific content description)
    ("¿De qué trata Aventuras Galácticas?", "RAG"),
    ("What is Terror Nocturno about?", "RAG"),
    
    # These should be HYBRID (ranking + description)
    ("De qué trata la película más vista?", "HYBRID"),
    ("What is the most viewed movie about?", "HYBRID"),
    ("Tell me about the highest rated content", "HYBRID"),
]

print("\nTesting classification:\n")
correct = 0
for query, expected in test_queries:
    state = {"user_query": query}
    result = agent._classify_query(state)
    got = result.get('query_type', 'UNKNOWN')
    status = "✅" if got == expected else "❌"
    if got == expected:
        correct += 1
    print(f"{status} {got:7} (expected {expected:7}) | {query}")

print("\n" + "="*60)
print(f"Score: {correct}/{len(test_queries)}")
print("="*60)
