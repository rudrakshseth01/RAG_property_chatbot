# Real Estate Property RAG - FastAPI Backend

A production-ready FastAPI backend for AI-powered real estate property search using Retrieval-Augmented Generation (RAG).

## ⚠️ LIVE DEPLOYMENT NOTICE

This API is **currently deployed on AWS EC2 with use of Docker** and available online at: `https://rag-property-chatbot.streamlit.app/`
And the Screenshots for the API endpoints are in the SCREENSHOT Folder
**Please use ethically and responsibly:**
- ✅ Legitimate property search queries
- ✅ Respect API rate limits (free tier)
- ❌ No prompt injection attempts
- ❌ No unethical use
- ❌ No API abuse or spam

This is a **personal project with daily API limits**. Help keep it available for everyone!

---

## 🚀 Features

- **AI-Powered Search**: Natural language property search using Google Gemini
- **RESTful API**: Clean and simple endpoints with async operations
- **Production Ready**: Dockerized and deployable to AWS EC2
- **FAISS Vector Search**: Semantic similarity search for intelligent matching
- **SQLite Database**: Indexed property data for fast queries
- **Structured Output**: Pydantic validation for consistent responses
- **Health Checks**: Built-in API health monitoring
- **Error Handling**: Comprehensive error messages and logging

## 📋 Prerequisites

- Python 3.11 or higher
- Google API Key (for Gemini AI)
- FAISS index files (from main project)
- SQLite database (properties_sql.db)
- Docker (for production deployment)

---

## 🔧 Local Installation

1. **Navigate to the FastAPI folder**:
   ```bash
   cd fastapi_app
   ```

2. **Create and activate virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   
   # Windows PowerShell
   venv\Scripts\Activate.ps1
   
   # Windows CMD
   venv\Scripts\activate.bat
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in `fastapi_app/`:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   LANGSMITH_API_KEY=your_langsmith_key_here  # Optional
   LANGSMITH_PROJECT=real-estate-rag          # Optional
   ```

   Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🏃 Running the API

### Development Mode (with auto-reload)
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API available at: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📚 API Endpoints

### 1. Root Endpoint
```
GET /
```
Get API information and available endpoints.

**Response**:
```json
{
  "message": "Welcome to Real Estate AI API",
  "version": "1.0.0",
  "endpoints": {
    "/health": "Check API health status",
    "/search": "Search for properties (POST)",
    "/properties": "Get all properties (GET)",
    "/property/{property_id}": "Get specific property by ID"
  }
}
```

### 2. Health Check
```
GET /health
```
Check if the API is healthy and ready to accept requests.

**Response**:
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "database_loaded": true
}
```

### 3. Search Properties (Main Endpoint)
```
POST /search
```
Search for properties using natural language AI-powered query.

**Request Body**:
```json
{
  "query": "3BHK flat with lift in South Mumbai",
  "k_results": 10,
  "temperature": 0.2
}
```

**Parameters**:
- `query` (string, required): Natural language search query
- `k_results` (integer, optional): Number of properties to retrieve (1-50, default: 10)
- `temperature` (float, optional): Response creativity (0.0-2.0, default: 0.2)

**Response**:
```json
{
  "matching_projects": [
    {
      "id": "PROP123",
      "projectName": "Green Valley Apartments",
      "location": "South Mumbai",
      "price": "₹85,00,000",
      "area": "1200 sq ft",
      "type": "3BHK",
      "pincode": "400050",
      "landmark": "Near Metro",
      "amenities": "Lift, Parking, Gym"
    }
  ],
  "unmatched_points": [],
  "explanation": "Found 1 property matching your requirements...",
  "min_price": 8500000,
  "max_price": 8500000,
  "sort_by": "price_asc",
  "total_results": 1
}
```

### 4. Get Raw FAISS Results
```
POST /search/raw
```
Get raw FAISS similarity search results (before LLM processing).

**Request Body**:
```json
{
  "query": "3BHK apartments",
  "k_results": 10
}
```

**Response**:
```json
{
  "query": "3BHK apartments",
  "total_results": 10,
  "results": [
    {
      "rank": 1,
      "property_id": "PROP123",
      "page_content": "Property details...",
      "metadata": {}
    }
  ]
}
```

### 5. Get All Properties
```
GET /properties?limit=50&offset=0&min_price=5000000&max_price=10000000
```
Browse all properties with optional filtering and pagination.

**Query Parameters**:
- `limit` (integer, optional): Results per page (1-100, default: 50)
- `offset` (integer, optional): Skip results (pagination, default: 0)
- `min_price` (integer, optional): Minimum price filter in INR
- `max_price` (integer, optional): Maximum price filter in INR

**Response**:
```json
{
  "total": 500,
  "limit": 50,
  "offset": 0,
  "count": 50,
  "properties": [...]
}
```

### 6. Get Property by ID
```
GET /property/{property_id}
```
Get a specific property by its unique ID.

**Response**:
```json
{
  "unique_property_id": "PROP123",
  "projectName": "Green Valley",
  "location": "South Mumbai",
  "price": 8500000,
  ...
}
```

### 7. Get Statistics
```
GET /stats
```
Get database statistics and summary information.

**Response**:
```json
{
  "total_properties": 1500,
  "average_price": 75000000,
  "min_price": 2500000,
  "max_price": 500000000,
  "property_types": [
    {"type": "3BHK", "count": 450},
    {"type": "2BHK", "count": 380}
  ]
}
```

---

## 🔍 Usage Examples

### Using cURL

**Search for properties**:
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "3BHK with gym in South Mumbai",
    "k_results": 5
  }'
```

**Get all properties**:
```bash
curl "http://localhost:8000/properties?limit=10"
```

**Health check**:
```bash
curl "http://localhost:8000/health"
```

### Using Python

```python
import requests

# Search for properties
response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "affordable 2BHK with parking",
        "k_results": 10,
        "temperature": 0.2
    }
)
print(response.json())

# Get property by ID
response = requests.get("http://localhost:8000/property/PROP123")
print(response.json())

# Get statistics
response = requests.get("http://localhost:8000/stats")
print(response.json())
```

### Using JavaScript

```javascript
// Search for properties
const response = await fetch('http://localhost:8000/search', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    query: "3BHK flats with lift",
    k_results: 10,
    temperature: 0.2
  })
});
const data = await response.json();
console.log(data);
```

---

## 🐳 Docker Deployment

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for comprehensive Docker and AWS deployment instructions.

**Quick Docker commands**:
```powershell
# Build image
docker build -t realestate-fastapi:latest .

# Run with env variables
docker run --rm -p 8000:8000 `
  -e GOOGLE_API_KEY="your_key" `
  realestate-fastapi:latest

# Push to Docker Hub
docker tag realestate-fastapi:latest rudrakshseth20144/realestate_fastapi:latest
docker push rudrakshseth20144/realestate_fastapi:latest
```

---

## 🏗️ Project Structure

```
fastapi_app/
├── main.py                      # FastAPI application & endpoints
├── rag_service.py               # RAG logic & AI search pipeline
├── models.py                    # Pydantic data models
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── .env                         # Environment variables (NOT committed)
├── .env.example                 # Template for environment
├── .dockerignore                # Files to exclude from Docker
├── README.md                    # This file
├── DOCKER_GUIDE.md              # Docker deployment guide
│
├── properties_sql.db            # SQLite database
└── faiss_realestate_index/      # FAISS vector index
    └── index.faiss
```

---

## 🔧 Configuration

### Environment Variables

Required:
- `GOOGLE_API_KEY`: Google Gemini API key

Optional:
- `LANGSMITH_API_KEY`: LangSmith API key for tracing
- `LANGSMITH_PROJECT`: LangSmith project name
- `PORT`: Server port (default: 8000)

### Model Settings

The API uses rotating models for better reliability:
```python
models = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite"
]
```

Models rotate on each request (round-robin) to balance usage.

---

## 🔐 Security

### .env Handling

- `.env` file is **NOT included in Docker image** (see `.dockerignore`)
- Secrets passed via environment variables at runtime
- Use `--env-file` or Docker secrets in production

### Input Validation

- All requests validated with Pydantic models
- Query length limits enforced
- Type checking on all parameters
- SQL injection protection via parameterized queries

### Known Limitations

- No authentication yet (add in production)
- Prompt injection handling not fully implemented
- Rate limiting managed by API quota only
- Personal project: use responsibly

---

## 🛡️ Error Handling

| HTTP Code | Error | Solution |
|-----------|-------|----------|
| 400 | Invalid request | Check request format |
| 503 | Service unavailable | FAISS index not loaded |
| 429 | Rate limit exceeded | Wait or upgrade API plan |
| 500 | Internal server error | Check logs |

### Common Errors

**GOOGLE_API_KEY not found**:
```
RuntimeError: GOOGLE_API_KEY not found in environment variables
```
→ Add to `.env` file

**FAISS index not found**:
```
RuntimeError: Error loading FAISS database
```
→ Run embedding.ipynb in main project

**Service not initialized**:
```
HTTPException: 503 - Service not initialized
```
→ Wait for startup, check logs

---

## 📊 Data Schema

Properties expected to have:

```python
{
  "unique_property_id": str,      # Primary key
  "projectName": str,             # Project name
  "fullAddress": str,             # Complete address
  "price": int,                   # Price in INR
  "carpetArea": float,            # Area in sq ft
  "pincode": str,                 # Location pincode
  "type": str,                    # 1BHK, 2BHK, 3BHK, etc.
  "landmark": str,                # Nearby landmark
  "amenities": str                # Comma-separated amenities
}
```

---

## 🧪 Testing

### Manual Testing

```bash
# Terminal 1: Start API
uvicorn main:app --reload

# Terminal 2: Test in another terminal
python test_api.py
```

### Using Interactive Docs

1. Start the API
2. Open browser: `http://localhost:8000/docs`
3. Try out endpoints using Swagger UI
4. All parameters documented in the UI

---

## 📈 Performance Tips

1. **Batch requests**: Instead of 100 single queries, batch them
2. **Cache results**: Store frequently searched properties
3. **Adjust k_results**: Start with 5-10, increase if needed
4. **Use price filters**: Pre-filter by price to reduce FAISS searches
5. **Set appropriate temperature**: 0.2-0.3 for consistent results

---

## 🐛 Troubleshooting

### API won't start

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000  # Windows

# Try different port
uvicorn main:app --port 8001
```

### GOOGLE_API_KEY errors

```bash
# Check .env file exists
dir .env

# Verify API key in Google Console
# https://console.cloud.google.com/
```

### Slow API responses

- Reduce `k_results` parameter
- Check FAISS index size
- Check API quota usage
- Optimize batch processing

---

## 📝 Development

### Adding New Endpoints

1. Add Pydantic model in `models.py`
2. Create endpoint in `main.py`
3. Add docstring with examples
4. Test in `/docs` UI

### Modifying RAG Pipeline

Edit `_create_rag_chain()` in `rag_service.py`:
- Customize prompt
- Change model
- Adjust temperature
- Modify output format

---

## 📄 License

Educational purposes only.

---

## 🙏 Credits

- **FastAPI**: Modern web framework
- **Gemini AI**: LLM and embeddings
- **FAISS**: Vector search engine
- **LangChain**: RAG framework
- **SQLite**: Data persistence

---

**Made with ❤️ using FastAPI, Google Gemini, and LangChain**

*Use this API responsibly. Respect API limits and do not abuse the service. This is a personal project with limited resources.*

The API will be available at: `http://localhost:8000`

## 📚 API Endpoints

### 1. Root Endpoint
```
GET /
```
Get API information and available endpoints.

### 2. Health Check
```
GET /health
```
Check if the API is healthy and database is loaded.

**Response**:
```json
{
  "status": "healthy",
  "message": "All systems operational",
  "database_loaded": true
}
```

### 3. Search Properties
```
POST /search
```
Search for properties using natural language.

**Request Body**:
```json
{
  "query": "3BHK flat with lift near Subhash Nagar",
  "k_results": 10,
  "temperature": 0.2
}
```

**Response**:
```json
{
  "matching_projects": [
    {
      "id": "PROP123",
      "projectName": "Green Valley Apartments",
      "location": "Subhash Nagar, Mumbai",
      "price": "₹85,00,000",
      "area": "1200 sq ft",
      "pincode": "400058",
      "type": "3BHK",
      "landmark": "Near Metro Station",
      "amenities": "Lift, Parking, Gym"
    }
  ],
  "unmatched_points": [],
  "explanation": "Found 1 property matching your requirements...",
  "total_results": 1
}
```

### 4. Get All Properties
```
GET /properties?limit=50&offset=0&min_price=5000000&max_price=10000000
```
Get all properties with optional filtering and pagination.

**Query Parameters**:
- `limit` (optional): Number of results (1-100, default: 50)
- `offset` (optional): Skip results (for pagination, default: 0)
- `min_price` (optional): Minimum price in INR
- `max_price` (optional): Maximum price in INR

### 5. Get Property by ID
```
GET /property/{property_id}
```
Get a specific property by its unique ID.

### 6. Get Statistics
```
GET /stats
```
Get database statistics and summary information.

**Response**:
```json
{
  "total_properties": 1500,
  "average_price": 75000000,
  "min_price": 2500000,
  "max_price": 500000000,
  "property_types": [
    {"type": "3BHK", "count": 450},
    {"type": "2BHK", "count": 380}
  ]
}
```

## 🔍 Example Usage

### Using cURL:

**Search for properties**:
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "affordable 2BHK apartment with parking",
    "k_results": 5
  }'
```

**Get all properties**:
```bash
curl "http://localhost:8000/properties?limit=10"
```

**Health check**:
```bash
curl "http://localhost:8000/health"
```

### Using Python:

```python
import requests

# Search for properties
response = requests.post(
    "http://localhost:8000/search",
    json={
        "query": "3BHK with gym and swimming pool",
        "k_results": 10
    }
)
print(response.json())

# Get property by ID
property_id = "PROP123"
response = requests.get(f"http://localhost:8000/property/{property_id}")
print(response.json())
```

## 📖 Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from these interfaces!

## 🏗️ Project Structure

```
fastapi_app/
├── main.py              # Main FastAPI application
├── models.py            # Pydantic models for requests/responses
├── rag_service.py       # RAG logic and AI search
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔐 Security Notes

- Always keep your API keys secure
- Use environment variables for sensitive data
- In production, configure CORS properly
- Add authentication/authorization as needed

## 🐛 Troubleshooting

**Error: "GOOGLE_API_KEY not found"**
- Make sure you have a `.env` file with your Google API key

**Error: "Service not initialized"**
- Check that the FAISS index files exist in the parent directory
- Verify the database file `properties_sql.db` is accessible

**Error: "Module not found"**
- Run `pip install -r requirements.txt` to install all dependencies

## 📝 Notes

- This is a beginner-friendly implementation
- All operations are asynchronous for better performance
- The API automatically loads the FAISS index on startup
- Price values are in Indian Rupees (INR)

## 🤝 Support

For issues or questions, please check:
1. The interactive docs at `/docs`
2. The health check endpoint
3. Application logs in the terminal

Happy coding! 🎉
