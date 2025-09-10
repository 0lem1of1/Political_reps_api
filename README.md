# Civic Tracker API 
A prototype API built to return U.S. political representative details for a given ZIP code. This project was developed as a technical challenge submission and demonstrates a full end-to-end data pipeline, from web scraping to API delivery.
## Project Overview
This project is a three-part system designed to be scalable and easy to set up:
Scraper Agent: A Python script that automatically fetches live representative data from official sources (ziplook.house.gov, senate.gov, nga.org).
Database: A PostgreSQL database running in a Docker container. It uses a simple, effective schema to store geographic, representative, and mapping information.
API Server: A high-performance API built with FastAPI that serves the stored data as a clean JSON response.
## Tech Stack
* Backend: Python 3.9+
* API Framework: FastAPI
* Web Server: Uvicorn
* Database: PostgreSQL
* Containerization: Docker & Docker Compose
* Web Scraping: requests & BeautifulSoup
## Setup and Installation
### Prerequisites

* Docker and Docker Compose
* Python (version 3.9 or newer)
* psql (PostgreSQL command-line client)

### Step 1: Clone the Repository
First, get the project code onto your local machine.

```
git clone https://github.com/your-username/civic-tracker-api.git
cd civic-tracker-api
```

### Step 2: Set Up Environment Variables
Create a .env file from the provided template. The default values are configured to work with the Docker setup.
```
cp .env.example .env
```

### Step 3: Set Up the Python Environment
Create a virtual environment and install the required packages.

#### Create a virtual environment
```
python -m venv venv
```
#### Activate it (on macOS/Linux)
```
source venv/bin/activate
```

#### On Windows, use: 
```
venv\Scripts\activate
```
#### Install dependencies
```
pip install -r requirements.txt
```

### Step 4: Start the Database

#### Use Docker Compose to start the PostgreSQL database container in the background.
```
docker compose up -d
```

To can check if the database is running with
``` 
 docker compose ps
```

### Step 5: Create the Database Schema

With the database running, execute the setup script to create all the necessary tables.
```
psql "postgresql://user:password@localhost:5432/civic_tracker" -f setup_database.sql
```

### Step 6: Populate the Database
Run the scraper agent to fetch live data and store it in your new tables.
```
python scraper/agent.py
```

### Step 7: Run the API Server
Finally, start the API using the Uvicorn server.
```
uvicorn api.main:app --reload
```

The server will be running at http://127.0.0.1:8000.
## API Usage
Your API is now live and ready to be used.
### Interactive Documentation
FastAPI automatically generates interactive documentation. Open your browser and navigate to:
`http://127.0.0.1:8000/docs`

### Example Request (curl)
You can test the endpoint from your terminal using curl.
```
curl http://127.0.0.1:8000/representatives?zip=11355
```

### Example Response
If the scraper was successful, you should receive a JSON response like this:
```
{
  "zip": "11355",
  "representatives": [
    {
      "name": "Grace Meng",
      "title": "U.S. House Rep, NY-06",
      "branch": "Federal"
    },
    {
      "name": "Charles E. Schumer",
      "title": "U.S. Senator, NY",
      "branch": "Federal"
    },
    {
      "name": "Kirsten E. Gillibrand",
      "title": "U.S. Senator, NY",
      "branch": "Federal"
    },
    {
      "name": "Kathy Hochul",
      "title": "Governor, New York",
      "branch": "State"
    }
  ]
}
```



