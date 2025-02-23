# Text2SQL Assignment

- [LinkedIn - Rajarshi Roy](https://www.linkedin.com/in/rajarshi-roy-learner/)
  
- [Github - Rajarshi Roy](https://github.com/Rajarshi12321/)

- [Medium - Rajarshi Roy](https://medium.com/@rajarshiroy.machinelearning)
  
- [Mail - Rajarshi Roy](mailto:royrajarshi0123@gmail.com)
- [Personal-Website - Rajarshi Roy](https://rajarshi12321.github.io/rajarshi_portfolio/)


## Table of Contents

- [Text2SQL Assignment](#text2sql-assignment)
  - [Table of Contents](#table-of-contents)
  - [About The Project](#about-the-project)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Database Setup](#database-setup)
  - [Usage](#usage)
  - [OR](#or)
  - [Project Structure](#project-structure)
  - [Features](#features)
  - [Database Schema](#database-schema)
  - [Evaluation Function](#evaluation-function)
  - [Evaluation Results](#evaluation-results)
  - [Example Queries](#example-queries)
    - [Demo Example](#demo-example)
  - [Troubleshooting](#troubleshooting)
  - [Notes](#notes)
  - [License](#license)
  - [Contributing](#contributing)
  - [Contact](#contact)

## About The Project
A natural language to SQL query converter using Google's Gemini model, specifically designed for the Pagila database.

## Prerequisites

- Docker installed on your system
- Python 3.8 or higher
- Git (for cloning the repository)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Rajarshi12321/Text2SQLAssignment.git
cd Text2Sql-assignment
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Set up your Google API key:
   - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add it to your code:
Create a `.env` file in the root directory with the following content:
```
GOOGLE_API_KEY = "your-api-key-here"
LANGCHAIN_API_KEY = "your-api-key-here"
```

## Database Setup

1. Run the database setup script:
```bash
python setup_db.py
```
This will:
- Pull the PostgreSQL Docker image
- Create and start a PostgreSQL container
- Set up the Pagila database with schema and data

## Usage

1. Run the app.py file:
```bash
python app.py
```
--- 
OR
 ---
1. Run the Jupyter notebook:
```bash
jupyter notebook text2sql.ipynb
```

2. Use the text-to-SQL converter in two ways:

a. Simple approach:
```python
# Single query
natural_language_query = "Show me the top 5 customers who have rented the most movies"
sql = text_to_sql(natural_language_query)
results = execute_query(sql)
print("\nresults:", results)
```

b. Agent-based approach:
```python
# Using the agent executor
result = agent_executor.invoke({
    "input": natural_language_query,
    "sql_query": "",
    "final_query": ""
})
print("\nFinal SQL Query:", result["final_query"])
```

## Project Structure

- `app.py`: Main application file
- `text2sql.ipynb`: Main notebook containing the text-to-SQL conversion logic
- `setup_db.py`: Database setup and query execution utilities
- `requirements.txt`: Python package dependencies
- `pagila/`: Directory containing Pagila database SQL files

## Features

- Natural language to SQL conversion using Gemini model
- Query validation and correction
- Support for complex queries including:
  - Joins across multiple tables
  - Aggregations and grouping
  - Sorting and limiting results
- Comprehensive database schema support
- Error handling and query validation

## Database Schema

The Pagila database includes tables for:
- Customers and staff
- Films and actors
- Rentals and payments
- Store locations and inventory
- Categories and languages

## Evaluation Function

A LLM powered evaluation function is used to evaluate the accuracy of the SQL Query generated.

Prompt:
```python
 f""" 
        Check if the following SQL query correctly implements the given natural language request:

        NL Query: {nl_query}
        SQL Query: {sql_query}
        
        Provided Database Schema: 
        {DATABASE_SCHEMA}

        Provide a response indicating if it is logically correct, with reasoning.
        The scoring breakdown could be as follows:
        100 for fully correct queries.
        50 for queries that are logically correct but have minor errors.
        0 for queries that are incorrect or produce the wrong results
        
        The response should be in the following format:
        Score: 100
        Reasoning: The query is fully correct.
        Score: 50
        Reasoning: The query is logically correct but has minor errors. (with proper reasoning and improvements)
        Score: 0
        Reasoning: The query is incorrect or produces the wrong results. (with proper reasoning and improvements)
"""
```


## Evaluation Results

Average accuracy of the model is 100%

<img width="362" alt="image" src="https://github.com/user-attachments/assets/be502394-01d7-4e1b-8332-7a393dbc91e5" />


## Example Queries

```python
# Example queries you can try:
queries = [
    "Show me the top 5 customers who have rented the most movies",
    "List all movies in the Action category",
    "What is the average rental duration for each film category?"
]

for query in queries:
    sql = text_to_sql(query)
    results = execute_query(sql)
    print(f"\nQuery: {query}")
    print(f"results: {results}")
```



### Demo Example

Here's an example of converting a natural language query to SQL:

Function and example:

```python

# Update example usage
def process_query(natural_language_query: str, max_retries=5, show_print=False):
    attempt = 0
    error_message = ""

    state = {
        "input": natural_language_query,
        "sql_query": "",
        "final_query": "",
        "query_results": ""
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
                state["input"] = f"""{natural_language_query}\n\nPrevious Error list: {error_messages}"""
                attempt += 1
                continue  # Retry the process

            # If no error, return the successful result
            return sql_query, query_results

        except Exception as e:
            # print(f"Unexpected error in attempt {attempt + 1}: {str(e)}")
            attempt += 1

    print(f"\nMax retries reached. Last error: {error_message}")
    return None, None  # Return None if max retries are exceeded


# Test the processing
test_query = "Show me the top 5 customers who have rented the most movies"
sql, results = process_query(test_query,show_print=True)
```

Output:

```python

Attempt 1:

Natural Language Query:
 Show me the top 5 customers who have rented the most movies

Generated SQL:
 SELECT
    C.first_name,
    C.last_name,
    COUNT(R.rental_id) AS rental_count
FROM
    customer AS C
    JOIN rental AS R ON C.customer_id = R.customer_id
GROUP BY
    C.customer_id,
    C.first_name,
    C.last_name
ORDER BY
    rental_count DESC
LIMIT 5;

Query results:
  first_name | last_name | rental_count 
------------+-----------+--------------
 ELEANOR    | HUNT      |           46
 KARL       | SEAL      |           45
 MARCIA     | DEAN      |           42
 CLARA      | SHAW      |           42
 TAMMY      | SANDERS   |           41
(5 rows)

```

Here's an example of using the Gradio UI - app.py:



https://github.com/user-attachments/assets/5429700f-ace0-4548-a286-0dcd95a01dfc




## Troubleshooting

1. **Docker Issues**
   - Ensure Docker is running
   - Check container status: `docker ps`
   - Restart container: `python setup_db.py`

2. **Database Connection Issues**
   - Verify PostgreSQL container is running
   - Check port availability (default: 5432)
   - Ensure database credentials are correct

3. **API Key Issues**
   - Verify API keys in .env file
   - Check for proper environment variable loading

## Notes

- The system uses Google's Gemini model for natural language processing
- Queries are validated and optimized before execution
- results are formatted for clear display
- The inferenced dataset containing the natural language queries, generated SQL queries and their outputs is stored in `inferenced_results.csv`
- The CSV file includes columns for:
  - Query Number
  - Natural Language Query
  - Difficulty
  - Query
  - sql_gen_query
  - results
- The evaluation dataset containing reasoning, score for the SQL queries and their outputs is stored in `evaluation_results.csv`
- The CSV file includes columns for:
  - Query Number
  - Natural Language Query
  - Difficulty
  - Query
  - sql_gen_query
  - results
  - reasoning
  - score


## License

This project is licensed under the MIT License. Feel free to modify and distribute it as per the terms of the license.

I hope this README provides you with the necessary information to get started with the road to Generative AI with Google Gemini and Langchain.



## Contributing
I welcome contributions to improve the functionality and performance of the app. If you'd 
like to contribute, please follow these guidelines:

1. Fork the repository and create a new branch for your feature or bug fix.

2. Make your changes and ensure that the code is well-documented.

3. Test your changes thoroughly to maintain app reliability.

4. Create a pull request, detailing the purpose and changes made in your contribution.

## Contact

Rajarshi Roy - [royrajarshi0123@gmail.com](mailto:royrajarshi0123@gmail.com)
