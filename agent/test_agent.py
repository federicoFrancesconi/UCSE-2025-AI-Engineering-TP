#!/usr/bin/env python3
"""
Quick test script to verify the agent is working correctly.
"""

import os
import sys
import logging
from dotenv import load_dotenv
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
    
    # Ollama configuration
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    sql_model = os.getenv("SQL_MODEL", "sqlcoder:7b")
    conversation_model = os.getenv("CONVERSATION_MODEL", "llama3.2:3b")
    
    try:
        # Initialize agent
        print("1. Initializing agent...")
        agent = SQLAgent(
            db_config=db_config,
            ollama_base_url=ollama_base_url,
            sql_model=sql_model,
            conversation_model=conversation_model
        )
        print("   ✅ Agent initialized\n")
        
        # Test query
        test_question = "¿Cuántos usuarios tenemos registrados?"
        print(f"2. Testing with question: '{test_question}'")
        
        result = agent.query(test_question)
        
        print("\n3. Results:")
        print("-" * 60)
        
        # Debug: print full result
        print(f"\n   🔍 Full result: {result}\n")
        
        if result.get("sql_query"):
            print(f"\n   📝 Generated SQL:\n   {result['sql_query']}\n")
        
        if result.get("error"):
            print(f"   ❌ Error: {result['error']}\n")
        else:
            print(f"   ✅ Query executed successfully")
            
        if result.get("results") and result["results"].get("success"):
            print(f"   📊 Rows returned: {result['results']['row_count']}")
            
        if result.get("response"):
            print(f"\n   🤖 Agent Response:\n   {result['response']}\n")
        
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
