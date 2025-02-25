# !pip install -r requirements.txt
## 1. Database Schema and Configuration
import os
import google.generativeai as genai
from setup_db import execute_query
from config import (
    GOOGLE_API_KEY,
    DATABASE_SCHEMA,
    COT_TEXT2SQL_EXAMPLE,
    LANGCHAIN_API_KEY,
)

import re
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
from langchain.tools import Tool
from langchain.schema import HumanMessage
from typing import TypedDict, Annotated, Sequence, Union
from typing import List, Tuple, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage


genai.configure(api_key=GOOGLE_API_KEY)

os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "text2sql"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

## 2. Core Text-to-SQL Functions

# Load LLMs
llm_sql_generator = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite-preview-02-05")
llm_sql_validator = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite-preview-02-05")


# Extract SQL from the model response
def extract_sql(text):
    match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL)
    return match.group(1) if match else text


# Tool 1: Generate SQL Query
def generate_sql(
    natural_language_query,
    DATABASE_SCHEMA=DATABASE_SCHEMA,
    COT_TEXT2SQL_EXAMPLE=COT_TEXT2SQL_EXAMPLE,
):
    """Agent to generate SQL from a natural language question."""
    prompt = f"""
    Properly use the Database Schema to properly use the table names and column names for respective tables.
    
    Database Schema:
    {DATABASE_SCHEMA}

    **************************
    Properly use the Database Schema to generate the SQL query.
    Answer Repeating the question and evidence, and generating the SQL with a query plan.
    
    <---(Example)--->
    {COT_TEXT2SQL_EXAMPLE}
    
    Only return the SQL query without ``` backticks, no other text. 
    Ensure the table alias is correctly assigned
    
    
    ---------------------------------
    Question: {natural_language_query}

    SQL Query: 
    """
    response = llm_sql_generator.invoke([HumanMessage(content=prompt)])
    return extract_sql(response.content)


# Tool 2: Validate and Fix SQL Query for PostgreSQL
def validate_and_fix_sql(sql_query, DATABASE_SCHEMA=DATABASE_SCHEMA):
    """Agent to validate and correct SQL syntax for PostgreSQL."""
    prompt = f"""
    The following SQL query might have syntax issues. Your task is to analyze it and correct any mistakes 
    so that it works properly in **PostgreSQL**.
    
    Properly use the Database Schema to generate the SQL query.
    Database Schema:
    {DATABASE_SCHEMA}

    Incorrect SQL:
    {sql_query}

    Return only the corrected SQL query without any explanations or ``` backticks.
    
    Make sure to use "ILIKE" instead of "=" for case insensitive matching. If not asked to be case sensitive
    Only while using "ILIKE" make sure to use "::TEXT" to avoid type mismatch errors.
    Don't use "::TEXT" while using "=" or anyother time
    

    Corrected SQL Query:
    """
    response = llm_sql_validator.invoke([HumanMessage(content=prompt)])
    return extract_sql(response.content)


# Define state type
class AgentState(TypedDict):
    input: str
    sql_query: str
    final_query: str
    query_results: str  # Add this field


# Define nodes with updated configuration
def generate_sql_node(state: AgentState) -> AgentState:
    """Generate initial SQL query"""
    try:
        sql_query = generate_sql(
            natural_language_query=state["input"],
            DATABASE_SCHEMA=DATABASE_SCHEMA,
            COT_TEXT2SQL_EXAMPLE=COT_TEXT2SQL_EXAMPLE,
        )
        state["sql_query"] = sql_query
        return state
    except Exception as e:
        print(f"Error in generate_sql_node: {str(e)}")
        raise


def validate_sql_node(state: AgentState) -> AgentState:
    """Validate and fix SQL query"""
    try:
        final_query = validate_and_fix_sql(state["sql_query"])
        state["final_query"] = final_query
        return state
    except Exception as e:
        print(f"Error in validate_sql_node: {str(e)}")
        raise


def execute_sql_node(state: AgentState) -> AgentState:
    """Execute the SQL query and store results"""
    try:
        query_results = execute_query(state["final_query"].replace("\n", " "))
        state["query_results"] = query_results
        return state
    except Exception as e:
        print(f"Error in execute_sql_node: {str(e)}")
        raise


# Create workflow
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("generate_sql", generate_sql_node)
workflow.add_node("validate_sql", validate_sql_node)
workflow.add_node("execute_sql", execute_sql_node)  # Add new node

# Add edges
workflow.add_edge("generate_sql", "validate_sql")
workflow.add_edge("validate_sql", "execute_sql")  # Add edge to new node
workflow.add_edge("execute_sql", END)  # Update final edge

# Set entry point
workflow.set_entry_point("generate_sql")

# Compile
agent_executor = workflow.compile()


# Update example usage
def process_query(natural_language_query: str, max_retries=5, show_print=True):
    attempt = 0
    error_message = ""

    state = {
        "input": natural_language_query,
        "sql_query": "",
        "final_query": "",
        "query_results": "",
    }

    error_messages = []
    while attempt < max_retries:
        # print(f"Attempt {attempt + 1}:{error_messages}")
        try:
            result = agent_executor.invoke(state)

            # Extract query and results
            sql_query = result["final_query"]
            query_results = result["query_results"]

            if show_print:
                print(f"\nAttempt {attempt + 1}:")
                print("\nNatural Language Query:\n", state["input"])
                print("\nGenerated SQL:\n", sql_query)
                print("\nQuery results:\n", query_results)

            # Check if the result contains an error
            if "ERROR" in query_results.upper():
                # Extract the error message
                error_message = query_results  # Full error message
                error_messages.append(error_message)
                # Prepare the retry prompt
                state["input"] = (
                    f"""{natural_language_query}\n\nPrevious Error list: {error_messages}"""
                )
                attempt += 1
                continue  # Retry the process

            # If no error, return the successful result
            return sql_query, query_results

        except Exception as e:
            # print(f"Unexpected error in attempt {attempt + 1}: {str(e)}")
            attempt += 1

    print(f"\nMax retries reached. Last error: {error_message}")
    return None, None  # Return None if max retries are exceeded


# # Test the processing
# test_query = "Show me the top 5 customers who have rented the most movies"
# # test_query = "Show all staff members hired before January 1, 2020."
# # test_query = "Show all staff members hired before January 1, 2020., create_date is not in staff table"
# sql, results = process_query(test_query,show_print=True)


llm_query_validator = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite-preview-02-05"
)


def string_to_dict(text):
    """
    Converts a JSON-like structured string into a dictionary, handling extra formatting.

    Args:
        text (str): Input string containing key-value pairs.

    Returns:
        dict: Dictionary with extracted key-value pairs.
    """

    # Remove code block markers like ```python and ```
    cleaned_text = re.sub(r"```[\w]*", "", text).strip()

    # Remove trailing commas before closing braces
    cleaned_text = re.sub(r",\s*}", "}", cleaned_text)

    # Convert to dictionary
    data_dict = json.loads(cleaned_text)

    try:
        return data_dict
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format")


# Validate Natural Language Query
def validate_nl_query(natural_language_query, user_instructions=None):
    """Agent to validate and improve natural language query."""
    prompt = f"""
    
    "JUST OUTPUT THE Python DICTIONARY of texts of natural language query"
    You are a helpful assistant that validates natural language queries for a Database.
    Your task is to analyze the query for ambiguity, incompleteness, or incorrectness and improve it if needed.
    You are also allowed to use the database schema to improve the query.

    User Instructions:
    {user_instructions}

    Database Schema:
    {DATABASE_SCHEMA}
    
    Natural Language Query:
    {natural_language_query}
    
    If the query is clear and complete, return it unchanged.
    If the query needs improvement, provide the improved version and explain why.
    Make sure to return the corrected input, the improved query and the feedback.
    Make sure to not alter the original query too much, if there is no typo or discrepancy with database schema. 
    
    
    In the following Format - For example:
    original_query: show moveis with actr smith
    corrected_input: show movies with actor smith
    feedback: Fixed typos in 'movies' and 'actor', added specificity about searching by last name
    
    original_query: show all movies with rating R
    corrected_input: show all movies with rating R
    feedback: Query is clear and well-formed, minor rewording for consistency
    
    original_query: list customer payments
    corrected_input: list customer payments
    feedback: Query is clear and grammatically correct   
    
    Output Format (make sure say why we changed what, if changed): 
    ```python
    {{
        original_query: show moveis with actr smith
        corrected_input: show movies with actor smith
        feedback: Fixed typos in 'movies' and 'actor'
    }}
    ```
    

    """
    response = llm_query_validator.invoke([HumanMessage(content=prompt)])

    print(response.content)
    return string_to_dict(response.content)
