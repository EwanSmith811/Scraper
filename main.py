from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import traceback
import nest_asyncio # 1. Import nest_asyncio

# 2. Apply the patch to allow nested event loops
nest_asyncio.apply()

app = FastAPI(title="ScrapeGraphAI Service")

class ScrapeRequest(BaseModel):
    url: str

@app.post("/scrape")
def scrape(req: ScrapeRequest): # 3. Changed 'async def' to 'def'
    try:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")

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

        graph = SmartScraperGraph(prompt=prompt, source=req.url, config=graph_config)
        
        # This now runs without the 'asyncio.run' conflict
        result = graph.run() 
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
