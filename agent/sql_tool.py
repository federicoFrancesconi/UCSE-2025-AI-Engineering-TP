"""
SQL Tool for executing SQL queries against the streaming database.
This tool validates, executes, and returns results from SQL queries.
"""

import logging
import re
from textwrap import dedent
from typing import Dict, List, Any, Optional, Tuple
import psycopg2
from psycopg2 import sql, Error as PostgresError
import sqlparse
from tabulate import tabulate

logger = logging.getLogger(__name__)


class SQLTool:
    """Tool for executing SQL queries with validation and schema awareness."""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Initialize SQL Tool with database configuration.
        
        Args:
            db_config: Dictionary with database connection parameters
        """
        self.db_config = db_config
        self.schema_cache = None
        logger.info("SQLTool initialized")
    
    def get_database_schema(self) -> str:
        """
        Retrieve the complete database schema for context.
        
        Returns:
            String representation of the database schema in CREATE TABLE format
        """
        if self.schema_cache:
            return self.schema_cache
        
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            schema_parts = []
            
            # Get all tables
            cursor.execute(dedent("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """))
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                # Start CREATE TABLE statement
                schema_parts.append(f"\nCREATE TABLE {table_name} (")
                
                # Get columns for each table
                cursor.execute(dedent("""
                    SELECT 
                        column_name, 
                        data_type,
                        character_maximum_length,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_name = %s 
                    ORDER BY ordinal_position;
                """), (table_name,))
                
                columns = cursor.fetchall()
                column_defs = []
                
                for col_name, data_type, char_max_len, is_nullable, col_default in columns:
                    # Format data type with length if applicable
                    if char_max_len and data_type == 'character varying':
                        type_str = f"VARCHAR({char_max_len})"
                    elif data_type == 'integer':
                        type_str = "INTEGER"
                    elif data_type == 'timestamp without time zone':
                        type_str = "TIMESTAMP"
                    elif data_type.startswith('numeric'):
                        type_str = data_type.upper()
                    else:
                        type_str = data_type.upper()
                    
                    # Build column definition
                    col_def = f"  {col_name} {type_str}"
                    
                    # Add constraints
                    if col_default and 'nextval' in col_default:
                        col_def += " PRIMARY KEY"  # Typically SERIAL columns
                    elif is_nullable == "NO":
                        col_def += " NOT NULL"
                    
                    column_defs.append(col_def)
                
                schema_parts.append(",\n".join(column_defs))
                schema_parts.append(");")
                
                # Add foreign key information as comments
                cursor.execute(dedent("""
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                        AND tc.table_name = %s;
                """), (table_name,))
                
                fkeys = cursor.fetchall()
                if fkeys:
                    for col, ref_table, ref_col in fkeys:
                        schema_parts.append(f"-- {table_name}.{col} can be joined with {ref_table}.{ref_col}")
            
            cursor.close()
            conn.close()
            
            self.schema_cache = "\n".join(schema_parts)
            logger.info("Database schema retrieved and cached")
            return self.schema_cache
            
        except PostgresError as e:
            error_msg = f"Error retrieving database schema: {str(e)}"
            logger.error(error_msg)
            return error_msg
    
    def validate_sql(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query for safety and correctness.
        
        Args:
            query: SQL query string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Parse and format the query
        try:
            parsed = sqlparse.parse(query)
            if not parsed:
                return False, "Empty or invalid SQL query"
            
            # Get the first statement
            statement = parsed[0]
            
            # Check if it's a SELECT statement
            first_token = statement.token_first(skip_ws=True, skip_cm=True)
            if not first_token or first_token.ttype is not sqlparse.tokens.Keyword.DML:
                return False, "Query must be a DML statement"
            
            if first_token.value.upper() != 'SELECT':
                return False, "Only SELECT queries are allowed"
            
            # Check for dangerous patterns
            query_upper = query.upper()
            dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    return False, f"Dangerous keyword '{keyword}' detected. Only SELECT queries are allowed."
            
            # Check for multiple statements (SQL injection attempt)
            if len(parsed) > 1:
                return False, "Multiple SQL statements are not allowed"
            
            logger.info("SQL query validated successfully")
            return True, None
            
        except Exception as e:
            error_msg = f"SQL validation error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results.
        
        Args:
            query: SQL query to execute
            
        Returns:
            Dictionary with execution results or error information
        """
        logger.info(f"Executing SQL query: {query}")
        
        # Validate query first
        is_valid, validation_error = self.validate_sql(query)
        if not is_valid:
            logger.error(f"Query validation failed: {validation_error}")
            return {
                "success": False,
                "error": validation_error,
                "query": query
            }
        
        try:
            # Connect to database
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Execute query
            cursor.execute(query)
            
            # Fetch results
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Close connection
            cursor.close()
            conn.close()
            
            logger.info(f"Query executed successfully. Returned {len(rows)} rows")
            
            return {
                "success": True,
                "query": query,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows)
            }
            
        except PostgresError as e:
            error_msg = f"Database error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "query": query
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "query": query
            }
    
    def format_results(self, results: Dict[str, Any]) -> str:
        """
        Format query results for display.
        
        Args:
            results: Dictionary with query results
            
        Returns:
            Formatted string representation of results
        """
        if not results["success"]:
            return f"❌ Error: {results['error']}"
        
        if results["row_count"] == 0:
            return "✓ Query executed successfully but returned no results."
        
        # Create table with tabulate
        table = tabulate(
            results["rows"],
            headers=results["columns"],
            tablefmt="grid",
            maxcolwidths=50
        )
        
        return f"✓ Query returned {results['row_count']} row(s):\n\n{table}"
