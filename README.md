## Step 0: Start Docker Desktop

Make sure Docker Desktop is running.

## Step 1: Activate Virtual Environment
.venv\Scripts\activate
You should see: (.venv)


## Step 2: Start PostgreSQL Container

From the project root:

docker compose up -d
docker compose ps


(Optional) Check logs:

docker logs <container_name>
eg: (Optional) Verify DB is ready: docker logs factorytwin_demo_db --tail 20


## Step 3: Start FastAPI Server
uvicorn app.main:app --reload


The API will start at:

http://127.0.0.1:8000

Verify Application

Health Check

http://127.0.0.1:8000/health


Swagger UI

http://127.0.0.1:8000/docs

## Authentication (JWT)
Login Endpoint
POST /api/v1/auth/login

Sample Request
{
  "email": "analyst@customera.com",
  "password": "Pass123!"
}

Response
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}


Tokens expire — re-login when required.

## Power BI Integration

Power BI connects directly to the API, not the database.

## Power Query Example

    let
    BaseUrl = "http://127.0.0.1:8000",
    Token = "PASTE_YOUR_TOKEN_HERE",
    FromTs = "2026-01-01T00:00:00Z",
    ToTs   = "2026-02-01T00:00:00Z",

    Url = BaseUrl & "/api/v1/analytics/production/daily"
        & "?from_ts=" & FromTs
        & "&to_ts=" & ToTs,

    Source =
        Json.Document(
            Web.Contents(
                Url,
                [
                    Headers = [
                        Authorization = "Bearer " & Token,
                        #"Content-Type" = "application/json"
                    ]
                ]
            )
        ),
    Table = Table.FromRecords(Source)
in
    Table

## Project Structure:
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





