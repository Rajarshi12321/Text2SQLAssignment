import gradio as gr
import google.generativeai as genai
from setup_db import execute_query
from config import (
    GOOGLE_API_KEY,
    DATABASE_SCHEMA,
    COT_TEXT2SQL_EXAMPLE,
    LANGCHAIN_API_KEY,
    EXAMPLE_QUERIES,
)
import os
from langchain_google_genai import ChatGoogleGenerativeAI
import re
import pandas as pd
from text2sql import process_query, validate_nl_query

# Configure API keys
genai.configure(api_key=GOOGLE_API_KEY)
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "text2sql"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"


LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "text2sql")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")


def process_input_query(query, choice):
    """Process the query and return results"""
    try:
        # Use example if selected
        query_text = query if choice == "Use example query" else query

        # Use the imported process_query function
        sql, results = process_query(query_text)

        # Format results as DataFrame
        if results:
            results_lines = results.strip().split("\n")
            if len(results_lines) > 2:
                headers = [h.strip() for h in results_lines[0].split("|")]
                data = []
                for line in results_lines[2:]:
                    if "|" in line:
                        row = [cell.strip() for cell in line.split("|")]
                        data.append(row)
                df = pd.DataFrame(data, columns=headers)
            else:
                df = pd.DataFrame({"results": ["No results found"]})
        else:
            df = pd.DataFrame({"Error": ["Error executing query"]})

        return sql, df
    except Exception as e:
        return str(e), pd.DataFrame({"Error": [str(e)]})


def create_interface():
    """Create the Gradio interface"""

    with gr.Blocks(title="Text to SQL Converter") as app:
        gr.Markdown("# Text to SQL Converter")
        gr.Markdown(
            "Convert natural language questions to SQL queries for the Pagila database"
        )

        with gr.Row():
            with gr.Column():
                # Query input methods
                query_type = gr.Radio(
                    choices=["Type custom query", "Use example query"],
                    label="Choose input method",
                    value="Type custom query",
                )

                # Custom query input
                custom_query = gr.Textbox(
                    label="Enter your question",
                    placeholder="Type your question here...",
                    lines=3,
                )

                # Example query dropdown
                example_query = gr.Dropdown(
                    choices=EXAMPLE_QUERIES,
                    label="Select an example query",
                    visible=False,
                )

                # Submit button
                submit_btn = gr.Button("Convert to SQL")

            with gr.Column():
                # Output displays
                query_feedback = gr.Markdown(label="Query Feedback")
                with gr.Row():
                    confirm_btn = gr.Button("Use this validated query", visible=False)
                    revalidate_btn = gr.Button("Validate query again", visible=False)

                # User suggestion input for revalidation
                user_suggestion = gr.Textbox(
                    label="Suggest your own correction (optional)",
                    placeholder="Modify the improved query if needed...",
                    visible=False,
                    lines=2,
                )

                improved_query_holder = (
                    gr.State()
                )  # Hidden state to store improved query
                sql_output = gr.Code(label="Generated SQL Query", language="sql")
                results_output = gr.Dataframe(label="Query results", wrap=True)

        # Show database schema
        with gr.Accordion("View Database Schema", open=False):
            gr.Code(value=DATABASE_SCHEMA, language="sql")

        # Handle query type selection
        def toggle_input(choice):
            return {
                custom_query: gr.update(visible=choice == "Type custom query"),
                example_query: gr.update(visible=choice == "Use example query"),
            }

        query_type.change(
            toggle_input, inputs=[query_type], outputs=[custom_query, example_query]
        )

        # Handle query submission
        def handle_submit(query_text, example_text, choice):
            query = example_text if choice == "Use example query" else query_text

            print(f"\nQuery: {query}")
            # First validate the query
            validation_result = validate_nl_query(query)
            original_query = validation_result["original_query"]
            improved_query = validation_result["corrected_input"]
            feedback = validation_result["feedback"]

            # Allow user input if improved query is different
            show_buttons = improved_query.lower() != query.lower()
            feedback_text = (
                f"Original Query: {original_query}\n\n\nImproved Query: {improved_query}\n\n\nFeedback: {feedback}"
                if feedback
                else f"Original Query: {query}\n\n\nNo changes needed."
            )

            return (
                feedback_text,
                gr.update(visible=True),  # Show confirm button
                gr.update(visible=True),  # Show revalidate button
                gr.update(visible=show_buttons),  # Show user suggestion input
                improved_query,
                "",
                None,
            )

        # Handle confirmation
        def process_confirmed_query(improved_query):
            sql, results = process_input_query(improved_query, "Type custom query")
            return sql, results

        # Handle revalidation
        def revalidate_query(query_text, example_text, choice, user_suggestion):
            # If user provided a suggestion, use that instead
            modified_query = (
                f"User Instructions: {user_suggestion}\n\n{query_text}"
                if user_suggestion
                else query_text
            )
            print(f"\nModified Query: {modified_query}")
            return handle_submit(modified_query, example_text, choice)

        submit_btn.click(
            handle_submit,
            inputs=[custom_query, example_query, query_type],
            outputs=[
                query_feedback,
                confirm_btn,
                revalidate_btn,
                user_suggestion,
                improved_query_holder,
                sql_output,
                results_output,
            ],
        )

        confirm_btn.click(
            process_confirmed_query,
            inputs=[improved_query_holder],
            outputs=[sql_output, results_output],
        )

        revalidate_btn.click(
            revalidate_query,
            inputs=[custom_query, example_query, query_type, user_suggestion],
            outputs=[
                query_feedback,
                confirm_btn,
                revalidate_btn,
                user_suggestion,
                improved_query_holder,
                sql_output,
                results_output,
            ],
        )

    return app


if __name__ == "__main__":
    app = create_interface()
    app.launch(share=True)
