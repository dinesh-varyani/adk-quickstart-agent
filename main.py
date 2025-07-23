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
# Be aware that setting to True might serve a default UI on the root path ('/').
SERVE_WEB_INTERFACE = False # Set to False if you want full control over your routes

# Call the function to get the FastAPI app instance
app = get_fast_api_app(
    agents_dir=AGENT_CODE_DIR, # Point to the specific agent folder
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# Pydantic model for the request body of the /predict endpoint
class QueryRequest(BaseModel):
    query: str

@app.get("/", summary="Health Check")
async def health_check():
    """
    Checks if the API is running and healthy.
    """
    return {"status": "healthy", "message": "ADK Weather and Time Agent is up!"}

@app.post("/predict", summary="Run ADK Agent with Query")
async def predict(request_body: QueryRequest):
    """
    Receives a user query and runs the ADK agent to get a response.
    """
    user_query = request_body.query
    if not user_query:
        raise HTTPException(status_code=400, detail="No query provided")

    try:
        # Access the ADK Runner instance set up by get_fast_api_app
        # It's typically stored in app.state.adk_runner
        adk_runner = app.state.adk_runner

        # Define a default user and session ID for demonstration purposes
        # In a real application, these might come from authentication or request headers
        USER_ID = "user_adk_fastapi_custom"
        SESSION_ID = "session_adk_fastapi_custom_001"

        final_response_text = ""
        # The runner.run() method handles session management internally using the
        # session_service configured in get_fast_api_app.
        async for event in adk_runner.run(USER_ID, SESSION_ID, user_query):
            if event.type == "final_response":
                # ADK events.message.content contains the actual response text
                final_response_text = event.message.content
                break # Assuming we only care about the first final response

        if not final_response_text:
            final_response_text = "The agent did not produce a final response."

        return {"response": final_response_text}
    except Exception as e:
        print(f"Error processing query: {e}")
        # Raise an HTTPException to return a proper HTTP error response
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    # Cloud Run automatically provides the PORT environment variable
    # If running locally, it defaults to 8080
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
