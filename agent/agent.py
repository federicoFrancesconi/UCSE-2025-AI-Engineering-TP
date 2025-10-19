"""
LangGraph-based SQL AI Agent for natural language to SQL translation.
"""

import logging
import os
from textwrap import dedent
from typing import TypedDict, Annotated, Sequence
from langchain_community.llms import Ollama
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import Graph, StateGraph, END
from langgraph.prebuilt import ToolExecutor
import operator

from sql_tool import SQLTool

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State of the agent graph."""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_query: str
    sql_query: str
    sql_results: dict
    formatted_response: str
    error: str


class SQLAgent:
    """SQL AI Agent using LangGraph for orchestration."""
    
    def __init__(
        self,
        db_config: dict,
        ollama_base_url: str,
        sql_model: str,
        conversation_model: str
    ):
        """
        Initialize the SQL Agent.
        
        Args:
            db_config: Database configuration dictionary
            ollama_base_url: Base URL for Ollama API
            sql_model: Model name for SQL generation
            conversation_model: Model name for conversation
        """
        self.sql_tool = SQLTool(db_config)
        self.ollama_base_url = ollama_base_url
        self.sql_model = sql_model
        self.conversation_model = conversation_model
        
        # Initialize LLMs
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
        workflow.add_node("generate_sql", self._generate_sql)
        workflow.add_node("execute_sql", self._execute_sql)
        workflow.add_node("format_response", self._format_response)
        workflow.add_node("handle_error", self._handle_error)
        
        # Set entry point
        workflow.set_entry_point("understand_query")
        
        # Add edges
        workflow.add_edge("understand_query", "generate_sql")
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
                "error": "handle_error"
            }
        )
        workflow.add_edge("format_response", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    def _understand_query(self, state: AgentState) -> AgentState:
        """
        Node: Understand and validate the user query.
        """
        logger.info(f"Understanding query: {state['user_query']}")
        
        # For now, just pass through - can add query classification later
        state["messages"] = [HumanMessage(content=state["user_query"])]
        
        return state
    
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
        
        # Create prompt for SQL generation following Ollama's recommended format for SQLCoder
        system_prompt = dedent(f"""
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
        
        try:
            # Generate SQL using the SQL-specialized model
            logger.info(f"Calling SQL model: {self.sql_model}")
            sql_query = self.sql_llm.invoke(system_prompt)
            logger.info(f"Raw SQL response: {sql_query}")
            
            # Clean up the response
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
            
            # Sometimes SQLCoder adds explanatory text - try to extract just the SELECT statement
            if "\n\n" in sql_query or ". " in sql_query:
                # Look for SELECT statement
                lines = sql_query.split("\n")
                for i, line in enumerate(lines):
                    if line.strip().upper().startswith("SELECT"):
                        # Take from SELECT to the end or until we hit explanatory text
                        sql_query = " ".join(lines[i:])
                        break
            
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
        Node: Format the SQL results into a natural language response.
        """
        logger.info("Formatting response")
        
        try:
            # Format results as table
            formatted_results = self.sql_tool.format_results(state["sql_results"])
            
            # Create conversational response
            prompt = dedent(f"""
                You are a helpful AI assistant for a streaming platform.

                The user asked: "{state['user_query']}"

                The following SQL query was executed:
                {state['sql_query']}

                Results:
                {formatted_results}

                Provide a brief, friendly summary of the results in natural language. Be concise but informative.
                If there are many results, highlight the most relevant ones.

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
            return "format"
        return "error"
    
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
            "sql_query": "",
            "sql_results": {},
            "formatted_response": "",
            "error": ""
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return {
            "response": final_state.get("formatted_response", ""),
            "sql_query": final_state.get("sql_query", ""),
            "results": final_state.get("sql_results", {}),
            "error": final_state.get("error", "")
        }
