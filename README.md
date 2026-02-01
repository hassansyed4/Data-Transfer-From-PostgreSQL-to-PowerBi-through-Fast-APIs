Project Structure:
app/
│
├── api/
│   ├── routes/
│   │   ├── auth.py          # Login & token generation
│   │   ├── analytics.py    # Analytics endpoints
│   │
│   └── deps.py              # Dependency injection
│
├── core/
│   ├── config.py            # App configuration
│   └── security.py          # JWT & security utilities
│
├── db/
│   ├── init_db.py           # DB initialization
│   ├── session.py           # DB session management
│   └── seed.py              # Sample seed data
│
├── main.py                  # FastAPI app entry point
│
docker-compose.yml           # PostgreSQL container setup
requirements.txt             # Python dependencies
README.md                    # Project documentation
.gitignore                   # Git ignore rules
