from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
from models.schemas import (
    ScrapeRequest, 
    ScrapeResponse, 
    EnrichmentRequest, 
    EnrichmentResponse,
    ExportRequest,
    Lead
)
from scraper.gmaps_scraper import GoogleMapsScraper
from enrichment.hunter_api import HunterEnrichment
from utils.export import ExportManager

app = FastAPI(
    title="Lovable Lead Gen API",
    description="A powerful lead generation API with Google Maps scraping and email enrichment",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
scraper = GoogleMapsScraper()
enricher = HunterEnrichment()
export_manager = ExportManager()

# In-memory storage for demo (replace with database in production)
leads_storage = {}

@app.get("/")
async def root():
    return {"message": "Welcome to Lovable Lead Gen API", "status": "active"}

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_leads(request: ScrapeRequest):
    """
    Scrape leads from Google Maps based on search query and location
    """
    try:
        leads = await scraper.scrape_businesses(
            query=request.query,
            location=request.location,
            max_results=request.max_results
        )
        
        # Store leads with a unique ID
        import uuid
        scrape_id = str(uuid.uuid4())
        leads_storage[scrape_id] = leads
        
        return ScrapeResponse(
            scrape_id=scrape_id,
            leads=leads,
            total_found=len(leads),
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.post("/enrich", response_model=EnrichmentResponse)
async def enrich_leads(request: EnrichmentRequest):
    """
    Enrich leads with email addresses using Hunter.io API
    """
    try:
        # Get leads from storage
        if request.scrape_id not in leads_storage:
            raise HTTPException(status_code=404, detail="Scrape ID not found")
        
        leads = leads_storage[request.scrape_id]
        
        # Enrich with emails
        enriched_leads = await enricher.enrich_leads(leads, request.hunter_api_key)
        
        # Update storage
        leads_storage[request.scrape_id] = enriched_leads
        
        return EnrichmentResponse(
            scrape_id=request.scrape_id,
            enriched_leads=enriched_leads,
            enrichment_count=len([lead for lead in enriched_leads if lead.email]),
            status="success"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enrichment failed: {str(e)}")

@app.post("/export")
async def export_leads(request: ExportRequest):
    """
    Export leads to CSV or Google Sheets
    """
    try:
        # Get leads from storage
        if request.scrape_id not in leads_storage:
            raise HTTPException(status_code=404, detail="Scrape ID not found")
        
        leads = leads_storage[request.scrape_id]
        
        if request.format == "csv":
            file_path = export_manager.export_to_csv(leads, request.filename)
            return {"message": f"Exported to {file_path}", "file_path": file_path}
        
        elif request.format == "sheets":
            if not request.sheets_url:
                raise HTTPException(status_code=400, detail="Google Sheets URL required")
            
            success = export_manager.export_to_sheets(leads, request.sheets_url)
            if success:
                return {"message": "Successfully exported to Google Sheets"}
            else:
                raise HTTPException(status_code=500, detail="Failed to export to Google Sheets")
        
        else:
            raise HTTPException(status_code=400, detail="Invalid export format")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/leads/{scrape_id}")
async def get_leads(scrape_id: str):
    """
    Get stored leads by scrape ID
    """
    if scrape_id not in leads_storage:
        raise HTTPException(status_code=404, detail="Scrape ID not found")
    
    return {
        "scrape_id": scrape_id,
        "leads": leads_storage[scrape_id],
        "total": len(leads_storage[scrape_id])
    }

@app.delete("/leads/{scrape_id}")
async def delete_leads(scrape_id: str):
    """
    Delete stored leads by scrape ID
    """
    if scrape_id not in leads_storage:
        raise HTTPException(status_code=404, detail="Scrape ID not found")
    
    del leads_storage[scrape_id]
    return {"message": "Leads deleted successfully"}

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "lovable-leadgen"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)