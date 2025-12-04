# Contract Risk Analysis Agent

AI-powered contract analyzer that identifies risks, calculates severity scores, and suggests remediation actions using OpenAI's GPT models.

## Quick Start (Docker)

```bash
# Clone and configure
git clone <repo>
cd ContractsConnected

# Set your OpenAI API key
cp .env.example .env
# Edit backend/.env and add: OPENAI_API_KEY=sk-your-key-here

# Start everything
docker-compose up --build

# Access application
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

## Quick Start (Local Development)

### Backend

```bash
cd backend

# Setup Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Access at http://localhost:5173
```

## Features

- **Contract Upload**: PDF and TXT files (max 10MB)
- **6 Risk Categories**: Missing Insurance, Uncapped Liability, Vague Payment Terms, Broad Indemnification, Missing Termination, Ambiguous Scope
- **Risk Scoring**: 0-100 severity scale (LOW, MEDIUM, HIGH, CRITICAL)
- **Remediation Suggestions**: Actionable fixes for each risk
- **Real-time Progress**: Async analysis with status updates

## API Endpoints

### Health Check
```
GET /api/v1/health
```

### Upload Contract
```
POST /api/v1/contracts/upload
Content-Type: multipart/form-data
- file: (PDF or TXT file)

Response (202 Accepted):
{
  "analysis_id": "...",
  "status": "pending",
  "injection_detected": false,
  "redactions_found": []
}
```

### Get Status
```
GET /api/v1/contracts/{analysis_id}/status
```

### Get Results
```
GET /api/v1/contracts/{analysis_id}/results

Response (200 OK):
{
  "analysis_id": "...",
  "status": "completed",
  "risks": [
    {
      "category": "uncapped_liability",
      "title": "...",
      "severity_score": 85,
      "severity_level": "CRITICAL",
      "description": "...",
      "remediation": {...}
    }
  ],
  "overall_risk_score": 72,
  "summary": "..."
}
```

## Configuration

### Backend (.env)

```env
# OpenAI API
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.1

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,txt

# CORS (frontend access)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Analysis
MAX_CONCURRENT_ANALYSES=5
ANALYSIS_TIMEOUT_SECONDS=300
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## Risk Categories

| Category | Description |
|----------|-------------|
| **missing_insurance** | No required insurance coverage or inadequate limits |
| **uncapped_liability** | Unlimited liability exposure or unreasonable caps |
| **vague_payment_terms** | Unclear payment schedules or ambiguous conditions |
| **broad_indemnification** | Overly broad indemnification obligations |
| **missing_termination** | Lack of termination rights or procedures |
| **ambiguous_scope** | Unclear scope of work or undefined deliverables |

## Severity Levels

- **LOW** (0-25): Minor issue, low impact
- **MEDIUM** (26-50): Moderate concern
- **HIGH** (51-75): Significant risk
- **CRITICAL** (76-100): Severe risk requiring immediate attention

## Project Structure

```
ContractsConnected/
├── backend/
│   ├── app/
│   │   ├── agents/        # LangGraph orchestration
│   │   ├── api/           # FastAPI routes & schemas
│   │   ├── core/          # PDF parsing
│   │   └── utils/         # Logging, exceptions
│   ├── .env.example
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── services/      # API client
│   │   └── types/         # TypeScript types
│   ├── .env.example
│   └── package.json
└── docker-compose.yml
```

## Analysis Flow

```
User uploads contract
         ↓
[Parse] - Validate input
         ↓
[Extract] - Identify key clauses
         ↓
[Detect] - Analyze for risks
         ↓
[Score] - Calculate severity (0-100)
         ↓
[Remediation] - Generate suggestions
         ↓
Return results to user
```

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend**: Python, FastAPI, LangGraph, LangChain
- **LLM**: OpenAI GPT-4o-mini / GPT-3.5-turbo
- **PDF**: PyPDF2, pdfplumber
- **Container**: Docker Compose

## Troubleshooting

### "Invalid OpenAI API key"
- Verify your API key in `.env` is correct
- Ensure key starts with `sk-`
- Check key has not been revoked in OpenAI dashboard

### Backend won't start
```bash
# Check logs
docker logs contract_analysis_backend

# Rebuild containers
docker-compose down
docker-compose up --build
```

### Frontend can't connect to API
- Ensure backend is running on port 8000
- Check `VITE_API_URL` in frontend/.env matches backend URL
- Verify CORS origins in backend/.env include frontend URL

### File upload fails
- Check file size (max 10MB)
- Ensure file is PDF or TXT format
- Verify MAX_FILE_SIZE_MB in .env is sufficient

## Performance

- Upload: ~1-2 seconds
- PDF parsing: 2-5 seconds
- Risk analysis: 30-60 seconds
- Total: ~35-70 seconds per contract

## Limitations

- Max file size: 10MB
- Supported formats: PDF, TXT
- Requires OpenAI API key
- Analysis timeout: 5 minutes
- Currently no authentication (for PoC)

## Next Steps

- Add user authentication
- Implement database persistence
- Add batch processing
- Create PDF report export
- Add rate limiting
- Implement caching with Redis

## License

MIT License

---

**Version**: 1.0.0
**Status**: Working PoC
**Last Updated**: December 2025
