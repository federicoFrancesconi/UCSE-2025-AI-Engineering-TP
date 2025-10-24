#!/usr/bin/env python3
"""
Basic agent functionality test.
Tests SQL query generation and execution with current configuration.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import agent module
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import SQLAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def test_agent():
    """Test the agent with a simple query."""
    
    print("🧪 Testing SQL AI Agent...\n")
    
    # Database configuration
    db_config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "streaming"),
        "user": os.getenv("DB_USER", "federico"),
        "password": os.getenv("DB_PASSWORD", "password")
    }
    
    # Model provider configuration
    model_provider = os.getenv("MODEL_PROVIDER", "ollama")
    
    # Ollama configuration
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    sql_model = os.getenv("SQL_MODEL", "phi3:mini")
    conversation_model = os.getenv("CONVERSATION_MODEL", "llama3.2:3b")
    classifier_model = os.getenv("CLASSIFIER_MODEL", "phi3:mini")
    
    # Groq configuration (if using Groq)
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_sql_model = os.getenv("GROQ_SQL_MODEL", "llama-3.1-8b-instant")
    groq_conversation_model = os.getenv("GROQ_CONVERSATION_MODEL", "llama-3.1-8b-instant")
    groq_classifier_model = os.getenv("GROQ_CLASSIFIER_MODEL", "llama-3.1-8b-instant")
    
    # RAG configuration (optional)
    rag_config = None
    if os.getenv("SUMMARIES_DIR"):
        rag_config = {
            "summaries_dir": os.getenv("SUMMARIES_DIR"),
            "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
            "chroma_db_dir": os.getenv("CHROMA_DB_DIR", "./chroma_db")
        }
    
    try:
        # Initialize agent
        print(f"1. Initializing agent with {model_provider} provider...")
        agent = SQLAgent(
            db_config=db_config,
            ollama_base_url=ollama_base_url,
            sql_model=sql_model,
            conversation_model=conversation_model,
            classifier_model=classifier_model,
            rag_config=rag_config,
            model_provider=model_provider,
            groq_api_key=groq_api_key,
            groq_sql_model=groq_sql_model,
            groq_conversation_model=groq_conversation_model,
            groq_classifier_model=groq_classifier_model
        )
        print("   ✅ Agent initialized\n")
        
        # Test query
        test_question = "¿Cuántos usuarios tenemos registrados?"
        print(f"2. Testing with question: '{test_question}'")
        
        result = agent.query(test_question)
        
        print("\n3. Results:")
        print("-" * 60)
        
        if result.get("query_type"):
            print(f"\n   🎯 Query Type: {result['query_type']}")
        
        if result.get("sql_query"):
            print(f"\n   📝 Generated SQL:\n   {result['sql_query']}\n")
        
        if result.get("error"):
            print(f"   ❌ Error: {result['error']}\n")
        else:
            print(f"   ✅ Query executed successfully")
            
        if result.get("results") and result["results"].get("success"):
            print(f"   📊 Rows returned: {result['results']['row_count']}")
            
        if result.get("rag_results") and result["rag_results"].get("success"):
            print(f"   📄 RAG documents retrieved: {result['rag_results'].get('count', 0)}")
            
        if result.get("response"):
            response_preview = result['response'][:300] + "..." if len(result['response']) > 300 else result['response']
            print(f"\n   🤖 Agent Response:\n   {response_preview}\n")
        
        print("-" * 60)
        print("\n✅ Test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_agent()
    sys.exit(0 if success else 1)
