# 🏢 Real Estate Property RAG System

An intelligent Real Estate AI Assistant powered by Retrieval-Augmented Generation (RAG) using Google's Gemini AI, LangChain, and FAISS vector database.

# its video demo link 

https://drive.google.com/file/d/1bPgdx2YVzpsqA1L_wZyj5MQ0FBBUTjYO/view?usp=sharing (Older version)

## ⚠️ IMPORTANT: Live Application Notice

This application is **currently live and deployed on AWS EC2**. Please use it **ethically and responsibly**.

**DO NOT:**
- ❌ Attempt prompt injection or jailbreak attempts
- ❌ Abuse the API with unethical queries
- ❌ Exceed rate limits intentionally
- ❌ Use for malicious or unauthorized purposes

**This is a personal project** with **free-tier API limits**. Respect these limitations and help keep the service available for legitimate use.

---

## 📋 Overview

This project implements a conversational AI assistant that helps users find real estate properties based on natural language queries. It uses advanced embedding techniques and semantic search to match user requirements with available properties in a cleaned, merged database.

**Live Demo**: [Real Estate AI Assistant](https://rag-property-assistant.streamlit.app/) with Fast API deployed on AWS using Docker 

## ✨ Features

- **🤖 AI-Powered Search**: Natural language property search using Google Gemini
- **🔍 Semantic Matching**: FAISS vector database for intelligent similarity search
- **📊 Structured Responses**: Pydantic-based output parsing with validation
- **💬 Chat Interface**: Interactive Streamlit-based conversational UI
- **🚀 Production Ready**: Dockerized FastAPI backend deployed on AWS EC2
- **⚙️ Customizable**: Adjustable model parameters (temperature, retrieval count)
- **📈 Batch Processing**: Efficient embedding generation with rate limiting
- **🧹 Data Pipeline**: Automated data cleaning and merging process

## 🛠️ Tech Stack

- **AI/ML**: Google Gemini (gemini-2.5-flash, gemini-embedding-001)
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **Vector Search**: FAISS (CPU)
- **Database**: SQLite
- **Data Processing**: Pandas, NumPy
- **Deployment**: Docker, AWS EC2
- **Framework**: LangChain
- **Environment**: Python 3.11+
- **Version Control**: Git + GitHub

## 📁 Project Structure

```
realestate_property_rag/
│
├── README.md                     # Project documentation (this file)
├── COMPLETE_BEGINNER_GUIDE.md    # Beginner's guide to the project
├── requirements.txt              # Python dependencies for main project
├── .env                         # Environment variables (NEVER COMMIT)
├── .env.example                 # Template for environment variables
│
├── streamlit_fastapi.py         # 🎯 Main Streamlit frontend (connects to FastAPI)
├── streamlit_app.py             # Legacy Streamlit app (direct local usage)
│
├── embedding.ipynb              # 📊 Jupyter notebook: Generate FAISS embeddings
├── merging.ipynb                # 🧹 Jupyter notebook: Data cleaning & merging
├── experiment_hybrid_embeddings.ipynb  # 🔬 Experimental hybrid embeddings
│
├── data/                        # 📁 Dataset directory
│   ├── project.csv              # Raw project data
│   ├── ProjectAddress.csv       # Address information
│   ├── ProjectConfiguration.csv # Configuration details
│   ├── ProjectConfigurationVariant.csv
│   ├── 2final_merged_realestate_data.csv
│   ├── 3final_merged_realestate_data.csv
│   ├── ...other versions...
│   └── 10final_merged_realestate_data.csv  # Final cleaned & merged data
│
├── faiss_realestate_index/      # 🔍 FAISS vector database
│   └── index.faiss
│
└── fastapi_app/                 # 🚀 Production API Backend
    ├── README.md                # FastAPI documentation
    ├── DOCKER_GUIDE.md          # Docker & deployment guide
    ├── requirements.txt         # FastAPI dependencies
    ├── .env                     # API env variables (NOT committed)
    ├── .env.example             # Environment template
    ├── .dockerignore            # Files excluded from Docker image
    │
    ├── main.py                  # FastAPI application
    ├── rag_service.py           # RAG pipeline service
    ├── models.py                # Pydantic data models
    ├── test_api.py              # API testing script
    │
    ├── Dockerfile               # Docker image definition
    ├── properties_sql.db        # SQLite database (properties)
    │
    ├── faiss_realestate_index/  # FAISS index copy
    │   └── index.faiss
    │
    └── fastenv/                 # Virtual environment (local dev)
```

---

## 🔄 Data Pipeline: Cleaning & Merging

The project includes a **complete data preparation pipeline** to convert raw CSV files into cleaned, merged, production-ready data.

### Data Processing Steps

#### 1. **Data Merging** (`merging.ipynb`)

Combines multiple CSV sources:
- **Input Files**:
  - `ProjectAddress.csv` - Address details
  - `ProjectConfiguration.csv` - Configuration specs
  - `ProjectConfigurationVariant.csv` - Variant configurations
  - `project.csv` - Main project data

- **Process**:
  - Merges on common keys (project IDs)
  - Handles missing values and duplicates
  - Creates unified property records
  - Validates schema consistency

- **Output**: `*final_merged_realestate_data.csv`

#### 2. **Data Cleaning**

The merging notebook includes:
- **Null Value Handling**: Fill or remove rows with missing critical fields
- **Duplicate Removal**: Identify and eliminate duplicate property records
- **Type Conversion**: Standardize data types (prices → numeric, locations → string)
- **Text Normalization**: Trim whitespace, standardize case
- **Price Parsing**: Extract numeric prices from formatted strings
- **Address Standardization**: Clean and normalize address fields
- **Data Validation**: Check data quality metrics

#### 3. **Database Generation**

- Creates `properties_sql.db` (SQLite database)
- Indexes on frequently searched fields (location, price, type)
- Optimized schema for fast queries

#### 4. **Embedding Generation** (`embedding.ipynb`)

- **Input**: Cleaned CSV file
- **Process**:
  - Converts property records into text documents
  - Generates embeddings using Google's `gemini-embedding-001` model
  - Implements batch processing with rate limiting
  - Handles API quota management

- **Output**: `faiss_realestate_index/index.faiss`

**Batch Processing Settings**:
```python
batch_size = 50              # Documents per batch
delay_between_batches = 2    # Seconds between batches (avoid rate limits)
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Google API Key (for Gemini AI & embeddings)
- Docker (for production deployment)
- Git (for version control)

### Quick Start (Local Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/rudrakshseth01/RAG_property_chatbot.git
   cd realestate_property_rag
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows PowerShell
   venv\Scripts\Activate.ps1
   
   # Windows CMD
   venv\Scripts\activate.bat
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   FASTAPI_URL=http://localhost:8000
   ```

   Or use the deployed version:
   ```env
   FASTAPI_URL=http://
   ```

   Get your API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

5. **Prepare data** (if first time)
   ```bash
   jupyter notebook merging.ipynb      # Clean & merge data
   jupyter notebook embedding.ipynb    # Generate FAISS index
   ```

### 📊 Data Preparation

The complete data pipeline is handled in Jupyter notebooks:

**Step 1: Merge & Clean Data**
```bash
jupyter notebook merging.ipynb
```
- Combines all CSV files
- Cleans and validates data
- Outputs cleaned merged CSV

**Step 2: Generate Embeddings**
```bash
jupyter notebook embedding.ipynb
```
- Creates FAISS vector index
- Processes in batches to respect API limits
- Saves index for RAG pipeline

---

## 🎯 Running the Application

### Option 1: Local Streamlit (Quick Testing)

```bash
streamlit run streamlit_app.py
# Opens at http://localhost:8501
```

**Runs entirely locally** with local FAISS index and SQLite database.

### Option 2: Streamlit + FastAPI Backend (Recommended)

**Terminal 1 - Start FastAPI**:
```bash
cd fastapi_app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# API available at http://localhost:8000/docs
```

**Terminal 2 - Start Streamlit**:
```bash
streamlit run streamlit_fastapi.py
# Frontend at http://localhost:8501
```

This separates frontend and backend, allowing independent scaling.

### Option 3: Docker (Production)

See [fastapi_app/DOCKER_GUIDE.md](fastapi_app/DOCKER_GUIDE.md) for detailed Docker instructions.

**Quick Docker run**:
```powershell
# Pull image
docker pull rudrakshseth20144/realestate_fastapi:latest

# Run with env variables
docker run --rm -p 8000:8000 `
  -e GOOGLE_API_KEY="your_key" `
  rudrakshseth20144/realestate_fastapi:latest
```

---

## 💡 Usage

### Example Queries

Try these natural language searches:

- "3BHK flats with lift in Yashvant Seth Jadhav Marg"
- "List projects near Subhash Nagar with parking and gym"
- "Show apartments under 1 crore with balcony"
- "Properties with swimming pool and kids play area"
- "Affordable 2BHK unfurnished apartments in South Mumbai"
- "Luxury villas with 4+ bedrooms and garden"

### Configuration Options

The Streamlit sidebar provides:

- **Model Temperature**: Adjust response creativity (0.0 = focused, 1.0 = creative)
- **Number of Results**: Control property retrieval count (3-40)
- **API Health Check**: Verify backend connection
- **Clear Chat**: Reset conversation history

---

## 🔧 Key Components

### 1. Data Cleaning Pipeline (`merging.ipynb`)

**Purpose**: Convert raw CSVs into a unified, clean dataset

**Key Functions**:
- Merge multiple CSV sources by property ID
- Handle missing values (fill, drop, or interpolate)
- Remove duplicate records
- Standardize data types and formats
- Normalize text (locations, amenities)
- Parse and validate prices

**Input**: `project.csv`, `ProjectAddress.csv`, `ProjectConfiguration.csv`, `ProjectConfigurationVariant.csv`

**Output**: `*final_merged_realestate_data.csv` (cleaned & merged)

---

### 2. Embedding Generation (`embedding.ipynb`)

**Purpose**: Convert property records into vector embeddings for semantic search

**Key Steps**:
- Load cleaned CSV
- Create text documents from property records
- Batch process documents (50 at a time)
- Generate embeddings using `gemini-embedding-001`
- Build FAISS index
- Save index locally

**Rate Limiting**:
```python
batch_size = 50
delay_between_batches = 2  # seconds
```

**Output**: `faiss_realestate_index/index.faiss`

---

### 3. FastAPI Backend (`fastapi_app/main.py`)

**Core Endpoints**:
- `GET /` - API information
- `GET /health` - Health check
- `POST /search` - AI-powered property search
- `GET /properties` - Browse all properties
- `GET /property/{id}` - Get specific property
- `GET /stats` - Database statistics

**RAG Pipeline** (`rag_service.py`):
1. User query → Embedding
2. FAISS similarity search (retrieves k properties)
3. Context building from retrieved docs
4. LLM processing with Gemini
5. Structured output parsing with Pydantic

---

### 4. Streamlit Frontend (`streamlit_fastapi.py`)

**Main Features**:
- Chat interface for conversational search
- Sidebar configuration (temperature, k_results)
- Property card display
- Health check button
- Browse all properties section
- Price range filter section

**Data Models**:
```python
PropertyMatch:
  - id: Property ID
  - projectName: Project name
  - location: Address
  - price: Price
  - area: Area (sq ft)
  - type: Property type
  - amenities: Amenities list
  - landmark: Nearby landmark
```

---

## 🚀 Deployment Architecture

### Local Setup
```
Streamlit Frontend (localhost:8501)
         ↓
    FastAPI (localhost:8000)
         ↓
   FAISS Index + SQLite DB
```

### Production (AWS EC2 + Docker)
```
Streamlit Frontend (localhost:8501)
         ↓
    FastAPI Container (Docker)
    on AWS EC2 ( :8000)
         ↓
   FAISS Index + SQLite DB
```

### Docker Deployment

**Image**: `rudrakshseth20144/realestate_fastapi:latest`

**Quick Deploy**:
```powershell
# Build locally
docker build -t realestate-fastapi:latest fastapi_app/

# Run with env
docker run --rm -p 8000:8000 `
  -e GOOGLE_API_KEY="your_key" `
  realestate-fastapi:latest

# Push to Docker Hub
docker tag realestate-fastapi:latest rudrakshseth20144/realestate_fastapi:latest
docker push rudrakshseth20144/realestate_fastapi:latest
```

See [fastapi_app/DOCKER_GUIDE.md](fastapi_app/DOCKER_GUIDE.md) for complete deployment guide.

---

## 🔐 Security & Ethics

### Ethical Usage

This application is a **personal project for educational purposes**. Please:

✅ **DO**:
- Use for legitimate property search
- Respect API rate limits
- Report security issues responsibly
- Provide constructive feedback

❌ **DON'T**:
- Attempt prompt injection or jailbreaks
- Use unethically or maliciously
- Abuse API with spam queries
- Scrape data without permission
- Share API keys publicly

### Technical Security

- `.env` files excluded from Docker image
- Secrets passed via environment variables
- Input validation with Pydantic models
- Error handling without exposing internals
- CORS configured appropriately

### Known Limitations

- **No authentication yet**: Security measures not fully implemented
- **Rate limited**: Free tier API has daily limits
- **Prompt injection handling**: Not yet implemented
- **Personal project**: Use responsibly, limit high-volume usage

---

## 🛡️ Error Handling

The application handles common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| `GOOGLE_API_KEY not found` | Missing API key | Set in `.env` file |
| `Service not initialized` | API startup failed | Check API logs, restart |
| `Cannot connect to FastAPI` | Backend unreachable | Start FastAPI server |
| `ResourceExhausted (429)` | Rate limit exceeded | Wait, reduce batch size |
| `FAISS index not found` | Missing embeddings | Run `embedding.ipynb` |
| `Database error` | SQLite access issue | Check file permissions |

---

## 📊 Data Schema

Properties in the database have:

```python
{
  "unique_property_id": "PROP001",
  "projectName": "Green Valley Apartments",
  "fullAddress": "123 Main St, Mumbai",
  "price": 8500000,
  "carpetArea": 1200,
  "pincode": "400050",
  "type": "3BHK",
  "landmark": "Near Metro Station",
  "amenities": "Gym, Swimming Pool, Parking"
}
```

---

## 📈 Performance Optimization

**Tips**:
- Use `@st.cache_resource` to cache FAISS index and avoid reloads
- Adjust `k_results` based on query complexity (3-10 optimal)
- Lower `temperature` (0.1-0.3) for consistent results
- Reduce `batch_size` in embedding if hitting API limits

---

## 🐛 Troubleshooting

### Data Pipeline Issues

| Issue | Solution |
|-------|----------|
| Merging produces wrong column count | Check CSV schema consistency |
| Embeddings fail with 429 error | Reduce `batch_size`, increase `delay_between_batches` |
| FAISS index not found | Run `embedding.ipynb` completely |
| SQLite database errors | Verify file permissions, database not corrupted |

### API & Streamlit Issues

| Issue | Solution |
|-------|----------|
| `GOOGLE_API_KEY not found` | Add to `.env` file |
| `Cannot connect to FastAPI` | Ensure `uvicorn main:app` is running |
| `Service not initialized` | Wait for API startup, check logs |
| `Port already in use` | Kill process on port, or use `--server.port` flag |

### Installation Issues

```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Fix LangChain issues
pip install --upgrade langchain-core langchain-google-genai

# Check Python version
python --version  # Ensure 3.11+
```

---

## 📝 Development

### Adding New Features

1. **New property fields**: Update merging logic + Pydantic models
2. **Custom LLM prompts**: Edit `_create_rag_chain()` in `fastapi_app/rag_service.py`
3. **Different embeddings**: Change model in `GoogleGenerativeAIEmbeddings()`
4. **Database fields**: Update SQLite schema + models

### Testing

```bash
# Test data pipeline
jupyter notebook merging.ipynb
jupyter notebook embedding.ipynb

# Test FastAPI locally
cd fastapi_app
python -m pytest test_api.py

# Test Streamlit UI
streamlit run streamlit_fastapi.py
```

---

## 📄 License

This project is for **educational purposes only**.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

---

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/rudrakshseth01/RAG_property_chatbot/issues)
- 📖 Docs: See `COMPLETE_BEGINNER_GUIDE.md` and `fastapi_app/DOCKER_GUIDE.md`
- 🚀 Deployment: See `fastapi_app/DOCKER_GUIDE.md` for Docker/AWS setup

---

## 🙏 Credits

- **Gemini AI** for LLM and embeddings
- **FAISS** for vector search
- **LangChain** for RAG framework
- **FastAPI** for production API
- **Streamlit** for interactive UI

---

**Made with ❤️ using Google Gemini, LangChain, and FastAPI**

*Please use this application ethically and responsibly. Respect API limits and do not abuse the service.*
