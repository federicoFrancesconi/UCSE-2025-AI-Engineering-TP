"""
LangGraph-based SQL AI Agent for natural language to SQL translation.
"""

import logging
from textwrap import dedent
from typing import TypedDict, Annotated, Sequence
from langchain_community.llms import Ollama
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import Graph, StateGraph, END
import operator

from sql_tool import SQLTool
from rag_tool import RAGTool

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State of the agent graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    query_type: str  # 'SQL', 'RAG', or 'HYBRID'
    sql_query: str
    sql_results: dict
    rag_results: dict
    retrieved_docs: list
    formatted_response: str
    error: str


class SQLAgent:
    """SQL AI Agent using LangGraph for orchestration."""
    
    def __init__(
        self,
        db_config: dict,
        ollama_base_url: str,
        sql_model: str,
        conversation_model: str,
        rag_config: dict = None
    ):
        """
        Initialize the SQL Agent.
        
        Args:
            db_config: Database configuration dictionary
            ollama_base_url: Base URL for Ollama API
            sql_model: Model name for SQL generation
            conversation_model: Model name for conversation
            rag_config: RAG configuration dictionary (optional)
        """
        self.sql_tool = SQLTool(db_config)
        self.ollama_base_url = ollama_base_url
        self.sql_model = sql_model
        self.conversation_model = conversation_model
        
        # Initialize RAG tool if config provided
        self.rag_tool = None
        if rag_config:
            try:
                self.rag_tool = RAGTool(
                    summaries_dir=rag_config['summaries_dir'],
                    ollama_base_url=ollama_base_url,
                    embedding_model=rag_config['embedding_model'],
                    chroma_db_dir=rag_config['chroma_db_dir']
                )
                logger.info("RAG functionality enabled")
            except Exception as e:
                logger.warning(f"RAG initialization failed, continuing without RAG: {e}")
                self.rag_tool = None
        
        # Initialize LLMs with model-specific optimizations
        if 'phi3' in sql_model.lower():
            # Phi3 optimizations: lower temperature, shorter context
            self.sql_llm = Ollama(
                model=sql_model,
                base_url=ollama_base_url,
                temperature=0,
                num_predict=500,
                top_k=5,
                top_p=0.7,
                repeat_penalty=1.0
            )
        else:
            # SQLCoder and other models
            self.sql_llm = Ollama(
                model=sql_model,
                base_url=ollama_base_url,
                temperature=0,
                num_predict=500  # Allow longer SQL queries
            )
        
        self.conversation_llm = Ollama(
            model=conversation_model,
            base_url=ollama_base_url,
            temperature=0.7
        )
        
        # Build the graph
        self.graph = self._build_graph()
        
        logger.info(f"SQLAgent initialized with SQL model: {sql_model}, Conversation model: {conversation_model}")
    
    def _build_graph(self) -> Graph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("understand_query", self._understand_query)
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("generate_sql", self._generate_sql)
        workflow.add_node("execute_sql", self._execute_sql)
        workflow.add_node("retrieve_documents", self._retrieve_documents)
        workflow.add_node("format_response", self._format_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("understand_query")
        
        # Add edges
        workflow.add_edge("understand_query", "classify_query")
        
        # Conditional routing based on query type
        workflow.add_conditional_edges(
            "classify_query",
            self._route_query,
            {
                "sql": "generate_sql",
                "rag": "retrieve_documents",
                "hybrid": "generate_sql",  # For hybrid, do SQL first
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "generate_sql",
            self._check_sql_generation,
            {
                "execute": "execute_sql",
                "error": "handle_error"
            }
        )
        workflow.add_conditional_edges(
            "execute_sql",
            self._check_sql_execution,
            {
                "format": "format_response",
                "rag": "retrieve_documents",  # For hybrid queries
                "error": "handle_error"
            }
        )
        workflow.add_edge("retrieve_documents", "format_response")
        workflow.add_edge("format_response", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    def _understand_query(self, state: AgentState) -> AgentState:
        """
        Node: Understand and validate the user query.
        """
        logger.info(f"Understanding query: {state['user_query']}")
        
        state["messages"] = [HumanMessage(content=state["user_query"])]
        
        return state
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """
        Node: Classify query as SQL, RAG, or HYBRID using LLM.
        """
        query = state['user_query']
        logger.info(f"Classifying query: {query}")
        
        # If RAG is not available, default to SQL
        if not self.rag_tool:
            state['query_type'] = 'SQL'
            logger.info("RAG not available, routing to SQL")
            return state
        
        # Use LLM to classify the query
        classification_prompt = dedent(f"""
            You are a query classifier for a streaming platform database system with content summaries.
            
            Classify the following user query into ONE of these categories:
            
            **SQL**: ONLY statistics, counts, lists, or rankings WITHOUT asking for content descriptions
            - "How many users?", "Average rating", "List top 10 movies", "Most viewed content"
            - "Which movie is most viewed?", "Show me the highest rated series"
            - Key: Just wants the NAME or DATA, not the plot/description
            
            **RAG**: ONLY content descriptions, plots, or themes of a SPECIFIC named content
            - "What is Aventuras Galácticas about?", "Describe the plot of Terror Nocturno"
            - "Tell me about El Misterio del Faro", "What's the theme of Amor en Primavera?"
            - Key: Must mention a specific content name and ask about its description
            
            **HYBRID**: Needs BOTH database query (top/best/most) AND content descriptions (what it's about/plot)
            - "What is the most viewed movie about?", "De qué trata la película más vista?"
            - "Best rated sci-fi movies and their plots", "Top series and what they're about"
            - "Tell me about the highest rated content", "Most popular movies with descriptions"
            - Key: Combines superlatives (most/best/top/más) WITH description requests (about/trata/plot)
            
            CRITICAL RULES:
            - If query asks "what is [superlative content] about?" → HYBRID (needs to find it first, then describe)
            - If query asks "what is [specific name] about?" → RAG (already knows the name)
            - If query just asks "which/what is the most X?" without description → SQL
            
            User Query: "{query}"
            
            Think step by step:
            1. Does it ask for top/best/most/highest? If YES and also asks "about/plot/describe" → HYBRID
            2. Does it mention a specific content name and ask about it? → RAG
            3. Does it only ask for data/stats/names? → SQL
            
            Respond with ONLY ONE WORD: SQL, RAG, or HYBRID
            Classification:""").strip()
        
        try:
            # Create a simple LLM for classification (fast, low temperature)
            classifier_llm = Ollama(
                model=self.conversation_model,
                base_url=self.ollama_base_url,
                temperature=0,
                num_predict=10  # We only need one word
            )
            
            response = classifier_llm.invoke(classification_prompt).strip().upper()
            
            # Extract the classification (handle cases where LLM adds extra text)
            if 'SQL' in response:
                query_type = 'SQL'
            elif 'RAG' in response:
                query_type = 'RAG'
            elif 'HYBRID' in response:
                query_type = 'HYBRID'
            else:
                # Default to SQL if classification is unclear
                logger.warning(f"Unclear classification response: {response}, defaulting to SQL")
                query_type = 'SQL'
            
            state['query_type'] = query_type
            logger.info(f"Query classified as: {query_type}")
            
        except Exception as e:
            logger.error(f"Error in query classification: {e}, defaulting to SQL")
            state['query_type'] = 'SQL'
        
        return state
    
    def _route_query(self, state: AgentState) -> str:
        """Conditional edge: Route based on query classification."""
        query_type = state.get('query_type', 'SQL')
        
        if query_type == 'SQL':
            return 'sql'
        elif query_type == 'RAG':
            return 'rag'
        elif query_type == 'HYBRID':
            return 'hybrid'
        else:
            return 'error'
    
    def _generate_sql(self, state: AgentState) -> AgentState:
        """
        Node: Generate SQL query from natural language.
        """
        logger.info("Generating SQL query")
        
        # Get database schema
        schema = self.sql_tool.get_database_schema()
        logger.info(f"Retrieved schema: {len(schema)} characters")
        
        # Process user query - clean and prepare it
        user_query = state['user_query'].strip()
        logger.info(f"Processing query: {user_query}")
        
        # Detect model type and create appropriate prompt
        if 'phi3' in self.sql_model.lower():
            # Phi3 uses a specific prompt template with special tokens
            system_prompt = self._create_phi3_prompt(user_query, schema)
        elif 'sqlcoder' in self.sql_model.lower():
            # SQLCoder uses ### Instructions format
            system_prompt = self._create_sqlcoder_prompt(user_query, schema)
        else:
            # Default prompt for other models
            system_prompt = self._create_default_prompt(user_query, schema)
        
        try:
            # Generate SQL using the SQL-specialized model
            logger.info(f"Calling SQL model: {self.sql_model}")
            sql_query = self.sql_llm.invoke(system_prompt)
            logger.info(f"Raw SQL response: {sql_query}")
            
            # Clean up the response
            sql_query = self._clean_sql_response(sql_query)
            
            state["sql_query"] = sql_query
            logger.info(f"Cleaned SQL: {sql_query}")
            
            if not sql_query:
                error_msg = "SQL model returned empty response"
                logger.error(error_msg)
                state["error"] = error_msg
            
        except Exception as e:
            error_msg = f"Error generating SQL: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["error"] = error_msg
        
        return state
    
    def _create_phi3_prompt(self, user_query: str, schema: str) -> str:
        """Create prompt for Phi3 model using its specific template."""
        return dedent(f"""
            <|system|>
            You are a PostgreSQL expert. Your task is to generate ONLY a valid PostgreSQL query.
            
            Rules:
            - Use proper table and column names from the schema
            - Every non-aggregated column in SELECT must be in GROUP BY
            - Use COUNT(*) for counting, SUM() for totals, AVG() for averages
            - For "top N" or "most X" queries: use ORDER BY with LIMIT
            - Use proper JOIN syntax with foreign key relationships
            - Generate ONLY the SQL query, no explanations or markdown
            <|end|>
            <|user|>
            Question: {user_query}
            
            Database Schema:
            {schema}
            
            Generate a PostgreSQL query to answer the question. Output ONLY the SQL query:
            <|end|>
            <|assistant|>
            SELECT
        """).strip()
    
    def _create_sqlcoder_prompt(self, user_query: str, schema: str) -> str:
        """Create prompt for SQLCoder model using its recommended format."""
        return dedent(f"""
            ### Instructions:
            Your task is to convert a question into a SQL query, given a PostgreSQL database schema.
            Adhere to these rules:
            - **Deliberately go through the question and database schema word by word** to appropriately answer the question
            - **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`
            - When creating a ratio, always cast the numerator as float
            - **CRITICAL PostgreSQL GROUP BY rule**: Every non-aggregated column in SELECT must appear in GROUP BY
              * If you SELECT c.titulo, c.id_contenido and use COUNT(*), you must GROUP BY c.titulo, c.id_contenido
              * If you SELECT c.titulo and use COUNT(*), you must GROUP BY c.titulo
            - Prefer simple queries over complex window functions when possible
            - For "most viewed" or "most popular" queries, use COUNT(*), GROUP BY, ORDER BY, and LIMIT
            - Use COUNT(*) for counting rows, SUM() for totals, AVG() for averages
            - Generate ONLY valid PostgreSQL syntax
            - Do NOT include explanations, comments, or additional text after the SQL query
            
            ### Input:
            Generate a SQL query that answers the question `{user_query}`.
            This query will run on a PostgreSQL database whose schema is represented below:
            {schema}
            
            ### Response:
            Based on your instructions, here is the SQL query I have generated to answer the question `{user_query}`:
            ```sql
        """).strip()
    
    def _create_default_prompt(self, user_query: str, schema: str) -> str:
        """Create default prompt for general models."""
        return dedent(f"""
            You are a PostgreSQL expert. Generate ONLY a valid SQL query.
            
            Question: {user_query}
            
            Database Schema:
            {schema}
            
            Generate a PostgreSQL query. Rules:
            - Every non-aggregated column in SELECT must be in GROUP BY
            - Use COUNT(*), SUM(), AVG() for aggregations
            - Use ORDER BY with LIMIT for "top N" queries
            - Output ONLY the SQL query, no explanations
            
            SQL Query:
        """).strip()
    
    def _clean_sql_response(self, sql_query: str) -> str:
        """Clean up SQL response from various model outputs."""
        sql_query = sql_query.strip()
        
        # Remove markdown code blocks if present
        if "```sql" in sql_query:
            # Extract SQL from code block
            start = sql_query.find("```sql") + 6
            end = sql_query.find("```", start)
            if end != -1:
                sql_query = sql_query[start:end]
        elif "```" in sql_query:
            # Remove any ``` markers
            sql_query = sql_query.replace("```sql", "").replace("```", "")
        
        sql_query = sql_query.strip()
        
        # Remove trailing semicolon if present
        while sql_query.endswith(";"):
            sql_query = sql_query[:-1].strip()
        
        # Remove any trailing newlines or whitespace
        sql_query = " ".join(sql_query.split())
        
        # Sometimes models add explanatory text - try to extract just the SELECT statement
        if "\n\n" in sql_query or ". " in sql_query:
            # Look for SELECT statement
            lines = sql_query.split("\n")
            for i, line in enumerate(lines):
                if line.strip().upper().startswith("SELECT"):
                    # Take from SELECT to the end or until we hit explanatory text
                    sql_query = " ".join(lines[i:])
                    break
        
        # Remove phi3-specific artifacts
        if sql_query.startswith("SELECT"):
            # Already starts with SELECT, good
            pass
        else:
            # Try to find SELECT in the response
            select_pos = sql_query.upper().find("SELECT")
            if select_pos != -1:
                sql_query = sql_query[select_pos:]
        
        return sql_query
    
    def _execute_sql(self, state: AgentState) -> AgentState:
        """
        Node: Execute the generated SQL query.
        """
        logger.info("Executing SQL query")
        
        try:
            results = self.sql_tool.execute_query(state["sql_query"])
            state["sql_results"] = results
            
            if not results["success"]:
                state["error"] = results["error"]
                
        except Exception as e:
            error_msg = f"Error executing SQL: {str(e)}"
            logger.error(error_msg)
            state["error"] = error_msg
        
        return state
    
    def _format_response(self, state: AgentState) -> AgentState:
        """
        Node: Format the results (SQL and/or RAG) into a natural language response.
        """
        logger.info("Formatting response")
        
        try:
            query_type = state.get('query_type', 'SQL')
            
            # Build context based on available data
            context_parts = []
            
            # Add SQL context if available
            if state.get("sql_results") and state["sql_results"].get("success"):
                formatted_results = self.sql_tool.format_results(state["sql_results"])
                context_parts.append(f"""
                SQL Query executed:
                {state.get('sql_query', 'N/A')}
                
                Results:
                {formatted_results}
                """)
            
            # Add RAG context if available
            if state.get("retrieved_docs"):
                docs = state["retrieved_docs"]
                rag_info = state.get("rag_results", {})
                metadatas = rag_info.get("metadatas", [])
                similarities = rag_info.get("similarities", [])
                
                rag_context = "Content Information from PDFs:\n"
                for i, (doc, meta, sim) in enumerate(zip(docs, metadatas, similarities), 1):
                    title = meta.get('title', 'Unknown') if meta else 'Unknown'
                    # Truncate long documents
                    doc_preview = doc[:500] + "..." if len(doc) > 500 else doc
                    rag_context += f"\n[{i}] {title} (relevance: {sim:.2f}):\n{doc_preview}\n"
                
                context_parts.append(rag_context)
            
            # Create the full context
            full_context = "\n\n".join(context_parts)
            
            # Generate response based on query type
            if query_type == 'RAG':
                # RAG-only response
                prompt = dedent(f"""
                    You are a helpful AI assistant for a streaming platform.
                    
                    The user asked: "{state['user_query']}"
                    
                    {full_context}
                    
                    Provide a clear, informative answer based on the content information above.
                    Be concise but include key details about the content.
                    
                    Response:
                """).strip()
            else:
                # SQL or HYBRID response
                prompt = dedent(f"""
                    You are a helpful AI assistant for a streaming platform.
    
                    The user asked: "{state['user_query']}"
    
                    {full_context}
    
                    Provide a brief, friendly summary combining the information above.
                    Be concise but informative. If there are many results, highlight the most relevant ones.
    
                    Response:
                """).strip()
            
            conversation_response = self.conversation_llm.invoke(prompt)
            state["formatted_response"] = conversation_response.strip()
            
        except Exception as e:
            error_msg = f"Error formatting response: {str(e)}"
            logger.error(error_msg)
            state["error"] = error_msg
        
        return state
    
    def _handle_error(self, state: AgentState) -> AgentState:
        """
        Node: Handle errors gracefully.
        """
        logger.info("Handling error")
        
        error_message = state.get("error", "Unknown error occurred")
        
        state["formatted_response"] = dedent(f"""
            I encountered an error while processing your request:

            ❌ {error_message}

            Please try rephrasing your question or ask something else.
        """).strip()
        
        return state
    
    def _check_sql_generation(self, state: AgentState) -> str:
        """Conditional edge: Check if SQL generation was successful."""
        if state.get("error"):
            return "error"
        if state.get("sql_query"):
            return "execute"
        return "error"
    
    def _check_sql_execution(self, state: AgentState) -> str:
        """Conditional edge: Check if SQL execution was successful."""
        if state.get("error"):
            return "error"
        if state.get("sql_results") and state["sql_results"].get("success"):
            # Check if this is a hybrid query that needs RAG
            if state.get("query_type") == "HYBRID":
                return "rag"
            return "format"
        return "error"
    
    def _retrieve_documents(self, state: AgentState) -> AgentState:
        """
        Node: Retrieve relevant documents using RAG.
        """
        logger.info("Retrieving documents via RAG")
        
        if not self.rag_tool:
            error_msg = "RAG functionality not available"
            logger.error(error_msg)
            state["error"] = error_msg
            return state
        
        try:
            # Search for relevant documents
            rag_results = self.rag_tool.search(state['user_query'], top_k=3)
            state["rag_results"] = rag_results
            
            if rag_results["success"]:
                state["retrieved_docs"] = rag_results["documents"]
                logger.info(f"Retrieved {len(rag_results['documents'])} documents")
            else:
                # RAG failed - check if it was RAG-only query
                if state.get("query_type") == "RAG":
                    # For RAG-only queries, this is an error
                    state["error"] = rag_results.get("error", "Failed to retrieve documents")
                else:
                    # For hybrid queries, continue without RAG
                    logger.warning("RAG retrieval failed, continuing without RAG context")
                    state["retrieved_docs"] = []
                    
        except Exception as e:
            error_msg = f"Error retrieving documents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Only fail for RAG-only queries
            if state.get("query_type") == "RAG":
                state["error"] = error_msg
            else:
                logger.warning("RAG failed for hybrid query, continuing with SQL only")
                state["retrieved_docs"] = []
        
        return state
    
    def query(self, user_query: str) -> dict:
        """
        Process a user query through the agent graph.
        
        Args:
            user_query: Natural language query from user
            
        Returns:
            Dictionary with response and metadata
        """
        logger.info(f"Processing user query: {user_query}")
        
        # Initialize state
        initial_state = {
            "messages": [],
            "user_query": user_query,
            "query_type": "",
            "sql_query": "",
            "sql_results": {},
            "rag_results": {},
            "retrieved_docs": [],
            "formatted_response": "",
            "error": ""
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return {
            "response": final_state.get("formatted_response", ""),
            "query_type": final_state.get("query_type", ""),
            "sql_query": final_state.get("sql_query", ""),
            "results": final_state.get("sql_results", {}),
            "rag_results": final_state.get("rag_results", {}),
            "error": final_state.get("error", "")
        }
