"""
LLM handler for Gemini 2.0 Flash
Generates answers from retrieved context
"""
import google.generativeai as genai
from typing import List, Dict, Optional
import os


class GeminiLLMHandler:
    """Handler for Gemini 2.0 Flash LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini LLM handler
        
        Args:
            api_key: Google AI API key (or set GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass api_key parameter.")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model - try gemini-2.0-flash-exp first, fallback to gemini-1.5-flash
        try:
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        except Exception:
            # Fallback to gemini-1.5-flash if 2.0 is not available
            self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_answer(self, query: str, contexts: List[Dict], source_url: str, conversation_history: str = "") -> str:
        """
        Generate answer from query and retrieved contexts using Gemini
        
        Args:
            query: User query
            contexts: List of retrieved context chunks
            source_url: Source URL for citation
            conversation_history: Previous conversation context
            
        Returns:
            Generated answer string
        """
        # Build context text from retrieved chunks
        context_text = "\n\n".join([
            f"Context {i+1}:\n{ctx.get('content', '')}"
            for i, ctx in enumerate(contexts[:5])  # Use top 5 contexts for better coverage
        ])
        
        # Build conversation history section
        history_section = ""
        if conversation_history:
            history_section = f"\n\nPrevious Conversation:\n{conversation_history}\n\nIMPORTANT: Use the previous conversation to understand context. If the user says 'the course' or 'it', they are referring to the course mentioned in the previous conversation."
        
        # Create prompt
        prompt = f"""You are a helpful FAQ assistant for Nextleap courses. Answer questions based ONLY on the provided context from Nextleap's official website.

IMPORTANT RULES:
1. Answer ONLY using information from the provided context
2. If the information is not in the context, say "I don't have that information available"
3. Be concise and factual - no advice, only facts
4. Always mention the source URL at the end: Source: {source_url}
5. If asked about price, format it as ₹X,XXX
6. If asked about dates and the date is not available, clearly state that
7. Use conversation history to understand context - if user says "the course" or "it", refer to the course from previous conversation
8. If asked about EMI or payment options, provide ALL available EMI plans from the context
9. Make sure to answer about the SAME course mentioned in previous conversation if user refers to "the course" or "it"

Context from Nextleap website:
{context_text}{history_section}

User Question: {query}

Answer (be concise and factual):"""

        try:
            # Generate response
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            
            # Ensure source URL is included
            if source_url and source_url not in answer:
                answer += f"\n\nSource: {source_url}"
            
            return answer
            
        except Exception as e:
            error_msg = str(e)
            # If quota exceeded, provide a helpful message
            if "quota" in error_msg.lower() or "429" in error_msg:
                # Fallback: extract answer from context directly
                return self._extract_from_context(query, contexts, source_url, conversation_history)
            return f"I encountered an error while generating the answer. Please try again. Error: {error_msg}"
    
    def _extract_from_context(self, query: str, contexts: List[Dict], source_url: str, conversation_history: str = "") -> str:
        """Extract answer directly from context when LLM fails"""
        query_lower = query.lower()
        answer_parts = []
        
        # Extract EMI/payment info
        if any(keyword in query_lower for keyword in ["emi", "installment", "payment"]):
            for ctx in contexts:
                metadata = ctx.get("metadata", {})
                if metadata.get("type") == "payment":
                    # Try to get EMI from content first (more reliable)
                    content = ctx.get("content", "")
                    if "EMI Options" in content:
                        # Extract EMI lines from content
                        lines = content.split("\n")
                        emi_lines = [line.strip() for line in lines if line.strip().startswith("-") and ("₹" in line or "EMI" in line)]
                        if emi_lines:
                            answer_parts.append("EMI Options available:")
                            for emi_line in emi_lines:
                                answer_parts.append(emi_line)
                            break
                    # Fallback to metadata
                    elif metadata.get("emi_options"):
                        emi_options_str = metadata.get("emi_options", "")
                        # If it's a string (from ChromaDB), split it properly
                        if isinstance(emi_options_str, str) and emi_options_str:
                            # Split by comma if it's a comma-separated string
                            emi_list = [e.strip() for e in emi_options_str.split(",") if e.strip()]
                            if emi_list:
                                answer_parts.append("EMI Options available:")
                                for emi in emi_list:
                                    answer_parts.append(f"- {emi}")
                                break
        
        # Extract price
        if "price" in query_lower or "cost" in query_lower:
            for ctx in contexts:
                metadata = ctx.get("metadata", {})
                if metadata.get("cost"):
                    answer_parts.append(f"The cost is ₹{metadata['cost']}")
                    break
        
        # Extract date
        if "date" in query_lower or "start" in query_lower:
            for ctx in contexts:
                metadata = ctx.get("metadata", {})
                if metadata.get("batch_start_date") and metadata.get("batch_start_date") != "null":
                    answer_parts.append(f"The batch starts on {metadata['batch_start_date']}")
                    break
            if not any("starts" in part for part in answer_parts):
                answer_parts.append("The batch start date is not currently available on the website")
        
        if not answer_parts:
            answer_parts.append(contexts[0].get("content", "")[:200])
        
        answer = ". ".join(answer_parts)
        if source_url:
            answer += f"\n\nSource: {source_url}"
        
        return answer
    
    def generate_answer_simple(self, query: str, context_text: str, source_url: str) -> str:
        """
        Generate answer with simple context text
        
        Args:
            query: User query
            context_text: Combined context text
            source_url: Source URL
            
        Returns:
            Generated answer
        """
        prompt = f"""You are a helpful FAQ assistant for Nextleap courses. Answer the question based ONLY on the provided context from Nextleap's official website.

IMPORTANT RULES:
1. Answer ONLY using information from the provided context
2. If the information is not in the context, say "I don't have that information available"
3. Be concise and factual - no advice, only facts
4. Always mention the source URL at the end: Source: {source_url}
5. If asked about price, format it as ₹X,XXX
6. If asked about dates and the date is not available, clearly state that

Context from Nextleap website:
{context_text}

User Question: {query}

Answer (be concise and factual):"""

        try:
            response = self.model.generate_content(prompt)
            answer = response.text.strip()
            
            if source_url and source_url not in answer:
                answer += f"\n\nSource: {source_url}"
            
            return answer
            
        except Exception as e:
            return f"I encountered an error while generating the answer. Please try again. Error: {str(e)}"

