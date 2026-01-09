from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.concurrency import run_in_threadpool
import os
import traceback
import nest_asyncio

# Apply the patch
nest_asyncio.apply()

app = FastAPI(title="ScrapeGraphAI Service")

class ScrapeRequest(BaseModel):
    url: str

# This helper function contains the actual scraping logic
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

        # run_in_threadpool runs the sync function in a separate thread
        # This prevents the 'asyncio.run' event loop conflict
        result = await run_in_threadpool(perform_scrape, req.url, api_key)
        return result
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
