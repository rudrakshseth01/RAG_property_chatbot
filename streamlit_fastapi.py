"""
Streamlit Frontend for Real Estate RAG - Connects to FastAPI Backend
This app calls the FastAPI endpoints instead of directly using FAISS/SQLite
Run FastAPI first: uvicorn fastapi_app/main:app --reload
Then run: streamlit run streamlit_fastapi.py
"""

import streamlit as st
import requests
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# --- Page Configuration ---
st.set_page_config(
    page_title="Real Estate AI Assistant (FastAPI)",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load environment ---
load_dotenv()

# FastAPI URL - set via FASTAPI_URL env variable or use default
DEFAULT_FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

# For deployed version, create .env in root with:
# FASTAPI_URL=http://

# Assign to fastapi_url for use throughout the app
fastapi_url = DEFAULT_FASTAPI_URL


# --- Sidebar Configuration ---
with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("### 🔍 Search Settings")
    
    # Number of results
    k_results = st.slider(
        "Number of Retrieved Properties",
        min_value=3,
        max_value=40,
        value=10,
        help="How many similar properties to retrieve from database"
    )
    
    # Temperature
    temperature = st.slider(
        "Model Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.2,
        step=0.1,
        help="Lower values = more focused, Higher values = more creative"
    )
    
    st.divider()
    
    st.markdown("### 📊 API Info")
    
    if st.button("🔗 Check API", use_container_width=True):
        try:
            response = requests.get(f"{fastapi_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                st.success("✅ Connected!")
                st.json(data)
            else:
                st.error(f"❌ Error: {response.status_code}")
        except Exception as e:
            st.error(f"❌ {str(e)}")
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    st.markdown("""
    ### 💡 Example Queries
    - "3BHK flats with lift in Yashvant Seth Jadhav Marg"
    - "List projects near Subhash Nagar with lift"
    - "Show apartments under 1 crore with parking"
    - "Properties with gym and swimming pool"
    - "Affordable 2BHK apartments with parking"
    """)
    
    st.divider()
    
    with st.expander("ℹ️ About This App"):
        st.markdown("""
        **Real Estate RAG Search**
        
        - **Frontend**: Streamlit (this app)
        - **Backend**: FastAPI (REST API)
        - **Search**: FAISS + Semantic AI
        - **Filtering**: SQLite + LLM extraction
        
        **Architecture:**
        ```
        Streamlit → FastAPI → FAISS + SQLite
        ```
        """)


# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_healthy" not in st.session_state:
    st.session_state.api_healthy = False

st.title("🏢 Real Estate AI Assistant")
st.markdown("""
**Powered by FastAPI · FAISS Vector Search · Gemini LLM , A Full GEN AI APP**

Ask me anything about available properties!

**📌 Important Notes:**
- Personal project with **free tier API limits** (daily usage restrictions)
- Backend hosted on **AWS EC2 using Docker**
- Data validation against this [dataset](https://drive.google.com/file/d/1G0JoUTDYL3hmAVdtBTTdKR8a3eCmlR8E/view?usp=sharing) and yes also merged different files and cleaned them to make this
- Low hallucination risk: Robust prompt templates + Pydantic validations

**⚠️ Security Notice:**
- Do not abuse with unethical queries or prompt injection attempts
- Security protections not yet fully implemented ,as **only a demo personal project**
""")


# --- API Helper Functions ---
def check_api_health(base_url: str) -> bool:
    """Check if FastAPI is running and healthy"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def search_properties(
    query: str, 
    base_url: str, 
    k_results: int, 
    temperature: float
) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Call FastAPI search endpoint"""
    try:
        payload = {
            "query": query,
            "k_results": k_results,
            "temperature": temperature
        }
        
        response = requests.post(
            f"{base_url}/search",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            error_detail = response.json().get("detail", response.text)
            return None, f"API Error: {response.status_code} - {error_detail}"
    
    except requests.exceptions.Timeout:
        return None, "⏱️ Request timeout. FastAPI might be slow or the query is complex."
    except requests.exceptions.ConnectionError:
        return None, f"❌ Cannot connect to FastAPI at `{base_url}`\n\n**Start FastAPI with:**\n```bash\ncd fastapi_app\nuvicorn main:app --reload\n```"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def get_retrieved_properties(
    query: str,
    base_url: str,
    k_results: int
) -> tuple[Optional[list], Optional[str]]:
    """Get the raw retrieved property data from FAISS similarity search"""
    try:
        payload = {
            "query": query,
            "k_results": k_results
        }
        
        response = requests.post(
            f"{base_url}/search/raw",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', []), None
        else:
            return None, f"Error: {response.status_code}"
    except Exception as e:
        return None, f"Error: {str(e)}"


def get_all_properties(
    base_url: str,
    limit: int = 20,
    offset: int = 0,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None
) -> tuple[Optional[Dict], Optional[str]]:
    """Get all properties with optional filtering"""
    try:
        params = {
            "limit": limit,
            "offset": offset
        }
        if min_price:
            params["min_price"] = min_price
        if max_price:
            params["max_price"] = max_price
        
        response = requests.get(
            f"{base_url}/properties",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.status_code}"
    except Exception as e:
        return None, f"Error: {str(e)}"


# --- Display Functions ---
def display_property_card(prop: Dict[str, Any]):
    """Display a single property as a card"""
    with st.container():
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.markdown(f"**🏢 {prop.get('projectName', 'N/A')}**")
            st.markdown(f"**ID:** `{prop.get('id', prop.get('unique_property_id', 'N/A'))}`")
            st.markdown(f"**Type:** {prop.get('type', 'N/A')}")
            st.markdown(f"**📍 Location:** {prop.get('location', 'N/A')}")
        
        with col2:
            st.markdown(f"**💰 Price:** {prop.get('price', 'N/A')}")
            st.markdown(f"**📐 Area:** {prop.get('area', 'N/A')}")
            st.markdown(f"**📮 Pincode:** {prop.get('pincode', 'N/A')}")
            if prop.get('landmark'):
                st.markdown(f"**🗺️ Landmark:** {prop.get('landmark')}")
        
        if prop.get('amenities'):
            st.markdown(f"**✨ Amenities:** {prop.get('amenities')}")
        
        st.divider()


def display_search_response(response: Dict[str, Any], fastapi_url: str = None, query: str = None, k_results: int = 10):
    """Display the complete response from FastAPI search endpoint"""
    
    # Show filter information if price constraints were applied
    if response.get('min_price') or response.get('max_price') or response.get('sort_by'):
        filter_info = "🔍 **Applied Filters:** "
        filters = []
        if response.get('min_price'):
            filters.append(f"Min Price: ₹{response['min_price']:,}")
        if response.get('max_price'):
            filters.append(f"Max Price: ₹{response['max_price']:,}")
        if response.get('sort_by') == "price_asc":
            filters.append("Sorted: Lowest to Highest Price")
        elif response.get('sort_by') == "price_desc":
            filters.append("Sorted: Highest to Lowest Price")
        
        if filters:
            st.info(filter_info + " | ".join(filters))
    
    # Matching Projects
    st.markdown("### ✅ Matching Projects")
    
    matching_projects = response.get('matching_projects', [])
    
    if matching_projects:
        st.success(f"Found {len(matching_projects)} matching properties")
        
        for prop in matching_projects:
            display_property_card(prop)
    else:
        st.warning("No matching projects found.")
    
    # Unmatched Points
    unmatched = response.get('unmatched_points', [])
    if unmatched:
        st.markdown("### ⚠️ Unmatched Points")
        for point in unmatched:
            st.warning(f"• {point}")
    
    # Explanation
    st.markdown("### 💡 Explanation")
    st.info(response.get('explanation', 'No explanation available'))
    
    # Retrieved Properties (Expander) - Fetch raw FAISS results
    with st.expander("📚 View Retrieved Property Data"):
        st.markdown("*Note: These are the raw FAISS similarity search results used for matching.*")
        st.markdown("---")
        
        if fastapi_url and query:
            if st.button("🔍 Load Retrieved Property Data", key=f"raw_results_{query}"):
                with st.spinner("Fetching FAISS results..."):
                    raw_results, error = get_retrieved_properties(query, fastapi_url, k_results)
                    
                    if error:
                        st.error(f"Could not fetch results: {error}")
                    elif raw_results:
                        st.success(f"Retrieved {len(raw_results)} FAISS results")
                        st.markdown("---")
                        
                        for result in raw_results:
                            st.markdown(f"**Property {result['rank']}:**")
                            st.markdown(f"- **Property ID:** `{result['property_id']}`")
                            st.text(result['page_content'])
                            st.divider()
                    else:
                        st.info("No results retrieved")
        else:
            st.info("ℹ️ Raw FAISS results will be available after searching")
    
# --- Check API Connection on Load ---
if not check_api_health(fastapi_url):
    st.error(f"""
    ❌ **Cannot connect to FastAPI at `{fastapi_url}`**
    
    **To start FastAPI, run in a terminal:**
    ```bash
    cd fastapi_app
    uvicorn main:app --reload
    ```
    
    **Then come back to this Streamlit app.**
    """)
    st.stop()

st.session_state.api_healthy = True


# --- Main Chat Interface ---
st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.markdown(message["content"])
        else:
            display_search_response(
                message["response"],
                fastapi_url=fastapi_url,
                query=message.get("query"),
                k_results=message.get("k_results", 10)
            )


# Chat input
if query := st.chat_input("Ask about properties (e.g., 'flats near Sindhi socity or Queens park , 2/3/4/1BHK, unfurnished/Semi-furnished/having balcony etc')"):
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Process query and display response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching properties... This might take a few seconds."):
            response, error = search_properties(
                query,
                fastapi_url,
                k_results,
                temperature
            )
            
            if error:
                st.error(error)
            elif response:
                display_search_response(
                    response,
                    fastapi_url=fastapi_url,
                    query=query,
                    k_results=k_results
                )
                
                # Add assistant response to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "response": response,
                    "query": query,
                    "k_results": k_results
                })
            else:
                st.error("❌ Unknown error occurred")


# --- Additional Features Section ---


with st.expander("🔍 Browse All Properties (Direct Database Query)", expanded=False):
    st.markdown("**Load properties without AI search - direct from database**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        limit = st.number_input("Results per page", min_value=1, max_value=100, value=20)
    
    with col2:
        offset = st.number_input("Offset (skip)", min_value=0, value=0)
    
    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("📥 Load Properties", use_container_width=True):
            st.session_state.load_properties = True
    
    # Display properties at full width (outside col3)
    if st.session_state.get('load_properties', False):
        with st.spinner("Loading properties..."):
            data, error = get_all_properties(fastapi_url, limit=limit, offset=offset)
            
            if error:
                st.error(error)
            elif data:
                st.info(f"Showing {data['count']} of {data['total']} properties")
                
                st.markdown("---")
                
                # Display properties in cards (full width - not crunched)
                for prop in data['properties']:
                    with st.container():
                        col_a, col_b = st.columns([2, 3])
                        
                        with col_a:
                            st.markdown(f"**🏢 {prop.get('projectName', 'N/A')}**")
                            st.markdown(f"**ID:** `{prop.get('unique_property_id', 'N/A')}`")
                            st.markdown(f"**Type:** {prop.get('type', 'N/A')}")
                            st.markdown(f"**📍 Location:** {prop.get('fullAddress', 'N/A')}")
                        
                        with col_b:
                            price_val = prop.get('price', 'N/A')
                            if isinstance(price_val, (int, float)):
                                st.markdown(f"**💰 Price:** ₹{price_val:,.0f}")
                            else:
                                st.markdown(f"**💰 Price:** {price_val}")
                            carpet_area = prop.get('carpetArea', 'N/A')
                            if carpet_area and carpet_area != 'N/A':
                                st.markdown(f"**📐 Area:** {carpet_area} sq ft")
                            else:
                                st.markdown(f"**📐 Area:** N/A")
                            st.markdown(f"**📮 Pincode:** {prop.get('pincode', 'N/A')}")
                        
                        if prop.get('landmark'):
                            st.markdown(f"**🗺️ Landmark:** {prop.get('landmark')}")
                        
                        st.divider()
            else:
                st.error("Failed to load properties")


with st.expander("💰 Filter by Price Range", expanded=False):
    st.markdown("**Search properties by price range only**")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        min_price = st.number_input(
            "Minimum Price (INR)",
            min_value=0,
            value=0,
            step=1000000,
            help="Leave 0 for no minimum"
        )
    
    with col2:
        max_price = st.number_input(
            "Maximum Price (INR)",
            min_value=0,
            value=100000000,
            step=1000000
        )
    
    with col3:
        st.write("")  # Spacing
        st.write("")  # Spacing
        if st.button("🔍 Search", use_container_width=True):
            st.session_state.filter_properties = True
    
    # Display properties at full width (outside col3)
    if st.session_state.get('filter_properties', False):
        with st.spinner("Filtering properties..."):
            data, error = get_all_properties(
                fastapi_url,
                limit=50,
                min_price=min_price if min_price > 0 else None,
                max_price=max_price if max_price > 0 else None
            )
            
            if error:
                st.error(error)
            elif data:
                st.success(f"Found {data['count']} properties in price range")
                
                st.markdown("---")
                
                # Display properties in cards (full width - not crunched)
                for prop in data['properties']:
                    with st.container():
                        col_a, col_b = st.columns([2, 3])
                        
                        with col_a:
                            st.markdown(f"**🏢 {prop.get('projectName', 'N/A')}**")
                            st.markdown(f"**ID:** `{prop.get('unique_property_id', 'N/A')}`")
                            st.markdown(f"**Type:** {prop.get('type', 'N/A')}")
                            st.markdown(f"**📍 Location:** {prop.get('fullAddress', 'N/A')}")
                        
                        with col_b:
                            price_val = prop.get('price', 'N/A')
                            if isinstance(price_val, (int, float)):
                                st.markdown(f"**💰 Price:** ₹{price_val:,.0f}")
                            else:
                                st.markdown(f"**💰 Price:** {price_val}")
                            carpet_area = prop.get('carpetArea', 'N/A')
                            if carpet_area and carpet_area != 'N/A':
                                st.markdown(f"**📐 Area:** {carpet_area} sq ft")
                            else:
                                st.markdown(f"**📐 Area:** N/A")
                            st.markdown(f"**📮 Pincode:** {prop.get('pincode', 'N/A')}")
                        
                        if prop.get('landmark'):
                            st.markdown(f"**🗺️ Landmark:** {prop.get('landmark')}")
                        
                        st.divider()


# --- Footer ---
st.markdown("---")
