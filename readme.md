# Text2SQL Assignment

- [LinkedIn - Rajarshi Roy](https://www.linkedin.com/in/rajarshi-roy-learner/)
  
- [Github - Rajarshi Roy](https://github.com/Rajarshi12321/)

- [Medium - Rajarshi Roy](https://medium.com/@rajarshiroy.machinelearning)
  
- [Kaggle - Rajarshi Roy](https://www.kaggle.com/rajarshiroy0123/)
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
  - [Project Structure](#project-structure)
  - [Features](#features)
  - [Database Schema](#database-schema)
  - [Example Queries](#example-queries)
  - [Troubleshooting](#troubleshooting)
  - [Contributing](#contributing)
  - [Contact](#contact)
  - [License](#license)


## About The Project
A natural language to SQL query converter using Google's Gemini model, specifically designed for the Pagila database.

## Prerequisites

- Docker installed on your system
- Python 3.8 or higher
- Git (for cloning the repository)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Text2Sql-assignment
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
pip install langchain-core==0.2.22
pip install langchain-google-genai==1.0.8
pip install langgraph
```

3. Set up your Google API key:
   - Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Add it to your code:
```python
import os
os.environ["GOOGLE_API_KEY"] = "your-api-key-here"
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
print("\nResults:", results)
```

b. Agent-based approach:
```python
# Using the agent executor
result = agent_executor.invoke({
    "input": natural_language_query,
    "database_schema": DATABASE_SCHEMA,
    "sql_query": "",
    "final_query": ""
})
print("\nFinal SQL Query:", result["final_query"])
```

## Project Structure

- `text2sql.ipynb`: Main notebook containing the text-to-SQL conversion logic
- `setup_db.py`: Database setup and query execution utilities
- `requirements.txt`: Python package dependencies
- `pagila/`: Directory containing Pagila database SQL files

## Features

- Natural language to SQL conversion using Google's Gemini model
- PostgreSQL compatibility with syntax validation
- Support for complex queries with joins and aggregations
- Error handling and query validation
- Docker-based database setup for reproducibility

## Database Schema

The Pagila database includes tables for:
- Customers and staff
- Films and actors
- Rentals and payments
- Store locations and inventory
- Categories and languages

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
    print(f"Results: {results}")
```

## Troubleshooting

1. If Docker container fails to start:
```bash
python setup_db.py  # This will restart the container
```

2. If you get API key errors:
- Verify your Google API key is valid
- Ensure the environment variable is set correctly

3. For database connection issues:
- Check if Docker is running
- Verify PostgreSQL container is up (`docker ps`)
- Check port 5432 is available



## Contributing
I welcome contributions to improve the functionality and performance of the app. If you'd like to contribute, please follow these guidelines:

1. Fork the repository and create a new branch for your feature or bug fix.

2. Make your changes and ensure that the code is well-documented.

3. Test your changes thoroughly to maintain app reliability.

4. Create a pull request, detailing the purpose and changes made in your contribution.

## Contact

Rajarshi Roy - [royrajarshi0123@gmail.com](mailto:royrajarshi0123@gmail.com)



## License
This project is licensed under the MIT License. Feel free to modify and distribute it as per the terms of the license.

I hope this README provides you with the necessary information to get started with the road to Generative AI with Google Gemini and Langchain.