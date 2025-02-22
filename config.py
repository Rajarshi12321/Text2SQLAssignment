## config.py
import os

gemini_api_key = os.getenv("GEMINI_API_KEY", "your_gemini_api_key")
db_config = {
    "dbname": "pagila",
    "user": "postgres",
    "password": "yourpassword",
    "host": "localhost"
}
