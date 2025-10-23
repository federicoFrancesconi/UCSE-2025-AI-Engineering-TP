#!/usr/bin/env python3
"""
Streamlit GUI for the SQL AI Agent.
"""

import os
import sys
import logging
import time
import streamlit as st
from dotenv import load_dotenv
from agent import SQLAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="SQL AI Agent",
    page_icon="🤖",
    layout="centered"
)

# Custom CSS for minimal styling
st.markdown("""
    <style>
    .stApp {
        max-width: 1200px;
    }
    .query-type-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .badge-sql {
        background-color: #e3f2fd;
        color: #1976d2;
    }
    .badge-rag {
        background-color: #f3e5f5;
        color: #7b1fa2;
    }
    .badge-hybrid {
        background-color: #e8f5e9;
        color: #388e3c;
    }
    .badge-auto {
        background-color: #fff3e0;
        color: #f57c00;
    }
    </style>
""", unsafe_allow_html=True)


def check_groq_availability():
    """Check if Groq API key is available."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    return groq_api_key is not None and len(groq_api_key.strip()) > 0


def initialize_agent(model_provider="ollama"):
    """
    Initialize the SQL Agent with configuration from environment.
    
    Args:
        model_provider: "ollama" or "groq"
    """
    
    # Load database configuration
    db_config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT")),
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD")
    }
    
    # Validate provider selection
    model_provider = model_provider.lower()
    if model_provider == "groq" and not check_groq_availability():
        st.warning("⚠️ Groq API key not found. Falling back to Ollama.")
        logger.warning("Groq selected but API key not available, falling back to Ollama")
        model_provider = "ollama"
    
    # Load Ollama configuration
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    sql_model = os.getenv("SQL_MODEL", "llama3.2:7b")
    conversation_model = os.getenv("CONVERSATION_MODEL", "llama3.2:7b")
    classifier_model = os.getenv("CLASSIFIER_MODEL", "phi3:mini")
    
    # Load Groq configuration
    groq_api_key = os.getenv("GROQ_API_KEY")
    groq_sql_model = os.getenv("GROQ_SQL_MODEL", "llama-3.1-8b-instant")
    groq_conversation_model = os.getenv("GROQ_CONVERSATION_MODEL", "llama-3.1-8b-instant")
    groq_classifier_model = os.getenv("GROQ_CLASSIFIER_MODEL", "llama-3.1-8b-instant")
    
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
    
    try:
        agent = SQLAgent(
            db_config=db_config,
            ollama_base_url=ollama_base_url,
            sql_model=sql_model,
            conversation_model=conversation_model,
            classifier_model=classifier_model,
            rag_config=rag_config,
            use_embeddings_classifier=use_embeddings_classifier,
            model_provider=model_provider,
            groq_api_key=groq_api_key,
            groq_sql_model=groq_sql_model,
            groq_conversation_model=groq_conversation_model,
            groq_classifier_model=groq_classifier_model
        )
        return agent, model_provider
    except Exception as e:
        st.error(f"Error initializing agent: {str(e)}")
        logger.error(f"Initialization error: {str(e)}")
        return None, None


def get_example_queries():
    """Return a list of example queries (Spanish and English)."""
    return [
        "¿Cuántos usuarios tenemos registrados?",
        "How many registered users do we have?",
        "Muestra los 10 contenidos más populares",
        "Show me the top 10 most popular content",
        "¿Qué géneros de contenido tenemos disponibles?",
        "What content genres are available?",
        "Películas mejor calificadas",
        "Highest rated movies",
        "¿De qué trata Aventuras Galácticas?",
        "What is Aventuras Galácticas about?",
        "¿De qué trata la película más vista?",
        "What is the most viewed movie about?"
    ]


def render_query_type_badge(query_type):
    """Render a styled badge for the query type."""
    if not query_type:
        query_type = "AUTO"
    
    badge_class = f"badge-{query_type.lower()}"
    emoji = {
        "SQL": "💾",
        "RAG": "📚",
        "HYBRID": "🔀",
        "AUTO": "🤖"
    }.get(query_type, "❓")
    
    st.markdown(
        f'<div class="query-type-badge {badge_class}">{emoji} {query_type}</div>',
        unsafe_allow_html=True
    )


def copy_to_clipboard_button(text, button_label="Copy to clipboard"):
    """Create a button that copies text to clipboard."""
    # Using streamlit's native button with a unique key
    if st.button(button_label, key=f"copy_{hash(text)}"):
        st.toast("✅ Copied to clipboard!")
        # Note: Actual clipboard copy requires JavaScript, so we'll show the text
        # in a code block that users can manually copy
        st.code(text, language=None)


def main():
    """Main Streamlit application."""
    
    # Title
    st.title("🤖 SQL AI Agent")
    st.markdown("Ask questions about users, content, ratings, and more!")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None
    
    if "selected_provider" not in st.session_state:
        st.session_state.selected_provider = None
    
    if "show_switch_warning" not in st.session_state:
        st.session_state.show_switch_warning = False
    
    if "switch_to_provider" not in st.session_state:
        st.session_state.switch_to_provider = None
    
    if "response_times" not in st.session_state:
        st.session_state.response_times = []
    
    # Pre-initialization: Provider selection screen
    if st.session_state.selected_provider is None:
        st.markdown("---")
        st.markdown("### 🔧 Configuration")
        st.markdown("Please select a model provider to get started:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🖥️ Local (Ollama)")
            st.markdown("- Uses local Ollama models")
            st.markdown("- Free, no API key needed")
            st.markdown("- Requires Ollama running")
            if st.button("Use Ollama", type="primary", use_container_width=True):
                st.session_state.selected_provider = "ollama"
                st.rerun()
        
        with col2:
            st.markdown("#### ☁️ Remote (Groq)")
            st.markdown("- Uses Groq cloud API")
            st.markdown("- Faster inference")
            st.markdown("- Requires API key in .env")
            
            groq_available = check_groq_availability()
            if not groq_available:
                st.error("⚠️ Groq API key not found in .env")
                if st.button("Use Groq (will fallback to Ollama)", use_container_width=True, disabled=True):
                    pass
            else:
                if st.button("Use Groq", type="primary", use_container_width=True):
                    st.session_state.selected_provider = "groq"
                    st.rerun()
        
        st.stop()
    
    # Initialize agent with selected provider
    if "agent" not in st.session_state or st.session_state.agent is None:
        with st.spinner("🔧 Initializing agent..."):
            agent, model_provider = initialize_agent(st.session_state.selected_provider)
            if agent:
                st.session_state.agent = agent
                st.session_state.model_provider = model_provider
                st.success(f"✅ Agent initialized! Using {model_provider.upper()} models")
            else:
                st.error("Failed to initialize agent. Please check your configuration.")
                st.stop()
    
    # Example queries section
    st.markdown("### 💡 Example Questions")
    example_queries = get_example_queries()
    
    # Display example queries as buttons in columns
    cols = st.columns(3)
    for idx, example in enumerate(example_queries):
        col = cols[idx % 3]
        with col:
            if st.button(example, key=f"example_{idx}", use_container_width=True):
                # Set pending query to be processed
                st.session_state.pending_query = example
                st.rerun()
    
    st.markdown("---")
    
    # Chat history
    st.markdown("### 💬 Conversation")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display additional info for assistant messages
            if message["role"] == "assistant" and "metadata" in message:
                metadata = message["metadata"]
                
                # Query type badge
                if metadata.get("query_type"):
                    render_query_type_badge(metadata["query_type"])
                
                # Response time
                if metadata.get("response_time"):
                    response_time = metadata["response_time"]
                    st.caption(f"⏱️ Response time: {response_time:.2f}s")
                
                # SQL Query (collapsible)
                if metadata.get("sql_query"):
                    with st.expander("📝 View SQL Query"):
                        st.code(metadata["sql_query"], language="sql")
                
                # RAG Results (collapsible)
                if metadata.get("rag_results") and metadata["rag_results"].get("success"):
                    rag = metadata["rag_results"]
                    with st.expander(f"📚 View RAG Sources ({len(rag.get('documents', []))} documents)"):
                        docs = rag.get("documents", [])
                        metadatas = rag.get("metadatas", [])
                        similarities = rag.get("similarities", [])
                        
                        for i, (doc, meta, sim) in enumerate(zip(docs, metadatas, similarities), 1):
                            title = meta.get('title', 'Unknown') if meta else 'Unknown'
                            st.markdown(f"**[{i}] {title}** (similarity: {sim:.2f})")
                            st.text_area(
                                f"Content {i}",
                                doc[:500] + "..." if len(doc) > 500 else doc,
                                height=150,
                                key=f"doc_{i}_{hash(doc)}",
                                label_visibility="collapsed"
                            )
                
                # Query Results Table (collapsible)
                if metadata.get("results") and metadata["results"].get("success"):
                    results = metadata["results"]
                    row_count = len(results.get("rows", []))
                    with st.expander(f"📊 View Query Results ({row_count} rows)"):
                        if results.get("columns") and results.get("rows"):
                            # Display as dataframe for better formatting
                            import pandas as pd
                            df = pd.DataFrame(results["rows"], columns=results["columns"])
                            st.dataframe(df, use_container_width=True)
                
                # Copy response button
                if st.button("📋 Copy Response", key=f"copy_response_{hash(message['content'])}"):
                    st.code(message["content"], language=None)
                    st.toast("✅ Response displayed for copying!")
    
    # Check for pending query from example buttons
    pending = st.session_state.pending_query
    if pending:
        st.session_state.pending_query = None
        user_input = pending
    else:
        user_input = None
    
    # Always show chat input
    chat_input = st.chat_input("Ask a question about the streaming platform...")
    
    # Use chat input if no pending query
    if not user_input and chat_input:
        user_input = chat_input
    
    # Process query only if we have new input
    if user_input:
        # Ensure agent is initialized before processing
        if st.session_state.agent is None:
            st.error("Agent is not initialized. Please refresh the page.")
            st.stop()
        
        # Check if this is a new message (not already in history)
        # This prevents reprocessing on rerun
        if not st.session_state.messages or st.session_state.messages[-1]["content"] != user_input or st.session_state.messages[-1]["role"] != "user":
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(user_input)
            
            # Process query with agent
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    try:
                        # Track response time
                        start_time = time.time()
                        result = st.session_state.agent.query(user_input)
                        end_time = time.time()
                        response_time = end_time - start_time
                        
                        response = result.get("response", "No response generated.")
                        
                        # Display response
                        st.markdown(response)
                        
                        # Display metadata
                        metadata = {
                            "query_type": result.get("query_type"),
                            "sql_query": result.get("sql_query"),
                            "results": result.get("results"),
                            "rag_results": result.get("rag_results"),
                            "response_time": response_time
                        }
                        
                        # Query type badge
                        if metadata.get("query_type"):
                            render_query_type_badge(metadata["query_type"])
                        
                        # Response time
                        if metadata.get("response_time"):
                            response_time = metadata["response_time"]
                            st.caption(f"⏱️ Response time: {response_time:.2f}s")
                        
                        # SQL Query (collapsible)
                        if metadata.get("sql_query"):
                            with st.expander("📝 View SQL Query"):
                                st.code(metadata["sql_query"], language="sql")
                        
                        # RAG Results (collapsible)
                        if metadata.get("rag_results") and metadata["rag_results"].get("success"):
                            rag = metadata["rag_results"]
                            with st.expander(f"📚 View RAG Sources ({len(rag.get('documents', []))} documents)"):
                                docs = rag.get("documents", [])
                                metadatas = rag.get("metadatas", [])
                                similarities = rag.get("similarities", [])
                                
                                for i, (doc, meta, sim) in enumerate(zip(docs, metadatas, similarities), 1):
                                    title = meta.get('title', 'Unknown') if meta else 'Unknown'
                                    st.markdown(f"**[{i}] {title}** (similarity: {sim:.2f})")
                                    st.text_area(
                                        f"Content {i}",
                                        doc[:500] + "..." if len(doc) > 500 else doc,
                                        height=150,
                                        key=f"doc_{i}_{hash(doc)}",
                                        label_visibility="collapsed"
                                    )
                        
                        # Query Results Table (collapsible)
                        if metadata.get("results") and metadata["results"].get("success"):
                            results = metadata["results"]
                            row_count = len(results.get("rows", []))
                            with st.expander(f"📊 View Query Results ({row_count} rows)"):
                                if results.get("columns") and results.get("rows"):
                                    import pandas as pd
                                    df = pd.DataFrame(results["rows"], columns=results["columns"])
                                    st.dataframe(df, use_container_width=True)
                        
                        # Copy response button
                        if st.button("📋 Copy Response", key=f"copy_response_{hash(response)}"):
                            st.code(response, language=None)
                            st.toast("✅ Response displayed for copying!")
                        
                        # Add assistant message to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "metadata": metadata
                        })
                        
                        # Track response time for statistics
                        st.session_state.response_times.append(response_time)
                        
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        logger.error(f"Query processing error: {str(e)}", exc_info=True)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Controls")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.response_times = []
            st.rerun()
        
        st.markdown("---")
        
        # Model provider switch
        st.markdown("### 🔄 Model Provider")
        current_provider = st.session_state.get('model_provider', 'unknown')
        
        if current_provider == "ollama":
            st.info("🖥️ Currently using: **Local (Ollama)**")
            
            # Check if Groq is available
            if check_groq_availability():
                if st.button("Switch to Groq", use_container_width=True):
                    # Show confirmation dialog using session state
                    st.session_state.show_switch_warning = True
                    st.session_state.switch_to_provider = "groq"
                    st.rerun()
            else:
                st.caption("⚠️ Groq unavailable (no API key)")
        
        elif current_provider == "groq":
            st.info("☁️ Currently using: **Remote (Groq)**")
            
            if st.button("Switch to Ollama", use_container_width=True):
                # Show confirmation dialog using session state
                st.session_state.show_switch_warning = True
                st.session_state.switch_to_provider = "ollama"
                st.rerun()
        
        # Handle provider switch warning
        if st.session_state.get('show_switch_warning', False):
            target_provider = st.session_state.get('switch_to_provider', 'ollama')
            st.warning(f"⚠️ Switching to **{target_provider.upper()}** will clear your conversation history.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm", use_container_width=True):
                    # Clear agent, conversation, and provider info
                    st.session_state.agent = None
                    st.session_state.model_provider = None
                    st.session_state.messages = []
                    st.session_state.response_times = []
                    st.session_state.selected_provider = target_provider
                    st.session_state.show_switch_warning = False
                    st.session_state.switch_to_provider = None
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_switch_warning = False
                    st.session_state.switch_to_provider = None
                    st.rerun()
        
        st.markdown("---")
        
        # Info section
        st.markdown("### ℹ️ Info")
        st.markdown(f"**Provider:** {current_provider.upper()}")
        
        # Count only user messages (queries)
        query_count = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
        st.markdown(f"**Queries:** {query_count}")
        
        # Response time statistics
        if st.session_state.response_times:
            avg_time = sum(st.session_state.response_times) / len(st.session_state.response_times)
            min_time = min(st.session_state.response_times)
            max_time = max(st.session_state.response_times)
            st.markdown(f"**Avg Response:** {avg_time:.2f}s")
            st.caption(f"Min: {min_time:.2f}s | Max: {max_time:.2f}s")


if __name__ == "__main__":
    main()
