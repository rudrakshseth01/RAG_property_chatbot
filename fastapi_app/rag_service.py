"""
RAG (Retrieval-Augmented Generation) Service
Handles the AI-powered property search logic
"""

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import sqlite3
import asyncio
import os
from typing import Optional, List
from pathlib import Path

from models import PropertySearchResponse, PropertyMatch


class RAGService:
    """Service for handling RAG-based property search"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.default_model = model_name
        self.db: Optional[FAISS] = None
        self.embeddings: Optional[GoogleGenerativeAIEmbeddings] = None
        self.is_initialized = False
        self.request_count = 0
        # Two models rotating in order
        self.models = [
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite"
        ]
    
    def _get_next_model(self) -> str:
        """Get next model in rotation (round-robin)"""
        model = self.models[self.request_count % len(self.models)]
        self.request_count += 1
        return model
    
    async def initialize(self):
        """Initialize the FAISS database and embeddings"""
        try:
            # Get the path to the FAISS index (same directory as this file)
            current_dir = Path(__file__).parent
            faiss_path = current_dir / "faiss_realestate_index"
            
            # Run the blocking FAISS load in a thread pool
            loop = asyncio.get_event_loop()
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="gemini-embedding-001",
                google_api_key=self.api_key
            )
            
            # Load FAISS index in thread pool since it's blocking
            self.db = await loop.run_in_executor(
                None,
                lambda: FAISS.load_local(
                    str(faiss_path),
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            )
            
            self.is_initialized = True
            print("✅ FAISS database loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading FAISS database: {str(e)}")
            raise
    
    async def get_raw_faiss_results(self, query: str, k_results: int = 10) -> List[dict]:
        """
        Get raw FAISS similarity search results without LLM processing
        Returns the unprocessed FAISS documents
        """
        if not self.is_initialized or self.db is None:
            raise RuntimeError("RAG Service not initialized")
        
        try:
            # Run similarity search in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.db.similarity_search(query, k=k_results)
            )
            
            # Convert FAISS documents to dictionaries
            formatted_results = []
            for i, doc in enumerate(results, 1):
                formatted_results.append({
                    "rank": i,
                    "property_id": doc.metadata.get('unique_property_ID', 'Unknown'),
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                })
            
            return formatted_results
        
        except Exception as e:
            raise RuntimeError(f"Error retrieving FAISS results: {str(e)}")
    
    def _create_rag_chain(self, temperature: float, model_name: str):
        """Create the RAG chain with parser"""
        
        parser = PydanticOutputParser(pydantic_object=PropertySearchResponse)
        
        prompt = ChatPromptTemplate.from_template("""
You are a Real Estate Expert Assistant helping users find matching properties.

You will be given retrieved property data and a user query.

Your job:
1. Identify properties that match **all** conditions in the query.
2. Return your answer strictly as JSON according to the provided format instructions.
3. If some query conditions are not met, list them under `unmatched_points`.
4. Never assume data not present in the retrieved context.
5. If nothing matches, leave `matching_projects` empty and explain why.
6. Extract price constraints and convert to INR:
   - "under 50 lakh" → max_price: 5000000
   - "30-50 crore" → min_price: 300000000, max_price: 500000000
7. Extract sort preference:
   - "cheapest", "affordable", "budget", "lowest" → sort_by: "price_asc"
   - "premium", "luxury", "expensive", "highest" → sort_by: "price_desc"

---
Retrieved Property Data:
{context}

User Query:
{question}

{format_instructions}
""")
        
        model = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
            temperature=temperature
        )
        
        rag_chain = prompt | model | parser
        
        return rag_chain, parser
    
    async def _sql_filter_with_ids(
        self,
        property_ids: List[str],
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        sort_by: Optional[str] = None
    ):
        """Filter properties by ID list and price constraints, then sort"""
        
        if not property_ids:
            return []
        
        # Run database query in thread pool
        loop = asyncio.get_event_loop()
        
        def _query_db():
            placeholders = ",".join(["?"] * len(property_ids))
            query = f"""
                SELECT *
                FROM properties
                WHERE unique_property_id IN ({placeholders})
            """
            
            params = list(property_ids)
            conditions = []
            
            if min_price is not None:
                conditions.append("price >= ?")
                params.append(min_price)
            
            if max_price is not None:
                conditions.append("price <= ?")
                params.append(max_price)
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
            
            if sort_by == "price_asc":
                query += " ORDER BY price ASC"
            elif sort_by == "price_desc":
                query += " ORDER BY price DESC"
            
            # Get database path (in parent directory)
            db_path = Path(__file__).parent / "properties_sql.db"
            conn = sqlite3.connect(str(db_path))
            rows = conn.execute(query, params).fetchall()
            conn.close()
            
            return rows
        
        return await loop.run_in_executor(None, _query_db)
    
    async def search_properties(
        self,
        query: str,
        k_results: int = 10,
        temperature: float = 0.2
    ) -> PropertySearchResponse:
        """
        Search for properties using RAG with rotating models
        
        Args:
            query: Natural language search query
            k_results: Number of similar properties to retrieve
            temperature: Model temperature for response generation
            
        Returns:
            PropertySearchResponse with matching properties
        """
        
        if not self.is_initialized or self.db is None:
            raise RuntimeError("RAG Service not initialized")
        
        try:
            # Get next model in rotation (alternates between 3 models)
            selected_model = self._get_next_model()
            
            # Stage 1: Retrieve similar documents from FAISS
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self.db.similarity_search(query, k=k_results)
            )
            
            # Build context from retrieved documents
            context = "\n\n---\n\n".join([
                f"Property ID: {doc.metadata.get('unique_property_ID', 'Unknown')}\n{doc.page_content}"
                for doc in results
            ])
            
            # Create RAG chain with selected model
            rag_chain, parser = self._create_rag_chain(temperature, selected_model)
            
            # Prepare input
            input_data = {
                "context": context,
                "question": query,
                "format_instructions": parser.get_format_instructions()
            }
            
            # Get response from LLM (run in thread pool)
            response = await loop.run_in_executor(
                None,
                lambda: rag_chain.invoke(input_data)
            )
            
            # Log which model was used
            print(f"Using model: {selected_model} (Request #{self.request_count})")
            
            # Stage 2: SQL Filtering - Apply price and sorting constraints
            matched_ids = [
                prop.id for prop in response.matching_projects 
                if hasattr(prop, "id") and prop.id
            ]
            
            if not matched_ids:
                # No properties matched the RAG filter
                response.total_results = 0
                return response
            
            # Apply SQL filtering
            final_results = await self._sql_filter_with_ids(
                property_ids=matched_ids,
                min_price=response.min_price,
                max_price=response.max_price,
                sort_by=response.sort_by
            )
            
            final_matching_ids = [row[0] for row in final_results]
            
            # Filter matching_projects to only include those that passed SQL filter
            original_count = len(response.matching_projects)
            response.matching_projects = [
                prop for prop in response.matching_projects 
                if prop.id in final_matching_ids
            ]
            
            # Sort matching_projects based on final_results order
            if response.sort_by:
                id_to_prop = {prop.id: prop for prop in response.matching_projects}
                response.matching_projects = [
                    id_to_prop[prop_id] for prop_id in final_matching_ids 
                    if prop_id in id_to_prop
                ]
            
            # Update explanation if SQL filtering reduced results
            filtered_count = len(response.matching_projects)
            if filtered_count < original_count:
                price_msg = ""
                if response.min_price and response.max_price:
                    price_msg = f" within price range Rs{response.min_price:,} - Rs{response.max_price:,}"
                elif response.min_price:
                    price_msg = f" with price above Rs{response.min_price:,}"
                elif response.max_price:
                    price_msg = f" with price below Rs{response.max_price:,}"
                
                if filtered_count == 0:
                    response.explanation += f"\n\nNote: {original_count} properties matched your requirements, but none were found{price_msg}."
                else:
                    response.explanation += f"\n\nNote: {original_count} properties matched initially, but only {filtered_count} properties were found{price_msg}."
            
            response.total_results = filtered_count
            
            return response
        
        except Exception as e:
            raise RuntimeError(f"Error in search_properties: {str(e)}")
