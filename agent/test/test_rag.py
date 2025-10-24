#!/usr/bin/env python3
"""
RAG functionality test suite.
Tests RAG initialization, query classification, and document retrieval.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path to import agent module
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import SQLAgent

def get_agent_config():
    """Get standard agent configuration."""
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
    
    return db_config, rag_config

def create_agent():
    """Create agent with current configuration."""
    db_config, rag_config = get_agent_config()
    model_provider = os.getenv("MODEL_PROVIDER", "ollama")
    
    return SQLAgent(
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

def test_rag_initialization():
    """Test that RAG tool initializes correctly."""
    print("\n" + "="*70)
    print("TEST 1: RAG Tool Initialization")
    print("="*70)
    
    try:
        agent = create_agent()
        
        if agent.rag_tool:
            print("✅ RAG Tool initialized successfully!")
            print(f"   Documents in vector store: {agent.rag_tool.collection.count()}")
            return True
        else:
            print("❌ RAG Tool not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_classification():
    """Test query classification."""
    print("\n" + "="*70)
    print("TEST 2: Query Classification")
    print("="*70)
    
    agent = create_agent()
    
    test_queries = [
        ("¿Cuántos usuarios hay?", "SQL"),
        ("How many users do we have?", "SQL"),
        ("¿De qué trata Aventuras Galácticas?", "RAG"),
        ("What is Aventuras Galácticas about?", "RAG"),
        ("¿De qué trata la película más vista?", "HYBRID"),
        ("What is the most viewed movie about?", "HYBRID"),
    ]
    
    print("\nTesting query classification:")
    all_correct = True
    for query, expected_type in test_queries:
        state = {"user_query": query}
        result = agent._classify_query(state)
        classified_type = result.get('query_type', 'UNKNOWN')
        is_correct = classified_type == expected_type
        all_correct = all_correct and is_correct
        status = "✅" if is_correct else "⚠️"
        print(f"{status} '{query[:50]}...' → {classified_type} (expected: {expected_type})")
    
    return all_correct


def test_sql_query():
    """Test a SQL-only query."""
    print("\n" + "="*70)
    print("TEST 3: SQL Query")
    print("="*70)
    
    agent = create_agent()
    
    query = "¿Cuántos usuarios tenemos?"
    print(f"\nQuery: {query}")
    print("Processing...")
    
    try:
        result = agent.query(query)
        print(f"\n✅ Query completed!")
        print(f"   Query Type: {result.get('query_type')}")
        print(f"   SQL: {result.get('sql_query')}")
        print(f"   Response: {result.get('response')[:200]}...")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_query():
    """Test a RAG-only query."""
    print("\n" + "="*70)
    print("TEST 4: RAG Query")
    print("="*70)
    
    agent = create_agent()
    
    query = "¿De qué trata Aventuras Galácticas?"
    print(f"\nQuery: {query}")
    print("Processing...")
    
    try:
        result = agent.query(query)
        print(f"\n✅ Query completed!")
        print(f"   Query Type: {result.get('query_type')}")
        print(f"   Response: {result.get('response')[:300]}...")
        if result.get('rag_results'):
            print(f"   Retrieved {result['rag_results'].get('count', 0)} documents")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 RAG FUNCTIONALITY TEST SUITE")
    print("="*70)
    
    tests = [
        test_rag_initialization,
        test_query_classification,
        test_sql_query,
        test_rag_query,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
    else:
        print("⚠️  Some tests failed")
    
    print("="*70 + "\n")
