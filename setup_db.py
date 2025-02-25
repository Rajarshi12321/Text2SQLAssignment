import subprocess
import os
import time
import platform  # Add this import at the top


# SQL queries
QUERIES = {
    "list_tables": """SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name""",
    "check_schema": """SELECT current_database(), current_schema""",
    "check_permissions": """SELECT usename, usesuper, usecreatedb FROM pg_user""",
    "check_database": """SELECT datname FROM pg_database""",
}


def setup_pagila_database():
    """Sets up the pagila database using SQL files"""
    try:
        time.sleep(3)  # Wait for the container to be ready
        # Check if database exists
        check_db = subprocess.run(
            """docker exec -i postgres psql -U postgres -t -c "SELECT datname FROM pg_database WHERE datname='pagila';""",
            shell=True,
            text=True,
            capture_output=True,
        )
        # # Print running containers
        # print("\nRunning containers:")
        # subprocess.run("docker ps -a", shell=True, check=True)
        # print("\n\n")
        if "pagila" not in check_db.stdout:
            print("Creating pagila database...")
            subprocess.run(
                'docker exec -i postgres psql -U postgres -c "CREATE DATABASE pagila;"',
                shell=True,
                check=True,
            )
        else:
            print("Database 'pagila' already exists, skipping creation...")
        # Check if schema exists by checking for tables
        check_schema = subprocess.run(
            """docker exec -i postgres psql -U postgres -d pagila -c "\dt" """,
            shell=True,
            text=True,
            capture_output=True,
        )

        # Modified schema loading for Windows compatibility
        if not check_schema.stdout.strip():
            print("Loading pagila schema...")
            try:
                print("Platform:", platform.system())
                # Use different commands based on OS
                if platform.system() == "Windows":
                    subprocess.run(
                        "docker exec -i postgres psql -U postgres -d pagila < pagila/pagila-schema.sql",
                        shell=True,
                        check=True,
                    )
                else:
                    # Original Unix command
                    subprocess.run(
                        "cat pagila/pagila-schema.sql | docker exec -i postgres psql -U postgres -d pagila",
                        shell=True,
                        check=True,
                    )
            except subprocess.CalledProcessError as e:
                print(f"Error loading schema: {e}")
                raise

        else:
            print("Schema already exists, skipping schema load...")

        # Check if data exists by counting rows in actor table
        check_data = subprocess.run(
            """docker exec -i postgres psql -U postgres -d pagila -t -c "SELECT COUNT(*) FROM actor;" """,
            shell=True,
            text=True,
            capture_output=True,
        )

        # Check if data exists
        if check_data.stdout.strip() == "0":

            print("Loading pagila data...")
            try:
                print("Platform:", platform.system())
                # Use different commands based on OS
                if platform.system() == "Windows":
                    subprocess.run(
                        "docker exec -i postgres psql -U postgres -d pagila < pagila/pagila-data.sql",
                        shell=True,
                        check=True,
                    )
                else:
                    # Original Unix command
                    subprocess.run(
                        "cat pagila/pagila-data.sql | docker exec -i postgres psql -U postgres -d pagila",
                        shell=True,
                        check=True,
                    )
            except subprocess.CalledProcessError as e:
                print(f"Error loading data: {e}")
                raise
        else:
            print("Data already exists, skipping data load...")

        print("Pagila database setup completed successfully!")

    except subprocess.CalledProcessError as e:
        print(f"Error setting up database: {e}")
    except FileNotFoundError as e:
        print(f"SQL file not found: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def execute_query(query):
    """Runs a SQL query inside the Docker container."""
    # Escape double quotes in the query and wrap the entire query in double quotes
    escaped_query = query.replace('"', '\\"').strip()
    docker_command = (
        f"""docker exec -i postgres psql -U postgres -d pagila -c "{escaped_query}" """
    )

    try:
        result = subprocess.run(
            docker_command, shell=True, check=True, text=True, capture_output=True
        )
        # print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running query: {e.stderr}")
        return e.stderr


def restart_postgres_container():
    """Stops any running postgres container and starts a new one"""
    try:
        # Check if postgres image exists
        check_image = subprocess.run(
            "docker images postgres --format '{{.Repository}}'",
            shell=True,
            text=True,
            capture_output=True,
        )

        if not check_image.stdout.strip():
            print("Postgres image not found, pulling from Docker Hub...")
            subprocess.run("docker pull postgres", shell=True, check=True)
            print("Successfully pulled postgres image")
        # Check for existing container (running or stopped)
        check_container = subprocess.run(
            "docker ps -a -f name=postgres", shell=True, text=True, capture_output=True
        )

        # Print the output of the check_container command
        print("Check", check_container.stdout)

        if "postgres" in check_container.stdout.strip():
            print("Found existing postgres container...")
            # Get container status
            status = subprocess.run(
                "docker inspect -f '{{.State.Running}}' postgres",
                shell=True,
                text=True,
                capture_output=True,
            )
            # The container status comes with quotes, so we need to strip them
            container_status = status.stdout.strip().lower().strip("'")
            print(f"Container status: {container_status}")
            if container_status == "true":
                print("Stopping running postgres container...")
                subprocess.run("docker stop postgres", shell=True, check=True)

            print("Removing existing postgres container...")
            subprocess.run("docker rm postgres", shell=True, check=True)

        # Start new container
        print("Starting new postgres container...")
        subprocess.run(
            "docker run --name postgres -e POSTGRES_PASSWORD=secret -p 5432:5432 -d postgres",
            shell=True,
            check=True,
        )

        # Wait for container to be ready
        print("Waiting for container to be ready...")

        # Verify container is running
        verify = subprocess.run(
            "docker ps -f name=postgres --format '{{.Status}}'",
            shell=True,
            text=True,
            capture_output=True,
        )

        if "Up" in verify.stdout:
            print("Postgres container started successfully!")
        else:
            raise Exception("Container failed to start properly")

    except subprocess.CalledProcessError as e:
        print(f"Error managing container: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    # First setup the database
    restart_postgres_container()
    time.sleep(10)  # Wait for the container to be ready
    setup_pagila_database()

    print("\n=== Checking current database and schema ===")
    print(execute_query(QUERIES["check_schema"]))

    print("\n=== Checking database existence ===")
    print(execute_query(QUERIES["check_database"]))

    print("\n=== Checking user permissions ===")
    print(execute_query(QUERIES["check_permissions"]))

    print("\n=== Listing all tables in public schema ===")
    print(execute_query(QUERIES["list_tables"]))
