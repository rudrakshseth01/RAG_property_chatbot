"""
Real Estate Property RAG FastAPI Application
A simple API for searching real estate properties using AI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from dotenv import load_dotenv
import sqlite3
from pathlib import Path

# Load environment variables
load_dotenv()

# ============================================
# LANGSMITH CONFIGURATION
# ============================================
# Enable LangSmith tracing if credentials are provided
if os.getenv("LANGSMITH_API_KEY"):
    os.environ["LANGSMITH_TRACING"] = "true"
    print("LangSmith tracing enabled")
else:
    print("LangSmith API key not found. To enable tracing, set LANGSMITH_API_KEY in .env")

# Import our modules (after environment is set up)
from rag_service import RAGService
from models import PropertySearchRequest, PropertySearchResponse, HealthResponse

# ============================================
# UTILITIES
# ============================================


def get_db_path():
    """Get the path to the SQLite database (in this directory)"""
    current_dir = Path(__file__).parent
    return current_dir / "properties_sql.db"

# Initialize FastAPI app
app = FastAPI(
    title="Real Estate AI API",
    description="Search real estate properties using AI-powered semantic search",
    version="1.0.0"
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service (loaded once at startup)
rag_service: Optional[RAGService] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the RAG service when the API starts"""
    global rag_service
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not found in environment variables")
    
    print("🔄 Loading FAISS index and embeddings...")
    rag_service = RAGService(api_key=api_key)
    await rag_service.initialize()
    print("✅ RAG Service initialized successfully!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when the API shuts down"""
    print("👋 Shutting down Real Estate API...")


# ============================================
# API ENDPOINTS
# ============================================


@app.get("/", response_model=dict)
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Welcome to Real Estate AI API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Check API health status",
            "/search": "Search for properties (POST)",
            "/properties": "Get all properties (GET)",
            "/property/{property_id}": "Get specific property by ID",
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the API is healthy and ready"""
    
    if rag_service is None or not rag_service.is_initialized:
        return HealthResponse(
            status="unhealthy",
            message="RAG service not initialized",
            database_loaded=False
        )
    
    return HealthResponse(
        status="healthy",
        message="All systems operational",
        database_loaded=True
    )


@app.post("/search", response_model=PropertySearchResponse)
async def search_properties(request: PropertySearchRequest):
    """
    Search for properties using natural language query
    
    Example queries:
    - "3BHK flats with lift in Yashvant Seth Jadhav Marg"
    - "Show apartments under 1 crore with parking"
    - "Properties with gym and swimming pool"
    """
    
    if rag_service is None or not rag_service.is_initialized:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        # Process the search query
        response = await rag_service.search_properties(
            query=request.query,
            k_results=request.k_results,
            temperature=request.temperature
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@app.post("/search/raw")
async def search_raw_faiss(request: PropertySearchRequest):
    """
    Get raw FAISS similarity search results without LLM processing
    
    This returns the unprocessed FAISS documents retrieved from similarity search,
    useful for debugging and understanding which properties were initially matched.
    
    Parameters:
    - query: Search query
    - k_results: Number of results to return
    """
    
    if rag_service is None or not rag_service.is_initialized:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        results = await rag_service.get_raw_faiss_results(
            query=request.query,
            k_results=request.k_results
        )
        
        return {
            "query": request.query,
            "total_results": len(results),
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Raw search error: {str(e)}")


@app.get("/properties")
async def get_all_properties(
    limit: int = Query(default=50, ge=1, le=100, description="Number of properties to return"),
    offset: int = Query(default=0, ge=0, description="Number of properties to skip"),
    min_price: Optional[int] = Query(default=None, description="Minimum price in INR"),
    max_price: Optional[int] = Query(default=None, description="Maximum price in INR")
):
    """
    Get all properties with optional filtering
    
    Parameters:
    - limit: Maximum number of properties to return (1-100)
    - offset: Number of properties to skip (for pagination)
    - min_price: Minimum price filter in INR
    - max_price: Maximum price filter in INR
    """
    
    try:
        query = "SELECT * FROM properties WHERE 1=1"
        params = []
        
        if min_price is not None:
            query += " AND price >= ?"
            params.append(min_price)
        
        if max_price is not None:
            query += " AND price <= ?"
            params.append(max_price)
        
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        conn = sqlite3.connect(str(get_db_path()))
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        rows = cursor.execute(query, params).fetchall()
        
        # Convert to list of dictionaries
        properties = [dict(row) for row in rows]
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM properties WHERE 1=1"
        count_params = []
        
        if min_price is not None:
            count_query += " AND price >= ?"
            count_params.append(min_price)
        
        if max_price is not None:
            count_query += " AND price <= ?"
            count_params.append(max_price)
        
        total_count = cursor.execute(count_query, count_params).fetchone()[0]
        
        conn.close()
        
        return {
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "count": len(properties),
            "properties": properties
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/property/{property_id}")
async def get_property_by_id(property_id: str):
    """
    Get a specific property by its unique ID
    
    Parameters:
    - property_id: The unique property identifier
    """
    
    try:
        conn = sqlite3.connect(str(get_db_path()))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        row = cursor.execute(
            "SELECT * FROM properties WHERE unique_property_id = ?",
            (property_id,)
        ).fetchone()
        
        conn.close()
        
        if row is None:
            raise HTTPException(status_code=404, detail=f"Property {property_id} not found")
        
        return dict(row)
    
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/stats")
async def get_statistics():
    """
    Get database statistics and summary information
    """
    
    try:
        conn = sqlite3.connect(str(get_db_path()))
        cursor = conn.cursor()
        
        # Total properties
        total = cursor.execute("SELECT COUNT(*) FROM properties").fetchone()[0]
        
        # Average price
        avg_price = cursor.execute("SELECT AVG(price) FROM properties WHERE price IS NOT NULL").fetchone()[0]
        
        # Price range
        price_range = cursor.execute(
            "SELECT MIN(price) as min_price, MAX(price) as max_price FROM properties WHERE price IS NOT NULL"
        ).fetchone()
        
        # Property types count
        types = cursor.execute(
            "SELECT property_type, COUNT(*) as count FROM properties GROUP BY property_type ORDER BY count DESC"
        ).fetchall()
        
        conn.close()
        
        return {
            "total_properties": total,
            "average_price": round(avg_price, 2) if avg_price else None,
            "min_price": price_range[0],
            "max_price": price_range[1],
            "property_types": [{"type": t[0], "count": t[1]} for t in types]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics error: {str(e)}")


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
