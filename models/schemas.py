from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from enum import Enum

class Lead(BaseModel):
    """
    Lead model representing a business lead
    """
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    rating: Optional[float] = None
    reviews_count: Optional[int] = None
    category: Optional[str] = None
    google_maps_url: Optional[str] = None
    place_id: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None  # {"lat": 0.0, "lng": 0.0}
    
    class Config:
        json_encoders = {
            # Custom encoders if needed
        }

class ScrapeRequest(BaseModel):
    """
    Request model for scraping leads
    """
    query: str = Field(..., description="Search query (e.g., 'restaurants', 'dentists')")
    location: str = Field(..., description="Location to search (e.g., 'New York, NY')")
    max_results: int = Field(default=50, ge=1, le=200, description="Maximum number of results")
    
    class Config:
        schema_extra = {
            "example": {
                "query": "restaurants",
                "location": "New York, NY",
                "max_results": 50
            }
        }

class ScrapeResponse(BaseModel):
    """
    Response model for scraping results
    """
    scrape_id: str
    leads: List[Lead]
    total_found: int
    status: str = "success"
    
class EnrichmentRequest(BaseModel):
    """
    Request model for enriching leads with email addresses
    """
    scrape_id: str = Field(..., description="ID from previous scrape operation")
    hunter_api_key: str = Field(..., description="Hunter.io API key")
    
    class Config:
        schema_extra = {
            "example": {
                "scrape_id": "abc123",
                "hunter_api_key": "your-hunter-api-key"
            }
        }

class EnrichmentResponse(BaseModel):
    """
    Response model for enrichment results
    """
    scrape_id: str
    enriched_leads: List[Lead]
    enrichment_count: int
    status: str = "success"

class ExportFormat(str, Enum):
    """
    Supported export formats
    """
    CSV = "csv"
    SHEETS = "sheets"

class ExportRequest(BaseModel):
    """
    Request model for exporting leads
    """
    scrape_id: str = Field(..., description="ID from previous scrape operation")
    format: ExportFormat = Field(..., description="Export format")
    filename: Optional[str] = Field(None, description="Filename for CSV export")
    sheets_url: Optional[str] = Field(None, description="Google Sheets URL for sheets export")
    
    class Config:
        schema_extra = {
            "example": {
                "scrape_id": "abc123",
                "format": "csv",
                "filename": "my_leads.csv"
            }
        }

class ErrorResponse(BaseModel):
    """
    Error response model
    """
    error: str
    detail: Optional[str] = None
    status_code: int

class HealthResponse(BaseModel):
    """
    Health check response model
    """
    status: str
    service: str
    timestamp: Optional[str] = None

class LeadsResponse(BaseModel):
    """
    Response model for getting stored leads
    """
    scrape_id: str
    leads: List[Lead]
    total: int