GameStats Aggregator 🎮
A high-performance, hybrid microservice web application designed to aggregate and display gaming statistics from multiple platforms, including Steam, PlayStation Network (PSN), and Xbox Live.
🚀 Architecture
The project utilizes a multi-stack approach to leverage the best tools for the job:
Core Backend (Orchestrator): Built with ASP.NET Core 10.0. It handles business logic, data aggregation, and serves the unified API to the frontend.
Data Provider (Scraper/Wrapper): Built with Python (FastAPI). It manages the "heavy lifting" of communicating with various gaming APIs (Steam Web API, PSN, and Xbox) using specialized libraries like httpx and psnawp.
Infrastructure: Fully containerized using Docker and Docker Compose for seamless deployment.
✨ Features
Unified Data Model: Translates different API responses from Valve, Sony, and Microsoft into a single, clean JSON format.
Multi-Platform Support:

Steam: Integration via official Web API.

PlayStation: Integration via npsso authentication/scraping (In Progress).

Xbox: Integration via XBL services (In Progress).
Scalable Design: Easy to add new platforms (Epic Games, Nintendo, etc.) by simply updating the Python Provider.
🛠 Tech Stack
C# / .NET 10.0 (Web API)
Python 3.11+ (FastAPI, Uvicorn)
PostgreSQL 16 (Persistent Storage)
Redis 7 (In-Memory Cache)
Docker & Docker Compose
🏁 Getting Started
Prerequisites
Docker Desktop installed and running.
A Steam Web API Key.
Installation & Setup
Clone the repository:
code
Bash
git clone https://github.com/YOUR_USERNAME/GameStats-Aggregator.git
cd GameStats-Aggregator
Configure API Keys:
Open PythonProvider/main.py and replace the placeholder with your actual Steam API Key:
code
Python
STEAM_API_KEY = "YOUR_STEAM_KEY_HERE"
Run with Docker Compose:
code
Bash
docker-compose up --build
API Usage
Once the containers are running, you can access the unified statistics through the .NET Gateway:
Steam Stats: GET http://localhost:5000/api/stats/steam/{steam_id64}
PSN Stats: GET http://localhost:5000/api/stats/psn/{online_id}
Xbox Stats: GET http://localhost:5000/api/stats/xbox/{gamertag}
Cache Metrics: GET http://localhost:5000/api/stats/metrics
📂 Project Structure
code
Text
├── CoreBackend/       # ASP.NET Core 10 project (API Gateway)
├── PythonProvider/    # FastAPI project (Platform Scrapers)
├── docker-compose.yml # Orchestration script
└── README.md          # Project documentation
🗺 Roadmap

Add PostgreSQL for user profile persistence.

Implement Redis caching to prevent API rate-limiting.

Develop a modern Frontend dashboard using React/Next.js.

Add support for Achievements and Trophies comparison.