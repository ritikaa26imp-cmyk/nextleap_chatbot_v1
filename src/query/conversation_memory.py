"""
Conversation memory manager for chatbot
Maintains conversation history for context-aware responses
"""
from typing import List, Dict, Optional
from collections import deque
from datetime import datetime


class ConversationMemory:
    """Manages conversation history with a sliding window"""
    
    def __init__(self, max_messages: int = 20):
        """
        Initialize conversation memory
        
        Args:
            max_messages: Maximum number of messages to remember
        """
        self.max_messages = max_messages
        self.conversations = {}  # session_id -> deque of messages
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """
        Add a message to conversation history
        
        Args:
            session_id: Unique session identifier
            role: 'user' or 'assistant'
            content: Message content
            metadata: Optional metadata (source_url, etc.)
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = deque(maxlen=self.max_messages)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[session_id].append(message)
    
    def get_history(self, session_id: str, last_n: Optional[int] = None) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: Session identifier
            last_n: Number of recent messages to return (None = all)
            
        Returns:
            List of message dictionaries
        """
        if session_id not in self.conversations:
            return []
        
        history = list(self.conversations[session_id])
        if last_n:
            return history[-last_n:]
        return history
    
    def get_conversation_context(self, session_id: str) -> str:
        """
        Get formatted conversation context for LLM
        
        Args:
            session_id: Session identifier
            
        Returns:
            Formatted conversation history as string
        """
        history = self.get_history(session_id)
        if not history:
            return ""
        
        context_parts = []
        for msg in history:
            role = msg["role"].capitalize()
            content = msg["content"]
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]


