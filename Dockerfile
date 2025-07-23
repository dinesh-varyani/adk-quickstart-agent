# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables to ensure Python output is unbuffered
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy just the requirements file from the 'app' directory into the container's /app directory.
# This allows Docker to cache the pip install layer efficiently.
COPY app/requirements.txt .

# Install any needed dependencies specified in requirements.txt
# Added -v for verbose output during pip install for better debugging
# Added 'set -euxo pipefail' to ensure the script exits immediately on any error if pip fails
RUN set -euxo pipefail && pip install --no-cache-dir -r requirements.txt -v

# Attempt to uninstall gunicorn if it was somehow installed (e.g., as a transitive dependency
# or part of the base image that conflict with ASGI startup).
# This is a defensive measure to ensure only Uvicorn is running.
RUN pip uninstall -y gunicorn || echo "gunicorn not found or unable to uninstall, skipping."

# Copy the entire contents of your local 'app' directory into the container's /app directory.
# This ensures main.py is directly at /app/main.py and other modules (like quickstart_agent) are accessible.
COPY app/ .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable for FastAPI to tell Uvicorn where to find the app
# Since main.py is now at /app/main.py, 'main:app' is correct.
ENV APP_MODULE=main:app

# Command to run the application using Uvicorn, explicitly calling it as a Python module
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
