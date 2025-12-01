"""
Query handler for answering questions about Nextleap courses
Uses RAG (Retrieval Augmented Generation) approach with Gemini LLM
"""
from typing import Dict, List, Optional
from src.embeddings.embedder import EmbeddingGenerator
from src.embeddings.vector_db import VectorDB
from src.query.llm_handler import GeminiLLMHandler
from src.query.conversation_memory import ConversationMemory


class QueryHandler:
    """Handle queries using RAG with Gemini LLM"""
    
    def __init__(self, vector_db: VectorDB, embedder: EmbeddingGenerator, llm_handler: Optional[GeminiLLMHandler] = None, conversation_memory: Optional[ConversationMemory] = None):
        """
        Initialize query handler
        
        Args:
            vector_db: Vector database instance
            embedder: Embedding generator instance
            llm_handler: Optional LLM handler (if None, will use simple extraction)
            conversation_memory: Optional conversation memory manager
        """
        self.vector_db = vector_db
        self.embedder = embedder
        self.llm_handler = llm_handler
        self.conversation_memory = conversation_memory or ConversationMemory(max_messages=20)
        self.conversation_memory = conversation_memory or ConversationMemory(max_messages=20)
    
    def retrieve_context(self, query: str, n_results: int = 3, course_filter: Optional[str] = None) -> List[Dict]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            n_results: Number of results to retrieve
            course_filter: Optional course name to filter/prioritize
            
        Returns:
            List of relevant chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embedder.generate_embedding(query)
        
        # Search vector database with more results to ensure we get batch info
        search_results = self.vector_db.search(query_embedding, n_results=max(n_results * 2, 20))
        
        # Format results
        contexts = []
        if search_results and search_results.get("documents") and len(search_results["documents"]) > 0:
            for i in range(len(search_results["documents"][0])):
                contexts.append({
                    "content": search_results["documents"][0][i],
                    "metadata": search_results["metadatas"][0][i] if search_results.get("metadatas") else {},
                    "distance": search_results["distances"][0][i] if search_results.get("distances") else None
                })
        
        # Filter by course if specified
        if course_filter:
            # Prioritize chunks from the specified course
            matching_course = [c for c in contexts if course_filter.lower() in c.get("metadata", {}).get("cohort_name", "").lower()]
            other_courses = [c for c in contexts if course_filter.lower() not in c.get("metadata", {}).get("cohort_name", "").lower()]
            contexts = matching_course + other_courses
        
        # Prioritize batch chunks for date/start/cost queries
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in ['start', 'date', 'when', 'cost', 'price', 'fee']):
            # Separate batch chunks from others
            batch_chunks = [c for c in contexts if c.get("metadata", {}).get("type") == "batch"]
            other_chunks = [c for c in contexts if c.get("metadata", {}).get("type") != "batch"]
            
            # Put batch chunks first, then others
            contexts = batch_chunks + other_chunks
        
        # Prioritize payment chunks for EMI/payment queries
        if any(keyword in query_lower for keyword in ['emi', 'installment', 'payment', 'pay']):
            payment_chunks = [c for c in contexts if c.get("metadata", {}).get("type") == "payment"]
            batch_chunks = [c for c in contexts if c.get("metadata", {}).get("type") == "batch"]
            other_chunks = [c for c in contexts if c.get("metadata", {}).get("type") not in ["payment", "batch"]]
            
            # Put payment chunks first, then batch (for course context), then others
            contexts = payment_chunks + batch_chunks + other_chunks
        
        # Return top n_results
        return contexts[:n_results]
    
    def format_answer(self, query: str, contexts: List[Dict], conversation_history: str = "") -> Dict:
        """
        Format answer from retrieved contexts using LLM if available
        
        Args:
            query: Original query
            contexts: Retrieved context chunks
            conversation_history: Previous conversation context
            
        Returns:
            Dictionary with answer and source URL
        """
        if not contexts:
            return {
                "answer": "I couldn't find relevant information to answer your question.",
                "source_url": None
            }
        
        # Get source URL from best context
        best_context = contexts[0]
        source_url = best_context.get("metadata", {}).get("source_url")
        
        # Use LLM if available, otherwise fall back to simple extraction
        if self.llm_handler:
            # Use Gemini to generate answer with conversation context
            answer = self.llm_handler.generate_answer(query, contexts, source_url, conversation_history)
        else:
            # Fallback to simple extraction
            answer = self._extract_answer_simple(query, contexts, source_url)
        
        return {
            "answer": answer,
            "source_url": source_url,
            "contexts_used": len(contexts)
        }
    
    def _extract_answer_simple(self, query: str, contexts: List[Dict], source_url: str) -> str:
        """
        Simple answer extraction (fallback when LLM not available)
        
        Args:
            query: User query
            contexts: Retrieved contexts
            source_url: Source URL
            
        Returns:
            Answer string
        """
        answer_parts = []
        query_lower = query.lower()
        
        # Extract price
        if "price" in query_lower or "cost" in query_lower:
            for ctx in contexts:
                metadata = ctx.get("metadata", {})
                if metadata.get("cost"):
                    answer_parts.append(f"The cost is ₹{metadata['cost']}")
                    break
        
        # Extract date
        if "date" in query_lower or "start" in query_lower:
            date_found = False
            for ctx in contexts:
                metadata = ctx.get("metadata", {})
                if metadata.get("batch_start_date") and metadata.get("batch_start_date") != "null":
                    answer_parts.append(f"The batch starts on {metadata['batch_start_date']}")
                    date_found = True
                    break
            if not date_found:
                answer_parts.append("The batch start date is not currently available")
        
        if not answer_parts:
            answer_parts.append(contexts[0].get("content", ""))
        
        answer = ". ".join(answer_parts)
        if source_url:
            answer += f"\n\nSource: {source_url}"
        
        return answer
    
    def answer_query(self, query: str, session_id: str = "default") -> Dict:
        """
        Answer a query using RAG with conversation memory
        
        Args:
            query: User query
            session_id: Session identifier for conversation memory
            
        Returns:
            Dictionary with answer and source URL
        """
        # Add user message to memory
        self.conversation_memory.add_message(session_id, "user", query)
        
        # Get conversation history
        conversation_history = self.conversation_memory.get_conversation_context(session_id)
        
        # Extract course name from conversation history if user refers to "the course"
        course_filter = None
        if conversation_history:
            # Look for course names in previous conversation
            history_lower = conversation_history.lower()
            course_keywords = {
                "product management": "Product Management",
                "data analyst": "Data Analyst",
                "business analyst": "Business Analyst",
                "ui ux": "UI UX Design",
                "ui/ux": "UI UX Design"
            }
            for keyword, course_name in course_keywords.items():
                if keyword in history_lower:
                    course_filter = course_name
                    break
        
        # Retrieve relevant context - use more results to ensure we get batch info
        contexts = self.retrieve_context(query, n_results=15, course_filter=course_filter)
        
        # Format answer with conversation context
        result = self.format_answer(query, contexts, conversation_history)
        
        # Add assistant response to memory
        self.conversation_memory.add_message(
            session_id, 
            "assistant", 
            result["answer"],
            {"source_url": result.get("source_url")}
        )
        
        return result

