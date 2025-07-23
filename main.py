import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.cli.fast_api import get_fast_api_app
from dotenv import load_dotenv

# Load environment variables (useful if you have other env vars not related to ADK's internal handling)
load_dotenv()

# --- Configuration for get_fast_api_app ---
# Get the directory where main.py is located. This is now the project root.
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Specify the directory containing your ADK agent(s).
# In your new structure, 'quickstart_agent' is directly under the root.
AGENT_CODE_DIR = os.path.join(AGENT_DIR, "quickstart_agent")

# Example session service URI (e.g., SQLite for local development/simple deployment).
# For production and multi-user applications, consider a persistent database like Firestore.
SESSION_SERVICE_URI = "sqlite:///./sessions.db"

# Allowed origins for Cross-Origin Resource Sharing (CORS).
# IMPORTANT: In a production environment, restrict "*" to your actual frontend URLs.
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]

# Set web=True if you intend to serve a web interface (like ADK's default UI), False otherwise.
# Setting to True serves a default UI on the root path ('/').
# Set to False if you want your custom routes (like '/') to be the primary interface.
SERVE_WEB_INTERFACE = False

# Call the function to get the FastAPI app instance.
# This function automatically sets up the ADK Runner and exposes the /predict endpoint.
app = get_fast_api_app(
    agents_dir=AGENT_CODE_DIR, # Point to the specific agent folder
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# You can add custom FastAPI routes here if you need additional API endpoints
# beyond what ADK's get_fast_api_app provides (e.g., a custom health check).

@app.get("/", summary="Health Check")
async def health_check():
    """
    Checks if the API is running and healthy.
    This is a custom health check, separate from ADK's functionality.
    """
    return {"status": "healthy", "message": "ADK Weather and Time Agent is up!"}

# The /predict endpoint is now automatically handled by get_fast_api_app.
# You do NOT need to define it manually here.
# If you try to define it, it will conflict or cause unexpected behavior.

if __name__ == "__main__":
    # Cloud Run automatically provides the PORT environment variable
    # If running locally, it defaults to 8080
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
