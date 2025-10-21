"""
LangGraph-based SQL AI Agent for natural language to SQL translation.
"""

import logging
from textwrap import dedent
from typing import TypedDict
from langchain_community.llms import Ollama
from langgraph.graph import Graph, StateGraph, END
from langchain_community.embeddings import OllamaEmbeddings

from sql_tool import SQLTool
from rag_tool import RAGTool

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State of the agent graph."""
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
    
    # ----------------- INITIALIZATION -----------------
    def __init__(
        self,
        db_config: dict,
        ollama_base_url: str,
        sql_model: str,
        conversation_model: str,
        classifier_model: str = None,
        rag_config: dict = None,
        use_embeddings_classifier: bool = False
    ):
        """
        Initialize the SQL Agent.
        
        Args:
            db_config: Database configuration dictionary
            ollama_base_url: Base URL for Ollama API
            sql_model: Model name for SQL generation
            conversation_model: Model name for conversation
            classifier_model: Model name for query classification (optional, defaults to conversation_model)
            rag_config: RAG configuration dictionary (optional)
            use_embeddings_classifier: Whether to use embeddings-based classification (default: False, uses LLM)
        """
        self.sql_tool = SQLTool(db_config)
        self.ollama_base_url = ollama_base_url
        self.sql_model = sql_model
        self.conversation_model = conversation_model
        self.classifier_model = classifier_model if classifier_model else conversation_model
        self.use_embeddings_classifier = use_embeddings_classifier
        
        # Initialize RAG tool
        self._init_rag_tool(rag_config, ollama_base_url)

        # Initialize LLMs
        self._init_models(sql_model, conversation_model, ollama_base_url)

        # Build the graph
        self.graph = self._build_graph()
        
        # Initialize query classification examples only if using embeddings classifier
        if self.use_embeddings_classifier:
            self._init_classification_examples()
        
        logger.info(f"SQLAgent initialized with SQL model: {sql_model}, Conversation model: {conversation_model}, Classifier model: {self.classifier_model}, Use embeddings classifier: {self.use_embeddings_classifier}")
    
    def _init_rag_tool(self, rag_config: dict, ollama_base_url: str):
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

    def _init_models(self, sql_model: str, conversation_model: str, ollama_base_url: str):
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

    def _init_classification_examples(self):
        """Initialize example queries for embedding-based classification."""
        self.classification_examples = {
            'SQL': [
                "¿Cuántos usuarios hay?",
                "How many users are registered?",
                "Dame el promedio de calificaciones",
                "What's the average rating?",
                "Lista los 10 contenidos más vistos",
                "Show me the top 10 movies",
                "¿Qué usuario tiene más visualizaciones?",
                "Which content is most viewed?",
                "Total de películas",
                "Count the series",
                "Highest rated content",
                "Contenido mejor calificado",
                "¿Cuál es la película más popular?",
                "Most viewed series",
            ],
            'RAG': [
                "¿De qué trata Aventuras Galácticas?",
                "What is Aventuras Galácticas about?",
                "Describe la trama de Terror Nocturno",
                "Tell me about El Misterio del Faro",
                "¿Cuál es el tema de Amor en Primavera?",
                "What's the plot of La Casa del Tiempo?",
                "Cuéntame sobre Historia de la Humanidad",
                "Describe Mundos Paralelos",
                "What is the story of Océanos Profundos?",
                "Explícame de qué va Familias Modernas",
                "What's Detectives del Futuro about?",
                "Háblame sobre Aventuras en el Amazonas",
            ],
            'HYBRID': [
                "¿De qué trata la película más vista?",
                "What is the most viewed movie about?",
                "Películas de ciencia ficción mejor calificadas con sus tramas",
                "Best rated sci-fi movies and their plots",
                "Top 5 películas populares y de qué tratan",
                "Most popular movies and what they're about",
                "Películas con rating mayor a 8 y sus descripciones",
                "Tell me about the highest rated movie and its plot",
                "Dame las películas de comedia más vistas y explícame de qué van",
                "Show me top rated movies with descriptions",
                "¿Cuál es la película mejor calificada y de qué trata?",
                "Most watched movies and their plots",
                "Mejor película y su descripción",
                "Top movies with summaries",
            ]
        }
        # Pre-compute embeddings for examples
        self._precompute_embeddings()
    
    def _precompute_embeddings(self):
        # Pre-compute embeddings for examples
        self.example_embeddings = {}
        if self.rag_tool:
            try:
                from langchain_community.embeddings import OllamaEmbeddings
                embeddings = OllamaEmbeddings(
                    model=self.rag_tool.embedding_model,
                    base_url=self.ollama_base_url
                )
                
                for category, examples in self.classification_examples.items():
                    self.example_embeddings[category] = embeddings.embed_documents(examples)
                    logger.info(f"Pre-computed {len(examples)} embeddings for {category}")
            except Exception as e:
                logger.warning(f"Could not pre-compute embeddings: {e}")
                self.example_embeddings = {}
        else:
            logger.warning("RAG tool not available, cannot pre-compute embeddings for classification")
    
    def _build_graph(self) -> Graph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Choose classifier based on configuration
        classifier_func = self._classify_query_embeddings if self.use_embeddings_classifier else self._classify_query
        
        # Add nodes
        workflow.add_node("classify_query", classifier_func)
        workflow.add_node("generate_sql", self._generate_sql)
        workflow.add_node("execute_sql", self._execute_sql)
        workflow.add_node("retrieve_documents", self._retrieve_documents)
        workflow.add_node("format_response", self._format_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point directly to classification
        workflow.set_entry_point("classify_query")
        
        # Add edges (removed edge from understand_query)
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
    
    # ----------------- QUERY CLASSIFICATION -----------------
    def _classify_query(self, state: AgentState) -> AgentState:
        """
        Node: Classify query as SQL, RAG, or HYBRID using LLM.
        """
        query = state['user_query']
        logger.info(f"Classifying query with LLM: {query}")
        
        # If RAG is not available, default to SQL
        if not self.rag_tool:
            state['query_type'] = 'SQL'
            logger.info("RAG not available, routing to SQL")
            return state
        
        # Use LLM to classify the query
        classification_prompt = dedent(f"""
            <|system|>
            Classify queries: SQL, RAG, or HYBRID.
            
            SQL - wants NAME/NUMBER/RANK only, no description:
            "Most active user?" → SQL
            "Película más vista" → SQL
            "Top 10" → SQL
            "Which is most viewed?" → SQL
            
            RAG - asks about SPECIFIC named content:
            "What is Aventuras Galácticas about?" → RAG
            "De qué trata Terror Nocturno?" → RAG
            
            HYBRID - wants content ranking AND description (must have "content/" + "trata/about/describe"):
            "De qué trata la película más vista?" → HYBRID
            "What is the most viewed series about?" → HYBRID
            "Tell me about the top rated película" → HYBRID
            
            Rules:
            - NO "trata/about/describe" = SQL (even with "más/most")
            - HYBRID only for content with description request
            - Users/series/episodes asking for description = SQL (not in RAG)
            <|end|>
            <|user|>
            Query: "{query}"
            <|end|>
            <|assistant|>
            Classification:""").strip()
        
        try:
            # Create a simple LLM for classification (fast, low temperature)
            classifier_llm = Ollama(
                model=self.classifier_model,
                base_url=self.ollama_base_url,
                temperature=0,
                num_predict=6,  # Allow enough tokens for full word
                top_k=3,
                top_p=0.5,
                repeat_penalty=1.0
            )
            
            response = classifier_llm.invoke(classification_prompt).strip().upper()
            
            # Extract the classification (handle cases where LLM adds extra text)
            if 'HYBRID' in response:
                query_type = 'HYBRID'
            elif 'RAG' in response:
                query_type = 'RAG'
            elif 'SQL' in response:
                query_type = 'SQL'
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
    
    def _classify_query_embeddings(self, state: AgentState) -> AgentState:
        """
        Alternative classification method using embedding similarity.
        This is kept as a backup/experimental approach.
        To use this, replace the call in the graph from _classify_query to this method.
        """
        query = state['user_query']
        logger.info(f"Classifying query with embeddings: {query}")
        
        # If RAG is not available, default to SQL
        if not self.rag_tool or not self.example_embeddings:
            state['query_type'] = 'SQL'
            logger.info("RAG not available or embeddings not initialized, routing to SQL")
            return state
        
        try:
            # Get embedding for the input query
            from langchain_community.embeddings import OllamaEmbeddings
            embeddings = OllamaEmbeddings(
                model=self.rag_tool.embedding_model,
                base_url=self.ollama_base_url
            )
            
            query_embedding = embeddings.embed_query(query)
            
            # Calculate similarity scores for each category
            category_scores = {}
            
            for category, example_embeddings in self.example_embeddings.items():
                # Calculate similarity with each example
                similarities = [
                    self._cosine_similarity(query_embedding, example_emb)
                    for example_emb in example_embeddings
                ]
                
                # Use max similarity as the category score
                max_similarity = max(similarities) if similarities else 0.0
                category_scores[category] = max_similarity
                
                logger.info(f"{category}: max_similarity={max_similarity:.4f}")
            
            # Select category with highest score
            best_category = max(category_scores, key=category_scores.get)
            best_score = category_scores[best_category]
            
            # Log detailed scores
            logger.info(f"Similarity scores: {category_scores}")
            logger.info(f"Best match: {best_category} (score: {best_score:.4f})")
            
            state['query_type'] = best_category
            
        except Exception as e:
            logger.error(f"Error in embedding-based classification: {e}, defaulting to SQL")
            import traceback
            traceback.print_exc()
            state['query_type'] = 'SQL'
        
        return state
    
    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors."""
        import math
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
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
        query_type = state.get('query_type', 'SQL')
        logger.info(f"Processing query: {user_query} (type: {query_type})")
        
        # Detect model type and create appropriate prompt
        if 'phi3' in self.sql_model.lower():
            # Phi3 uses a specific prompt template with special tokens
            system_prompt = self._create_phi3_prompt(user_query, schema, query_type)
        elif 'sqlcoder' in self.sql_model.lower():
            # SQLCoder uses ### Instructions format
            system_prompt = self._create_sqlcoder_prompt(user_query, schema, query_type)
        else:
            # Default prompt for other models
            system_prompt = self._create_default_prompt(user_query, schema, query_type)
        
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
    
    def _create_phi3_prompt(self, user_query: str, schema: str, query_type: str = "SQL") -> str:
        """Create prompt for Phi3 model using its specific template."""
        
        # Add special instruction for HYBRID queries
        hybrid_instruction = ""
        if query_type == "HYBRID":
            hybrid_instruction = "\n            - CRITICAL: ALWAYS include c.titulo (content title) in SELECT for ranking queries"
        
        return dedent(f"""
            <|system|>
            You are a PostgreSQL expert. Your task is to generate ONLY a valid PostgreSQL query.
            
            Rules:
            - Use proper table and column names from the schema
            - Every non-aggregated column in SELECT must be in GROUP BY
            - Use COUNT(*) for counting, SUM() for totals, AVG() for averages
            - For "top N" or "most X" queries: use ORDER BY with LIMIT{hybrid_instruction}
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
    
    def _create_sqlcoder_prompt(self, user_query: str, schema: str, query_type: str = "SQL") -> str:
        """Create prompt for SQLCoder model using its recommended format."""
        
        # Add special instruction for HYBRID queries
        hybrid_instruction = ""
        if query_type == "HYBRID":
            hybrid_instruction = "\n            - **CRITICAL for ranking queries**: ALWAYS include c.titulo (content title) in SELECT clause"
        
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
            - For "most viewed" or "most popular" queries, use COUNT(*), GROUP BY, ORDER BY, and LIMIT{hybrid_instruction}
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
    
    def _create_default_prompt(self, user_query: str, schema: str, query_type: str = "SQL") -> str:
        """Create default prompt for general models."""
        
        # Add special instruction for HYBRID queries
        hybrid_instruction = ""
        if query_type == "HYBRID":
            hybrid_instruction = "\n            - CRITICAL: Include c.titulo (content title) in SELECT for ranking queries"
        
        return dedent(f"""
            You are a PostgreSQL expert. Generate ONLY a valid SQL query.
            
            Question: {user_query}
            
            Database Schema:
            {schema}
            
            Generate a PostgreSQL query. Rules:
            - Every non-aggregated column in SELECT must be in GROUP BY
            - Use COUNT(*), SUM(), AVG() for aggregations
            - Use ORDER BY with LIMIT for "top N" queries{hybrid_instruction}
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
            
            # Convert rows to list of dictionaries for easier access
            if results["success"] and results.get("columns") and results.get("rows"):
                columns = results["columns"]
                rows = results["rows"]
                
                # Convert to list of dicts
                results["results"] = [
                    dict(zip(columns, row)) for row in rows
                ]
                logger.info(f"Converted {len(results['results'])} rows to dictionary format")
            else:
                results["results"] = []
            
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
        For HYBRID queries: extracts content titles from SQL results and retrieves their PDFs.
        For RAG queries: does semantic search based on user query.
        """
        logger.info("Retrieving documents via RAG")
        
        if not self.rag_tool:
            error_msg = "RAG functionality not available"
            logger.error(error_msg)
            state["error"] = error_msg
            return state
        
        try:
            query_type = state.get("query_type")
            
            # For HYBRID queries, extract titles from SQL results
            if query_type == "HYBRID":
                logger.info("HYBRID query detected - extracting content titles from SQL results")
                titles = self._extract_titles_from_sql_results(state)
                
                if not titles:
                    logger.warning("No titles found in SQL results, falling back to semantic search")
                    rag_results = self.rag_tool.search(state['user_query'], top_k=3)
                else:
                    logger.info(f"Found {len(titles)} titles in SQL results: {titles}")
                    rag_results = self._retrieve_documents_by_titles(titles)
            else:
                # For RAG-only queries, use semantic search
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
    
    def _extract_titles_from_sql_results(self, state: AgentState) -> list:
        """
        Extract content titles from SQL query results.
        Looks for 'titulo' column in the results.
        
        Args:
            state: Current agent state with SQL results
            
        Returns:
            List of content titles
        """
        titles = []
        
        try:
            sql_results = state.get("sql_results", {})
            if not sql_results.get("success"):
                return titles
            
            results = sql_results.get("results", [])
            if not results:
                return titles
            
            # Check if 'titulo' column exists in results
            for row in results:
                if isinstance(row, dict) and 'titulo' in row:
                    title = row['titulo']
                    if title:
                        titles.append(str(title))
                        logger.debug(f"Extracted title: {title}")
            
            logger.info(f"Extracted {len(titles)} titles from SQL results")
            
        except Exception as e:
            logger.error(f"Error extracting titles from SQL results: {e}", exc_info=True)
        
        return titles
    
    def _retrieve_documents_by_titles(self, titles: list) -> dict:
        """
        Retrieve documents from RAG by specific content titles.
        
        Args:
            titles: List of content titles to retrieve
            
        Returns:
            Dictionary with success status, documents, and metadata (same format as rag_tool.search)
        """
        all_documents = []
        all_metadatas = []
        all_similarities = []
        
        for title in titles:
            try:
                # Try exact match first
                result = self.rag_tool.get_document_by_title(title)
                
                if result["success"]:
                    all_documents.append(result["document"])
                    all_metadatas.append(result.get("metadata", {"title": title}))
                    all_similarities.append(1.0)  # Exact match = 100% similarity
                    logger.info(f"Found exact match for title: {title}")
                else:
                    # If exact match fails, try semantic search with the title
                    logger.warning(f"Exact match failed for '{title}', trying semantic search")
                    search_result = self.rag_tool.search(title, top_k=1)
                    
                    if search_result["success"] and search_result["documents"]:
                        all_documents.extend(search_result["documents"])
                        all_metadatas.extend(search_result["metadatas"])
                        all_similarities.extend(search_result["similarities"])
                        logger.info(f"Found semantic match for title: {title}")
                    else:
                        logger.warning(f"No match found for title: {title}")
                        
            except Exception as e:
                logger.error(f"Error retrieving document for title '{title}': {e}", exc_info=True)
                continue
        
        if all_documents:
            return {
                "success": True,
                "documents": all_documents,
                "metadatas": all_metadatas,
                "similarities": all_similarities,
                "count": len(all_documents)
            }
        else:
            return {
                "success": False,
                "error": "No documents found for the specified titles",
                "documents": [],
                "metadatas": [],
                "similarities": [],
                "count": 0
            }
    
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
