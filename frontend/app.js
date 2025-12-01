// Backend API URL - automatically detect based on environment
// In production (Railway), use the same origin; in development, use localhost
const API_URL = window.location.origin === 'http://localhost:3000' 
    ? 'http://localhost:8000' 
    : window.location.origin;

// Session management
let sessionId = localStorage.getItem('chatbot_session_id') || `session_${Date.now()}`;
localStorage.setItem('chatbot_session_id', sessionId);

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const loadingIndicator = document.getElementById('loadingIndicator');
const sendButton = document.querySelector('.send-button');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check backend connection
    checkBackendConnection();
    
    // Focus on input
    userInput.focus();
});

// Check if backend is running
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (response.ok) {
            console.log('Backend connected successfully');
        }
    } catch (error) {
        console.error('Backend connection failed:', error);
        addSystemMessage('⚠️ Unable to connect to backend. Please ensure the backend server is running on http://localhost:8000');
    }
}

// Handle suggestion button click
function askSuggestion(question) {
    userInput.value = question;
    sendMessage();
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Send message
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) {
        return;
    }

    // Disable input and button
    userInput.disabled = true;
    sendButton.disabled = true;

    // Add user message to chat
    addMessage(message, 'user');

    // Clear input
    userInput.value = '';

    // Show loading indicator
    showLoading();

    try {
        // Call backend API
        const response = await fetch(`${API_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                question: message,
                session_id: sessionId  // Add session_id for conversation memory
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        // Hide loading indicator
        hideLoading();

        // Add assistant response
        // Extract source URL from answer if it's embedded, otherwise use the separate field
        let answerText = data.answer || '';
        let sourceUrl = data.source_url || null;
        
        // Check if source URL is already in the answer text
        if (answerText.includes('Source:')) {
            const sourceMatch = answerText.match(/Source:\s*(https?:\/\/[^\s\n]+)/i);
            if (sourceMatch && sourceMatch[1]) {
                sourceUrl = sourceMatch[1];
                // Remove the source line from answer text
                answerText = answerText.replace(/Source:\s*https?:\/\/[^\s\n]+/gi, '').trim();
            }
        }
        
        addMessage(answerText, 'assistant', sourceUrl);

    } catch (error) {
        console.error('Error:', error);
        hideLoading();
        let errorMessage = 'Sorry, I encountered an error. Please try again.';
        if (error.message.includes('Failed to fetch') || error.message.includes('Connection refused')) {
            errorMessage = '⚠️ Unable to connect to the backend server. Please ensure the backend is running on http://localhost:8000';
        }
        addMessage(errorMessage, 'assistant');
    } finally {
        // Re-enable input and button
        userInput.disabled = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}

// Add message to chat
function addMessage(text, type, sourceUrl = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    
    // Format the message text (preserve line breaks)
    let formattedText = text.replace(/\n/g, '<br>');
    
    // Remove duplicate source URLs from the text if they exist
    // The backend already includes source URL, so we don't want duplicates
    if (sourceUrl) {
        const sourcePattern = new RegExp(`Source:\\s*${sourceUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'gi');
        formattedText = formattedText.replace(sourcePattern, '');
        // Also remove standalone "Source:" lines
        formattedText = formattedText.replace(/Source:\s*<br>/gi, '');
    }
    
    messageDiv.innerHTML = formattedText.trim();
    
    // Add source link if available (only if not already in text)
    if (sourceUrl && type === 'assistant' && !text.includes(sourceUrl)) {
        const sourceLink = document.createElement('a');
        sourceLink.href = sourceUrl;
        sourceLink.target = '_blank';
        sourceLink.className = 'source-link';
        sourceLink.textContent = `Source: ${sourceUrl}`;
        messageDiv.appendChild(sourceLink);
    }
    
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add system message
function addSystemMessage(text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message assistant';
    messageDiv.style.background = '#fff3cd';
    messageDiv.style.border = '1px solid #ffc107';
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Show loading indicator
function showLoading() {
    loadingIndicator.style.display = 'flex';
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide loading indicator
function hideLoading() {
    loadingIndicator.style.display = 'none';
}

