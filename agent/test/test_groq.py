#!/usr/bin/env python3
"""
Groq integration test.
Verifies that Groq cloud models work correctly as an alternative to Ollama.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import agent module
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import SQLAgent

# Load environment variables
load_dotenv()

def test_groq_integration():
    """Test that Groq models work correctly."""
    
    print("🧪 Testing Groq Integration\n")
    
    # Load configuration
    db_config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }
    
    # RAG configuration (optional)
    rag_config = None
    if os.getenv("SUMMARIES_DIR"):
        rag_config = {
            "summaries_dir": os.getenv("SUMMARIES_DIR"),
            "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
            "chroma_db_dir": os.getenv("CHROMA_DB_DIR", "./chroma_db")
        }
    
    model_provider = "groq"
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_sql_model = os.getenv("GROQ_SQL_MODEL", "llama-3.1-8b-instant")
    groq_conversation_model = os.getenv("GROQ_CONVERSATION_MODEL", "llama-3.1-8b-instant")
    groq_classifier_model = os.getenv("GROQ_CLASSIFIER_MODEL", "llama-3.1-8b-instant")
    
    if not groq_api_key:
        print("❌ Error: GROQ_API_KEY not found in environment")
        sys.exit(1)
    
    print(f"📋 Configuration:")
    print(f"   Provider: {model_provider}")
    print(f"   SQL Model: {groq_sql_model}")
    print(f"   Conversation Model: {groq_conversation_model}")
    print(f"   Classifier Model: {groq_classifier_model}\n")
    
    try:
        # Initialize agent with Groq
        print("🔧 Initializing agent with Groq...")
        agent = SQLAgent(
            db_config=db_config,
            ollama_base_url="http://localhost:11434",  # Not used with Groq
            sql_model="",  # Not used with Groq
            conversation_model="",  # Not used with Groq
            classifier_model="",  # Not used with Groq
            rag_config=rag_config,
            model_provider=model_provider,
            groq_api_key=groq_api_key,
            groq_sql_model=groq_sql_model,
            groq_conversation_model=groq_conversation_model,
            groq_classifier_model=groq_classifier_model
        )
        print("✅ Agent initialized successfully!\n")
        
        # Test queries
        test_queries = [
            "¿Cuántos usuarios tenemos?",
            "How many users do we have?",
            "Muestra los 5 contenidos más vistos",
            "Show top 5 most viewed content"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{'='*70}")
            print(f"📝 Test {i}: {query}")
            print('='*70)
            
            result = agent.query(query)
            
            print(f"\n🔍 Query Type: {result.get('query_type', 'N/A')}")
            
            if result.get('sql_query'):
                print(f"\n💾 Generated SQL:")
                print(f"   {result['sql_query']}")
            
            if result.get('response'):
                print(f"\n🤖 Response:")
                print(f"   {result['response']}")
            
            if result.get('error'):
                print(f"\n❌ Error: {result['error']}")
        
        print("\n" + "="*70)
        print("✅ All tests completed successfully!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    test_groq_integration()
