import os
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv
import uvicorn # Import uvicorn to run the FastAPI app

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ADK Weather and Time Agent",
    description="An API for getting weather and time information using an ADK agent.",
    version="1.0.0",
)

# --- ADK Agent Setup ---
# Import your agent from the quickstart_agent package
from quickstart_agent.agent import root_agent # Renamed to root_agent as per your agent.py

# Session management for ADK
session_service = InMemorySessionService()
app_name = "adk-weather-time-agent" # A unique name for your application

# Initialize the ADK Runner
runner = Runner(
    agent=root_agent,
    app_name=app_name,
    session_service=session_service
)

# Define a default user and session ID for demonstration purposes
USER_ID = "user_adk_fastapi"
SESSION_ID = "session_adk_fastapi_001"

# Pydantic model for the request body
class QueryRequest(BaseModel):
    query: str

@app.get("/", summary="Health Check")
async def health_check():
    """
    Checks if the API is running.
    """
    return {"status": "healthy", "message": "ADK Weather and Time Agent is up!"}

@app.post("/predict", summary="Run ADK Agent")
async def predict(request_body: QueryRequest):
    """
    Receives a user query and runs the ADK agent to get a response.
    """
    user_query = request_body.query
    if not user_query:
        raise HTTPException(status_code=400, detail="No query provided")

    try:
        # Run the agent with the user query
        final_response_text = ""
        async for event in runner.run(USER_ID, SESSION_ID, user_query):
            if event.type == "final_response":
                final_response_text = event.message.content
                break # Assuming we only care about the first final response

        if not final_response_text:
            final_response_text = "The agent did not produce a final response."

        return {"response": final_response_text}
    except Exception as e:
        print(f"Error running agent: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    # Cloud Run provides the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

