from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
import os
import traceback
import nest_asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

# Add these new endpoints to your Koyeb main.py
@app.get("/venues")
def get_venues():
    try:
        with open("venues.json", "r") as f:
            return json.load(f)
    except:
        return []

@app.get("/scrape-progress")
def get_progress():
    # You'll need to update a global dictionary or file during your scrape() function
    try:
        with open("progress.json", "r") as f:
            return json.load(f)
    except:
        return {"current": 0, "total": 0, "runId": "none", "done": False}
app = FastAPI()

# Add this block to allow your Vercel app to talk to Koyeb
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development; change to your Vercel URL later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Apply the patch (This now works because we forced --loop asyncio)
nest_asyncio.apply()

app = FastAPI(title="ScrapeGraphAI Service")

class ScrapeRequest(BaseModel):
    url: str

def perform_scrape(target_url, api_key):
    from scrapegraphai.graphs import SmartScraperGraph
    
    graph_config = {
        "llm": {
            "api_key": api_key,
            "model": "openai/gpt-4o-mini",
            "temperature": 0,
        },
        "verbose": False,
        "headless": True,
    }

    prompt = (
        "Extract happy hour information. Return a JSON object with this structure: "
        '{"happyHours": [{"days": ["Mon", "Tue"], "startTime": "15:00", "endTime": "18:00", "deals": ["Pints $3"]}]}. '
        "Days must use 3-letter abbreviations. Times must be 24-hour format HH:MM."
    )

    graph = SmartScraperGraph(prompt=prompt, source=target_url, config=graph_config)
    return graph.run()

@app.post("/scrape")
async def scrape(req: ScrapeRequest):
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")

        # Run the scrape in a separate thread
        result = await run_in_threadpool(perform_scrape, req.url, api_key)
        return result
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


