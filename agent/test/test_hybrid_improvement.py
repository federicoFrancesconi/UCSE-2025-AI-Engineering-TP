#!/usr/bin/env python3
"""
HYBRID query test.
Tests that HYBRID queries:
1. Generate SQL with titulo column
2. Extract titles from SQL results
3. Retrieve RAG documents for those specific titles
4. Combine both in the final response
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

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'streaming'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

# RAG configuration
rag_config = {
    'summaries_dir': os.getenv('SUMMARIES_DIR', '../summaries'),
    'embedding_model': os.getenv('EMBEDDING_MODEL', 'nomic-embed-text'),
    'chroma_db_dir': os.getenv('CHROMA_DB_DIR', './chroma_db')
}

# Model provider
model_provider = os.getenv('MODEL_PROVIDER', 'ollama')

# Initialize agent
agent = SQLAgent(
    db_config=db_config,
    ollama_base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
    sql_model=os.getenv('SQL_MODEL', 'phi3:mini'),
    conversation_model=os.getenv('CONVERSATION_MODEL', 'llama3.2:3b'),
    classifier_model=os.getenv('CLASSIFIER_MODEL', 'phi3:mini'),
    rag_config=rag_config,
    model_provider=model_provider,
    groq_api_key=os.getenv('GROQ_API_KEY'),
    groq_sql_model=os.getenv('GROQ_SQL_MODEL', 'llama-3.1-8b-instant'),
    groq_conversation_model=os.getenv('GROQ_CONVERSATION_MODEL', 'llama-3.1-8b-instant'),
    groq_classifier_model=os.getenv('GROQ_CLASSIFIER_MODEL', 'llama-3.1-8b-instant')
)

print("="*80)
print("Testing HYBRID Query Improvements")
print("="*80)

# Test cases
test_queries = [
    "¿De qué trata la película más vista?",
    "What is the most viewed movie about?",
    "Tell me about the top 3 most popular películas",
]

for i, query in enumerate(test_queries, 1):
    print(f"\n{'='*80}")
    print(f"Test {i}/{len(test_queries)}: {query}")
    print(f"{'='*80}")
    
    try:
        # Process query
        result = agent.query(query)
        
        print(f"\n✓ Query Type: {result['query_type']}")
        
        if result['query_type'] == 'HYBRID':
            print(f"\n✓ SQL Query Generated:")
            print(f"  {result['sql_query']}")
            
            # Check if 'titulo' is in the SQL query
            if 'titulo' in result['sql_query'].lower():
                print(f"\n✓ SQL includes 'titulo' column ✓")
            else:
                print(f"\n✗ WARNING: SQL does NOT include 'titulo' column!")
            
            # Check SQL results
            if result['results'].get('success'):
                sql_data = result['results'].get('results', [])
                print(f"\n✓ SQL Results ({len(sql_data)} rows):")
                for row in sql_data[:3]:  # Show first 3
                    print(f"  - {row}")
                
                # Check if titulo is in results
                if sql_data and 'titulo' in sql_data[0]:
                    print(f"\n✓ Results contain 'titulo' field ✓")
                else:
                    print(f"\n✗ WARNING: Results do NOT contain 'titulo' field!")
            
            # Check RAG results
            if result['rag_results'].get('success'):
                rag_count = result['rag_results'].get('count', 0)
                metadatas = result['rag_results'].get('metadatas', [])
                print(f"\n✓ RAG Documents Retrieved: {rag_count}")
                for meta in metadatas:
                    print(f"  - {meta.get('title', 'Unknown')}")
            else:
                print(f"\n✗ RAG retrieval failed: {result['rag_results'].get('error', 'Unknown error')}")
            
            # Final response
            print(f"\n✓ Final Response:")
            response_preview = result['response'][:300] + "..." if len(result['response']) > 300 else result['response']
            print(f"  {response_preview}")
        else:
            print(f"\n✗ Query was classified as {result['query_type']}, not HYBRID!")
        
        if result.get('error'):
            print(f"\n✗ Error: {result['error']}")
    
    except Exception as e:
        print(f"\n✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*80}")
print("Test Complete")
print("="*80)
