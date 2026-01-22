# Loudli v2 - Podcast Advertising Marketplace

A modern platform connecting podcasters with advertisers for sponsored content campaigns.

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy (async)
- **Authentication**: JWT with refresh tokens
- **API Documentation**: OpenAPI/Swagger (auto-generated)
- **External API**: Podcast Index (free, open-source)

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod validation

## Project Structure

```
loudli-v2/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Config, security, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   ├── tests/             # Test files
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── app/           # Next.js pages
    │   ├── components/    # React components
    │   ├── lib/           # Utilities, API client
    │   ├── hooks/         # Custom hooks
    │   └── types/         # TypeScript types
    └── package.json
```

## Getting Started

### Option 1: Docker (Recommended)

The easiest way to run Loudli - no need to install Python, Node.js, or PostgreSQL.

**Prerequisites:** Docker and Docker Compose

```bash
cd loudli-v2

# Start all services (builds on first run)
docker-compose up

# Or run in background
docker-compose up -d
```

That's it! Open:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/v1/docs

**Other Docker commands:**
```bash
# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up --build

# View logs
docker-compose logs -f

# Reset database (delete volume)
docker-compose down -v
```

**Development with hot reload:**
```bash
# Uses mounted volumes for live code updates
docker-compose -f docker-compose.dev.yml up
```

### Option 2: Manual Setup

#### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

#### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your settings
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user
- `PATCH /api/v1/users/me` - Update current user
- `GET /api/v1/users/me/profile` - Get user profile
- `PATCH /api/v1/users/me/profile` - Update profile

### Podcasts
- `GET /api/v1/podcasts` - List podcasts
- `POST /api/v1/podcasts` - Create podcast
- `GET /api/v1/podcasts/{id}` - Get podcast details
- `PATCH /api/v1/podcasts/{id}` - Update podcast
- `DELETE /api/v1/podcasts/{id}` - Delete podcast
- `POST /api/v1/podcasts/{id}/sync` - Sync RSS feed
- `GET /api/v1/podcasts/search/external` - Search Podcast Index
- `GET /api/v1/podcasts/trending` - Get trending podcasts
- `POST /api/v1/podcasts/import` - Import from external source

### Campaigns
- `GET /api/v1/campaigns` - List campaigns
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns/{id}` - Get campaign details
- `PATCH /api/v1/campaigns/{id}` - Update campaign
- `GET /api/v1/campaigns/stats` - Get campaign statistics
- `POST /api/v1/campaigns/{id}/messages` - Send message
- `GET /api/v1/campaigns/{id}/messages` - List messages

## External APIs

### Podcast Index
Free, open-source podcast database. Get API credentials at:
https://podcastindex.org/

Features:
- Search podcasts by keyword
- Get trending podcasts
- Fetch podcast details and episodes
- No rate limits

## Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/loudli
PODCAST_INDEX_API_KEY=your-api-key
PODCAST_INDEX_API_SECRET=your-api-secret
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Security Features

- Environment-based configuration (no hardcoded secrets)
- JWT authentication with refresh tokens
- Password hashing with bcrypt
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (React escaping)

## License

MIT
