#!/usr/bin/env python3
"""
CLI interface for the SQL AI Agent.
"""

import os
import sys
import logging
from textwrap import dedent
from dotenv import load_dotenv
from agent import SQLAgent

# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = "INFO"
LOG_FILE = "agent.log"

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner."""
    banner = dedent("""
        ╔══════════════════════════════════════════════════════════════╗
        ║                                                              ║
        ║          🎬 Streaming Platform SQL AI Agent 🤖              ║
        ║                                                              ║
        ║  Ask questions about users, content, ratings, and more!     ║
        ║  I'll translate your questions into SQL and fetch results.  ║
        ║                                                              ║
        ╚══════════════════════════════════════════════════════════════╝

        Type 'quit', 'exit', or 'q' to exit.
        Type 'help' for example questions.

    """)
    print(banner)


def print_help():
    """Print help information with example queries."""
    help_text = dedent("""
        📚 EXAMPLE QUESTIONS:

        General Queries:
          • ¿Cuántos usuarios tenemos registrados?
          • Muestra los 10 contenidos más populares
          • ¿Qué géneros de contenido tenemos disponibles?

        User Analytics:
          • ¿Cuáles son los usuarios más activos?
          • Usuarios que se registraron en el último mes
          • ¿Cuántos usuarios hay por país?

        Content Analytics:
          • Películas mejor calificadas
          • Series con más visualizaciones
          • Contenido agregado este año

        Ratings & Views:
          • Promedio de rating por género
          • Contenido con más de 100 visualizaciones
          • Usuarios que nunca han calificado contenido

        Actor Information:
          • Actores con más participaciones
          • Actores nacidos en Argentina
          • Contenido protagonizado por [nombre del actor]

    """)
    print(help_text)

def print_divisor():
    print("\n" + "="*70)


def main():
    """Main CLI loop."""
    print_banner()
    
    # Load database configuration from environment
    db_config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }
    
    # Load Ollama configuration
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    sql_model = os.getenv("SQL_MODEL", "llama3.2:7b")
    conversation_model = os.getenv("CONVERSATION_MODEL", "llama3.2:7b")
    classifier_model = os.getenv("CLASSIFIER_MODEL", "phi3:mini")
    
    # Load classifier configuration
    use_embeddings_classifier = os.getenv("CLASSIFIER_TYPE", "llm").lower() == "embeddings"
    
    # Load RAG configuration (optional)
    rag_config = None
    summaries_dir = os.getenv("SUMMARIES_DIR")
    if summaries_dir and os.path.exists(summaries_dir):
        rag_config = {
            "summaries_dir": summaries_dir,
            "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
            "chroma_db_dir": os.getenv("CHROMA_DB_DIR", "./chroma_db")
        }
        print(f"📚 RAG functionality enabled (summaries: {summaries_dir})")
    else:
        print("⚠️  RAG functionality disabled (summaries directory not found)")
    
    
    try:
        # Initialize agent
        print("🔧 Initializing agent...")
        agent = SQLAgent(
            db_config=db_config,
            ollama_base_url=ollama_base_url,
            sql_model=sql_model,
            conversation_model=conversation_model,
            classifier_model=classifier_model,
            rag_config=rag_config,
            use_embeddings_classifier=use_embeddings_classifier
        )
        print("✅ Agent initialized successfully!\n")
        
    except Exception as e:
        print(f"❌ Error initializing agent: {str(e)}")
        logger.error(f"Initialization error: {str(e)}")
        sys.exit(1)
    
    # Main loop
    while True:
        try:
            # Get user input
            user_input = input("\n💬 Your question: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Thanks for using the SQL AI Agent.\n")
                break
            
            # Check for help command
            if user_input.lower() == 'help':
                print_help()
                continue
            
            # Skip empty input
            if not user_input:
                continue
            
            # Process query
            print("\n🤔 Thinking...")
            result = agent.query(user_input)
            
            print_divisor()
            
            # Show query type
            if result.get("query_type"):
                query_type_emoji = {
                    "SQL": "💾",
                    "RAG": "📚", 
                    "HYBRID": "🔀"
                }
                emoji = query_type_emoji.get(result["query_type"], "❓")
                print(f"\n{emoji} Query Type: {result['query_type']}\n")
            
            # Show generated SQL
            if result.get("sql_query"):
                print(f"📝 Generated SQL:\n")
                print(f"   {result['sql_query']}\n")
            
            # Show response
            if result.get("response"):
                print(f"🤖 Response:\n")
                print(f"{result['response']}\n")
            
            # Show raw results if available
            if result.get("results") and result["results"].get("success"):
                from sql_tool import SQLTool
                formatted = SQLTool(db_config).format_results(result["results"])
                print(f"\n📊 Query Results:\n")
                print(formatted)
            
            print_divisor()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using the SQL AI Agent.\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            logger.error(f"Runtime error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
