# NextLeap FAQ Chatbot

A comprehensive FAQ assistant that answers questions about NextLeap courses using only official public pages. Built with RAG (Retrieval Augmented Generation) architecture, powered by Gemini 2.0 Flash LLM.

## 🎯 Project Goal

Build a small FAQ assistant that answers facts about NextLeap (cohorts, batches, curriculum, mentors, instructors, placements, reviews) using only official public pages. Every answer must include one source link. No advice.

## ✨ Features

- **Intelligent Q&A**: Answers questions about NextLeap courses using RAG architecture
- **Conversation Memory**: Remembers last 20 messages for context-aware responses
- **EMI Information**: Extracts and provides payment/EMI options for courses
- **Source URLs**: Every answer includes source URL from NextLeap website
- **Modern UI**: Clean, responsive frontend with real-time chat interface
- **FastAPI Backend**: RESTful API with automatic documentation
- **Vector Search**: Semantic search using ChromaDB and sentence transformers

## 🏗️ Architecture

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Frontend UI    │
│  (Port 3000)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  FastAPI Server │
│  (Port 8000)    │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Query Handler   │
│ (RAG System)    │
└──────┬──────────┘
       │
       ├──────────────┐
       ▼              ▼
┌─────────────┐  ┌──────────────┐
│ Vector DB   │  │   Gemini     │
│ (ChromaDB)  │  │ 2.0 Flash    │
│             │  │    LLM       │
└─────────────┘  └──────────────┘
       │              │
       └──────┬───────┘
              ▼
       ┌─────────────┐
       │   Answer    │
       │ + Source URL│
       └─────────────┘
```

## 📁 Project Structure

```
nextleap_chatbot_v1/
├── frontend/              # Frontend UI
│   ├── index.html        # Main HTML structure
│   ├── styles.css        # Styling
│   └── app.js           # JavaScript for API integration
├── src/
│   ├── api/             # FastAPI server
│   │   └── server.py    # API endpoints
│   ├── scraper/         # Web scraping
│   │   ├── scraper.py   # Main scraper
│   │   ├── pages.py     # Course URLs
│   │   └── enhanced_scraper.py  # Enhanced scraper (optional)
│   ├── processor/       # Data processing
│   │   ├── chunker.py   # Text chunking
│   │   └── data_validator.py  # Data validation
│   ├── embeddings/      # Vector database
│   │   ├── embedder.py  # Embedding generation
│   │   └── vector_db.py # ChromaDB operations
│   └── query/           # Query handling
│       ├── query_handler.py      # RAG query handler
│       ├── llm_handler.py        # Gemini LLM handler
│       └── conversation_memory.py # Conversation memory
├── scripts/
│   ├── scrape_data.py   # Scrape course data
│   ├── build_kb.py      # Build knowledge base
│   ├── run_server.py    # Start backend server
│   ├── run_frontend.py  # Start frontend server
│   ├── run_all.py       # Start both servers
│   └── test_server.py   # Test API endpoints
├── data/
│   ├── raw/             # Raw scraped data
│   ├── processed/       # Validated course data
│   └── knowledge_base/  # Vector database (ChromaDB)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- pip

### Installation

1. **Clone the repository** (if applicable)

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```
   Or the server will use the default key provided in the code.

4. **Scrape course data:**
   ```bash
   python3 scripts/scrape_data.py
   ```

5. **Build knowledge base:**
   ```bash
   python3 scripts/build_kb.py
   ```

6. **Start the application:**
   ```bash
   # Option 1: Start both backend and frontend together
   python3 scripts/run_all.py
   
   # Option 2: Start separately
   # Terminal 1 - Backend
   python3 scripts/run_server.py
   
   # Terminal 2 - Frontend
   python3 scripts/run_frontend.py
   ```

7. **Access the application:**
   - Frontend UI: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📊 Data Extraction

### Extracted Information

The scraper extracts the following data from NextLeap course pages:

- **Cohorts**: Course names and descriptions
- **Batches**: Start dates, cost, course type (live/self-paced)
- **Payment Options**: EMI plans and payment information
- **Curriculum**: Detailed course content and modules
- **Mentors/Instructors**: Names of instructors and mentors
- **Placements**: Placement support information
- **Reviews**: Student reviews and testimonials

### Data Sources

Currently scraped courses:
1. Product Management Certification Course
2. Data Analyst Certification Course
3. UI UX Design Certification Course
4. Business Analyst Certification Course

### Data Extraction Features

- ✅ **JSON-LD Extraction**: Uses structured data for reliable extraction
- ✅ **HTML Fallback**: Falls back to HTML parsing when needed
- ✅ **URL Validation**: All URLs validated to ensure they belong to nextleap.app
- ✅ **Source URL Tracking**: Every data point includes its source URL
- ✅ **Data Validation**: Validates and cleans all extracted data
- ✅ **EMI Extraction**: Extracts payment and EMI options

### Output Files

- **Raw Data**: `data/raw/raw_data_scrape_data.json` - Unprocessed scraped data
- **Processed Data**: `data/processed/nextleap_courses.json` - Validated and cleaned data

## 🔧 Backend API

### Endpoints

#### Health Check
```bash
GET /health
GET /
```

Response:
```json
{
  "status": "healthy",
  "message": "Nextleap FAQ Chatbot API is running",
  "knowledge_base_chunks": 86
}
```

#### Query (POST)
```bash
POST /query
Content-Type: application/json

{
  "question": "What is the cost of product management course?",
  "session_id": "optional_session_id"
}
```

Response:
```json
{
  "answer": "The cost is ₹49,999\n\nSource: https://nextleap.app/course/product-management-course",
  "source_url": "https://nextleap.app/course/product-management-course"
}
```

#### Query (GET)
```bash
GET /query?question=What is the cost of product management course?
```

### API Usage Examples

#### Using cURL
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the cost of data analyst course?"}'
```

#### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/query",
    json={"question": "What is the cost of data analyst course?"}
)

result = response.json()
print(result["answer"])
print(result["source_url"])
```

#### Using JavaScript
```javascript
const response = await fetch('http://localhost:8000/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What is the cost of data analyst course?'
  })
});

const data = await response.json();
console.log(data.answer);
console.log(data.source_url);
```

## 💬 Frontend UI

### Features

- Clean, modern design with gradient background
- Real-time chat interface
- Loading animations
- Suggestion buttons for quick queries
- Source URL links for all answers
- Responsive design for mobile and desktop
- Conversation memory (remembers context)

### Access

Open http://localhost:3000 in your browser after starting the frontend server.

### Testing the Chatbot

1. Ask: "what is the cost of product management course?"
2. Then ask: "are there any emi options for the course?"

The chatbot will:
- Remember the context from the first question
- Return EMI information for the Product Management course
- Include source URLs with answers

## 🧠 Knowledge Base

### Structure

- **Location**: `data/knowledge_base/chroma_db`
- **Collection**: `nextleap_courses`
- **Total Chunks**: 86 (from 4 courses)
- **Chunk Types**: cohort, batch, payment, curriculum, mentors_instructors, placements, reviews

### Chunk Metadata

Each chunk includes:
- `type`: Type of information (cohort, batch, payment, curriculum, etc.)
- `cohort_name`: Name of the course
- `source_url`: Source URL from NextLeap website
- `field`: Specific field (cohort_info, batch_info, payment_options, etc.)
- Additional fields based on type (cost, batch_start_date, emi_options, instructors, etc.)

### Rebuilding Knowledge Base

If you update the course data:
```bash
python3 scripts/build_kb.py
```

## 🔍 Query Processing Flow

1. **User Query**: User asks a question via frontend or API
2. **Session Management**: Conversation memory retrieves previous messages (if any)
3. **Embedding**: Query is converted to embedding vector
4. **Retrieval**: Vector DB searches for similar chunks (top 10-15)
5. **Prioritization**: Chunks are prioritized by type (batch chunks for date/cost queries, payment chunks for EMI queries)
6. **Context Filtering**: If conversation history exists, filter by course mentioned previously
7. **LLM Generation**: Gemini 2.0 Flash generates answer from retrieved context
8. **Response**: Returns answer with source URL

## 🎨 Components

### 1. Scraper (`src/scraper/scraper.py`)
- Extracts data from NextLeap course pages
- Uses JSON-LD structured data (most reliable)
- Falls back to HTML parsing
- Validates all URLs
- Extracts payment/EMI options

### 2. Data Chunker (`src/processor/chunker.py`)
- Splits course data into searchable chunks
- Creates chunks for: cohort info, batch info, payment options, curriculum, mentors, placements, reviews
- Each chunk includes metadata (source URL, type, field)

### 3. Embedding Generator (`src/embeddings/embedder.py`)
- Uses `sentence-transformers` with `all-MiniLM-L6-v2` model
- Generates embeddings for text chunks and queries
- Enables semantic search

### 4. Vector Database (`src/embeddings/vector_db.py`)
- Uses ChromaDB for persistent storage
- Stores chunks with embeddings and metadata
- Enables fast similarity search

### 5. Query Handler (`src/query/query_handler.py`)
- Implements RAG (Retrieval Augmented Generation)
- Retrieves relevant context from vector DB
- Prioritizes chunks based on query type
- Filters by course from conversation history
- Formats answers with source URLs

### 6. LLM Handler (`src/query/llm_handler.py`)
- Handles Gemini 2.0 Flash API calls
- Generates answers from retrieved context
- Includes conversation history in prompts
- Fallback mechanism for quota issues

### 7. Conversation Memory (`src/query/conversation_memory.py`)
- Maintains conversation history per session
- Stores last 20 messages
- Provides context for LLM prompts

### 8. FastAPI Server (`src/api/server.py`)
- RESTful API endpoints
- Request/response validation
- CORS support for frontend
- Error handling

## 📝 Example Queries

The system can answer various questions:

1. **Price queries:**
   - "What is the cost of the data analyst course?"
   - "Tell me the price of product management course"

2. **Date queries:**
   - "When does the data analyst batch start?"
   - "What is the start date for product management course?"

3. **EMI/Payment queries:**
   - "Are there any EMI options for the course?"
   - "What payment plans are available?"

4. **Curriculum queries:**
   - "What is the curriculum for data analyst course?"
   - "What topics are covered in the product management course?"

5. **Instructor queries:**
   - "Who are the instructors for product management course?"
   - "Tell me about mentors for data analyst course"

6. **Combined queries:**
   - "Tell me price and date of Nextleap data analysis cohort"
   - "What is the cost and EMI options for product management course?"

## ⚙️ Configuration

### Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key (required)

### Model Configuration

- Primary: `gemini-2.0-flash-exp`
- Fallback: `gemini-1.5-flash` (if 2.0 unavailable)

### CORS Configuration

Backend has CORS enabled for all origins. In production, configure allowed origins in `src/api/server.py`.

## 🧪 Testing

### Test Backend API
```bash
python3 scripts/test_server.py
```

### Test Individual Query
```bash
python3 scripts/query_api.py "Tell me price and date of Nextleap data analysis cohort"
```

### Test Frontend
1. Open http://localhost:3000
2. Try the suggestion buttons
3. Type your own questions
4. Check that answers include source URLs

## 🐛 Troubleshooting

### Backend not starting?
- Check if port 8000 is available
- Verify `GEMINI_API_KEY` is set correctly
- Ensure knowledge base exists (run `build_kb.py`)
- Check backend logs

### Frontend not loading?
- Check if port 3000 is available
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify CORS is enabled in backend

### No answers generated?
- Verify knowledge base has chunks: Check `/health` endpoint
- Ensure scraped data exists in `data/processed/nextleap_courses.json`
- Rebuild knowledge base if needed: `python3 scripts/build_kb.py`

### Quota Exceeded Error?
- The system will automatically fall back to direct context extraction
- Answer quality may be slightly lower but still functional
- Consider upgrading your Gemini API quota

### Conversation memory not working?
- Ensure `session_id` is being sent with requests
- Check that conversation memory is initialized in query handler
- Verify frontend is sending `session_id` in API requests

## 📦 Dependencies

Key dependencies (see `requirements.txt` for full list):

- `fastapi` - Web framework for API
- `uvicorn` - ASGI server
- `google-generativeai` - Gemini LLM integration
- `chromadb` - Vector database
- `sentence-transformers` - Embedding generation
- `beautifulsoup4` - HTML parsing
- `requests` - HTTP requests

## 🔒 Security Notes

- API keys should be stored in environment variables, not in code
- CORS should be configured for specific origins in production
- Consider adding rate limiting for production use
- Validate and sanitize all user inputs

## 🚀 Production Considerations

1. **API Key Security**: Store API key in environment variables or secure vault
2. **Rate Limiting**: Implement rate limiting for API endpoints
3. **CORS**: Configure allowed origins in production
4. **Error Logging**: Add proper logging for production
5. **Monitoring**: Set up monitoring for API health and performance
6. **Caching**: Consider caching for common queries
7. **Authentication**: Add authentication/authorization if needed

## 📈 Future Enhancements

- [ ] Selenium integration for JavaScript-rendered content
- [ ] Automated data validation and monitoring
- [ ] Scheduled data updates
- [ ] Enhanced error handling and logging
- [ ] Rate limiting and authentication
- [ ] Multi-language support
- [ ] Analytics and usage tracking

## 📄 License

This project is for educational/demonstration purposes.

## 🤝 Contributing

This is a project-specific implementation. For modifications, please follow the existing code structure and patterns.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at http://localhost:8000/docs
3. Check backend and frontend logs

---

**Built with ❤️ for NextLeap FAQ assistance**
