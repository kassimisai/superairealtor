# Ready Set Realtor

An AI-driven platform for real estate professionals that automates lead management, communication, and transaction coordination.

## Features

- **AI-Driven Lead Engagement**
  - Automated calling, texting, and emailing
  - Dynamic conversation handling
  - Lead qualification and scoring
  - Follow-up management

- **Smart Scheduling**
  - Automated appointment setting
  - Calendar management
  - Reminders and notifications
  - Conflict resolution

- **Transaction Coordination**
  - Document generation and management
  - Milestone tracking
  - Deadline management
  - E-signature integration

- **CRM Integration**
  - Two-way sync with popular CRM systems
  - Lead import/export
  - Activity tracking
  - Custom field mapping

## Technology Stack

- **Frontend**
  - Next.js 14
  - React with TypeScript
  - TailwindCSS
  - Shadcn UI

- **Backend**
  - FastAPI
  - SQLAlchemy
  - Pydantic
  - Celery

- **AI/ML**
  - OpenAI GPT-4
  - LangChain
  - Custom MCP Implementation

- **Database**
  - PostgreSQL (via Supabase)
  - Redis for caching

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ready-set-realtor.git
   cd ready-set-realtor
   ```

2. Set up the backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Set up the frontend:
   ```bash
   cd ../frontend
   npm install
   ```

5. Start the development servers:
   ```bash
   # Backend
   cd backend
   uvicorn app.main:app --reload

   # Frontend
   cd frontend
   npm run dev
   ```

## Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ready_set_realtor

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Supabase
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Other APIs
VAPI_API_KEY=your_vapi_api_key
DOCUSIGN_API_KEY=your_docusign_api_key
```

## Project Structure

```
ready-set-realtor/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── mcp/
│   ├── agents/
│   └── tests/
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
└── docs/
```

## AI Agents

The platform uses several specialized AI agents:

1. **Lead Generation Agent**
   - Qualifies leads
   - Schedules initial appointments
   - Manages lead scoring

2. **Transaction Coordinator Agent**
   - Manages document generation
   - Tracks transaction milestones
   - Handles deadline management

3. **Follow-up Agent**
   - Manages nurture campaigns
   - Handles regular check-ins
   - Processes feedback

4. **Scheduler Agent**
   - Manages appointments
   - Handles calendar conflicts
   - Sends reminders

## API Documentation

The API documentation is available at `/docs` when running the backend server. It includes:

- Endpoint descriptions
- Request/response schemas
- Authentication requirements
- Example requests

## Testing

Run the test suite:

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email support@readysetrealtor.com or join our Slack channel. 