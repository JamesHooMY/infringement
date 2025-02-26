# Infringement services

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
- 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🚀 [React](https://react.dev) for the frontend.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.

### Dashboard Login

[![API docs](img/login.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Admin

[![API docs](img/dashboard.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Create User

[![API docs](img/dashboard-create.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Items

[![API docs](img/dashboard-items.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - User Settings

[![API docs](img/dashboard-user-settings.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Current Companies

[![API docs](img/companies.jpg)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Current Patents

[![API docs](img/patents.jpg)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Infringement Analysis

[![API docs](img/infringement_analysis.jpg)](https://github.com/fastapi/full-stack-fastapi-template)

### Dashboard - Dark Mode

[![API docs](img/dashboard-dark.png)](https://github.com/fastapi/full-stack-fastapi-template)

### Interactive API Documentation

[![API docs](img/docs.png)](https://github.com/fastapi/full-stack-fastapi-template)

## Database ER Diagram

```mermaid
%%{init: {'theme': 'dark'}}%%
erDiagram
    USER {
        UUID id PK
        string email "unique, indexed"
        boolean is_active
        boolean is_superuser
        string full_name
        string hashed_password
    }

    ITEM {
        UUID id PK
        string title
        string description
        UUID owner_id FK "references USER(id)"
    }

    PATENT {
        UUID id PK
        string publication_number "unique, indexed"
        string title
        string ai_summary
        string raw_source_url
        string assignee
        string abstract
        string description
        datetime priority_date
        datetime application_date
        datetime grant_date
        string jurisdictions
        string classifications
        JSON application_events
        JSON citations
        JSON image_urls
        JSON landscapes
        datetime created_at
        datetime updated_at
        datetime publish_date
        string citations_non_patent
        string provenance
        JSON attachment_urls
        JSON inventors
        JSON claims
    }

    COMPANY {
        UUID id PK
        string name "unique, indexed"
        JSON products
    }

    INFRINGEMENT_ANALYSIS {
        UUID id PK
        datetime analysis_date
        string overall_risk_assessment
        string patent_id FK "references PATENT(publication_number)"
        string company_name FK "references COMPANY(name)"
        JSON top_infringing_products
        string explanation
    }

    USER ||--o{ ITEM : owns
    PATENT ||--o{ INFRINGEMENT_ANALYSIS : analyzed_in
    COMPANY ||--o{ INFRINGEMENT_ANALYSIS : involved_in
```


## How to start the services

1. Change the value of `OPENAI_API_KEY` in the `.env` file to your key. This free key can be obtained from [FreeChatgptAPI](https://github.com/popjane/free_chatgpt_api?tab=readme-ov-file#%E9%A1%B9%E7%9B%AE%E4%BB%8B%E7%BB%8D).

2. Run the following command to start the services:
```bash
docker-compose up -d
```

3. Open your browser and go to `http://localhost:5173/login`.

4. You can log in with the default admin user below:
- **Username:** `james_test@yopmail.com`
- **Password:** `password`


## Optimized system design for the best performance and scalability.
```mermaid
%%{init: {'theme': 'dark'}}%%
graph TD;
    %% API Layer: User, API Gateway, and FastAPI Service
    subgraph "API Layer"
       User[User Frontend Request]
       API_Gateway[API Gateway]
       FastAPI[FastAPI Service]
    end

    %% AI Service Management Layer: Managing AI Models, Task Scheduling, and Authentication
    subgraph "AI Service Management Layer"
       AI_ServiceMgmt[AI Service Management]
       AI_Model1[Patent Application Drafting]
       AI_Model2[Infringement Detection]
       AI_Model3[Claim Charts]
       AI_Model4[Patent Pruning]
       AI_ServiceMgmt -->|Dispatch| AI_Model1
       AI_ServiceMgmt -->|Dispatch| AI_Model2
       AI_ServiceMgmt -->|Dispatch| AI_Model3
       AI_ServiceMgmt -->|Dispatch| AI_Model4
       TaskQueue[Task Queue Celery / Redis Queue]
       Identity[Identity & Access Management OAuth2 / JWT]
    end

    %% Storage and Caching Layer: Persistent Storage and Caching Services
    subgraph "Storage & Caching"
       DB[PostgreSQL / MongoDB Historical Data Storage]
       Cache[Redis Cache]
    end

    %% Big Data Processing Layer: Hadoop and Spark for Batch Data Processing
    subgraph "Big Data Processing Layer"
       HDFS[Hadoop HDFS Raw Data / Result Storage]
       Spark[Spark Batch Data Processing]
    end

    %% Data Crawling Layer: Web Crawlers for Data Collection
    subgraph "Data Crawling Layer"
       Crawler[Web Crawler Service]
    end

    %% Data Flow Connections
    %% Frontend Requests Enter API Layer
    User -->|API Request| API_Gateway
    API_Gateway -->|HTTP/gRPC| FastAPI

    %% FastAPI Queries Cache and DB
    FastAPI -->|Query Cache| Cache
    Cache -- Cache Hit --> FastAPI
    Cache -- Cache Miss --> DB
    DB -- Data Found --> FastAPI
    DB -- No Result --> AI_ServiceMgmt

    %% FastAPI Sends Query Request to AI Service Management
    FastAPI -->|Query AI Service| AI_ServiceMgmt

    %% AI Analysis Results Stored in DB
    AI_Model1 -->|Analysis Result| DB
    AI_Model2 -->|Analysis Result| DB
    AI_Model3 -->|Analysis Result| DB
    AI_Model4 -->|Analysis Result| DB

    %% API Gateway Handles Authentication and Task Distribution
    API_Gateway -->|Authentication| Identity
    API_Gateway -->|Distribute Task| TaskQueue
    TaskQueue --> AI_ServiceMgmt

    %% Big Data Processing Flow: Crawling, HDFS, and Spark Processing
    Crawler -->|Crawl Data| HDFS
    HDFS -->|Raw Data| Spark
    Spark -->|Processed Data| DB
    DB -- Spark Processed Data --> AI_ServiceMgmt

    %% Final Results Returned to User
    FastAPI -->|Return Result| User

```