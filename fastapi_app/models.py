"""
Pydantic models for request and response data
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# ============================================
# REQUEST MODELS
# ============================================


class PropertySearchRequest(BaseModel):
    """Request model for property search"""
    
    query: str = Field(
        ...,
        description="Natural language query for property search",
        example="3BHK flat with lift near Subhash Nagar"
    )
    
    k_results: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Number of similar properties to retrieve"
    )
    
    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
        description="Model temperature (0=focused, 2=creative)"
    )


# ============================================
# RESPONSE MODELS
# ============================================


class PropertyMatch(BaseModel):
    """Individual property match in search results"""
    
    id: str = Field(..., description="Unique property ID")
    projectName: Optional[str] = Field(None, description="Project name")
    location: Optional[str] = Field(None, description="Location/address")
    price: Optional[str] = Field(None, description="Price or price range")
    area: Optional[str] = Field(None, description="Area details")
    pincode: Optional[str] = Field(None, description="Pincode")
    type: Optional[str] = Field(None, description="Property type")
    landmark: Optional[str] = Field(None, description="Nearby landmark")
    amenities: Optional[str] = Field(None, description="Available amenities")


class PropertySearchResponse(BaseModel):
    """Response model for property search"""
    
    matching_projects: List[PropertyMatch] = Field(
        default_factory=list,
        description="List of matching properties"
    )
    
    unmatched_points: List[str] = Field(
        default_factory=list,
        description="Query requirements that couldn't be matched"
    )
    
    explanation: str = Field(
        ...,
        description="AI explanation of search results"
    )
    
    min_price: Optional[int] = Field(
        None,
        description="Extracted minimum price from query"
    )
    
    max_price: Optional[int] = Field(
        None,
        description="Extracted maximum price from query"
    )
    
    sort_by: Optional[str] = Field(
        None,
        description="Sorting preference: 'price_asc' or 'price_desc'"
    )
    
    total_results: int = Field(
        0,
        description="Total number of matching properties found"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    
    status: str = Field(..., description="API status: 'healthy' or 'unhealthy'")
    message: str = Field(..., description="Status message")
    database_loaded: bool = Field(..., description="Whether FAISS database is loaded")
