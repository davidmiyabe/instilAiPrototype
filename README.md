# Nonprofit CRM Data Layer

A complete data ingestion and schema layer for a nonprofit CRM proof-of-concept with AI-powered fundraising message generation.

## Overview

This project provides a robust, normalized database schema for managing nonprofit constituent relationships, including donors, volunteers, board members, contributions, interactions, opportunities, and financial transactions.

## Features

- **Normalized SQL Schema**: Properly structured tables with relationships and constraints
- **Data Validation**: Built-in data cleaning and validation during ingestion
- **ORM Models**: SQLAlchemy models for easy database interaction
- **REST API**: FastAPI-powered REST API for constituent management
- **AI-Powered Message Generation**: Claude AI integration for personalized fundraising messages
- **Flexible Database Support**: Works with SQLite and PostgreSQL
- **Comprehensive Indexing**: Optimized queries with strategic indexes
- **Data Quality Handling**: Graceful handling of missing/null values

## Database Schema

### Tables

1. **constituents**: Core table for donors, volunteers, and board members
   - Primary key: `constituent_id`
   - Indexes on: email, type, created_date, name

2. **contributions**: Monetary and in-kind donations
   - Primary key: `contribution_id`
   - Foreign key: `constituent_id` → constituents
   - Indexes on: constituent, date, campaign, type, amount

3. **interactions**: Communications and meetings with constituents
   - Primary key: `interaction_id`
   - Foreign key: `constituent_id` → constituents
   - Indexes on: constituent, date, type, staff, follow_up

4. **opportunities**: Fundraising pipeline and opportunity management
   - Primary key: `opportunity_id`
   - Foreign key: `constituent_id` → constituents
   - Indexes on: constituent, stage, close_date, assigned, amount

5. **transactions**: Financial transactions related to contributions
   - Primary key: `transaction_id`
   - Foreign key: `contribution_id` → contributions
   - Indexes on: contribution, date, status, processor, reconciliation

### Relationships

```
constituents (1) ──→ (N) contributions
constituents (1) ──→ (N) interactions
constituents (1) ──→ (N) opportunities
contributions (1) ──→ (N) transactions
```

## Project Structure

```
.
├── schema.sql              # SQL schema with tables, constraints, and indexes
├── models.py               # SQLAlchemy ORM models
├── load_data.py           # Data ingestion script
├── main.py                # FastAPI application
├── config.py              # Application configuration
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── nonprofit_crm.db       # SQLite database (generated)
├── api/                   # API layer
│   ├── routes/
│   │   └── message.py     # Message generation endpoints
│   └── schemas/
│       └── message.py     # API request/response schemas
├── src/                   # Business logic
│   └── messages/
│       └── generator.py   # Claude AI message generator
└── /mnt/data/             # CSV data files
    ├── constituents.csv
    ├── contributions.csv
    ├── interactions.csv
    ├── opportunities.csv
    └── transactions.csv
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) For PostgreSQL support:
```bash
pip install psycopg2-binary
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

Get your Anthropic API key from: https://console.anthropic.com/

## Usage

### Running the API Server

Start the FastAPI server:

```bash
python3 main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### Running Data Ingestion

Load all CSV files into the database:

```bash
python3 load_data.py
```

The script will:
- Create/initialize the database schema
- Read and validate all CSV files
- Clean and normalize data
- Load data with proper foreign key ordering
- Display a summary with row counts and statistics

### Using the ORM Models

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Constituent, Contribution, get_constituent_summary

# Create engine and session
engine = create_engine('sqlite:///nonprofit_crm.db')
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Query constituents
donors = session.query(Constituent).filter_by(constituent_type='Donor').all()

# Get constituent summary
summary = get_constituent_summary(session, constituent_id=1)
print(summary)

# Query contributions by campaign
from sqlalchemy import func
campaign_stats = session.query(
    Contribution.campaign_id,
    func.count(Contribution.contribution_id),
    func.sum(Contribution.amount)
).group_by(Contribution.campaign_id).all()

session.close()
```

## API Endpoints

### Message Generation

Generate personalized fundraising messages using Claude AI.

#### Generate Message for Constituent

**Endpoint:** `POST /api/constituents/{constituent_id}/message`

**Request Body:**
```json
{
  "briefing": {
    "campaign_name": "Annual Fund 2025",
    "campaign_goal": 50000.00,
    "campaign_description": "Support our scholarship program for underserved students",
    "organization_mission": "Empowering youth through education and mentorship",
    "key_talking_points": [
      "Last year we served 500 students",
      "Every $100 provides books for one student"
    ],
    "deadline": "December 31, 2025"
  },
  "segment_context": {
    "segment_name": "Major Donors",
    "segment_characteristics": "High-capacity donors who have given $10,000+ lifetime",
    "giving_pattern": "Annual gifts of $1,000-5,000 in November/December"
  },
  "tone": "warm, human, relationship-forward",
  "target_length": 200,
  "generate_alternates": false,
  "num_alternates": 3
}
```

**Response:**
```json
{
  "subject_line": "Your Impact: Transforming Lives Through Education",
  "message": "Dear Sarah, your generous support has been instrumental in our mission to empower youth through education...",
  "alternates": [],
  "metadata": {
    "model": "claude-sonnet-4-20250514",
    "tone": "warm, human, relationship-forward",
    "target_length": 200,
    "timestamp": "2025-01-15T10:30:00",
    "constituent_id": 123,
    "constituent_name": "Sarah Johnson"
  }
}
```

#### Get Constituent Details

**Endpoint:** `GET /api/constituents/{constituent_id}`

Returns detailed constituent information including contribution history, interactions, and opportunities.

### Example: Generate a Fundraising Message

```bash
curl -X POST "http://localhost:8000/api/constituents/1/message" \
  -H "Content-Type: application/json" \
  -d '{
    "briefing": {
      "campaign_name": "Annual Fund 2025",
      "campaign_goal": 50000,
      "campaign_description": "Support our scholarship program",
      "organization_mission": "Empowering youth through education",
      "key_talking_points": ["500 students served last year"]
    },
    "tone": "warm, human, relationship-forward",
    "target_length": 200
  }'
```

### Python Example

```python
import requests

# Generate a fundraising message
response = requests.post(
    "http://localhost:8000/api/constituents/1/message",
    json={
        "briefing": {
            "campaign_name": "Annual Fund 2025",
            "campaign_goal": 50000.00,
            "campaign_description": "Support our scholarship program for underserved students",
            "organization_mission": "Empowering youth through education and mentorship",
            "key_talking_points": [
                "Last year we served 500 students",
                "Every $100 provides books for one student"
            ],
            "deadline": "December 31, 2025"
        },
        "segment_context": {
            "segment_name": "Major Donors",
            "segment_characteristics": "High-capacity donors",
            "giving_pattern": "Annual gifts in Q4"
        },
        "tone": "warm, human, relationship-forward",
        "target_length": 200,
        "generate_alternates": True,
        "num_alternates": 3
    }
)

result = response.json()
print(f"Subject: {result['subject_line']}")
print(f"Message: {result['message']}")
print(f"\nGenerated {len(result['alternates'])} alternate versions")
```

## Message Generator Features

The AI-powered message generator:

- **Personalization**: Incorporates donor's giving history, past interactions, and relationship depth
- **Context-Aware**: References specific campaigns, organizational mission, and key talking points
- **Segment Intelligence**: Adapts messaging based on donor segment characteristics and giving patterns
- **Tone Customization**: Generates messages in your preferred tone (warm, professional, casual, etc.)
- **Length Control**: Creates messages between 150-500 words with configurable target length
- **Multiple Versions**: Optionally generates 3-5 alternate message variations
- **Authentic Voice**: Produces human-sounding, non-generic messages that avoid fundraising clichés
- **Ready to Send**: Includes compelling subject lines and polished message bodies

### Message Generation Best Practices

1. **Provide Rich Briefing Data**: The more context you provide, the better the message
2. **Use Specific Talking Points**: Include concrete impact examples and statistics
3. **Segment Your Donors**: Different segments respond to different messaging approaches
4. **Test Multiple Versions**: Use `generate_alternates: true` to A/B test messages
5. **Review and Edit**: While AI-generated messages are high-quality, always review before sending
6. **Maintain Authenticity**: Adjust tone settings to match your organization's voice

## Configuration

Environment variables (`.env` file):

```bash
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional (with defaults)
ANTHROPIC_MODEL=claude-sonnet-4-20250514
DATABASE_URL=sqlite:///nonprofit_crm.db
API_HOST=0.0.0.0
API_PORT=8000
DEFAULT_TONE=warm, human, relationship-forward
DEFAULT_MESSAGE_LENGTH=200
```

See `.env.example` for all available configuration options.
```

### Database Configuration

#### SQLite (Default)
```python
DATABASE_URL = "sqlite:///nonprofit_crm.db"
```

#### PostgreSQL
```python
DATABASE_URL = "postgresql://username:password@localhost/nonprofit_crm"
```

Edit the `DATABASE_URL` variable in `load_data.py` to switch databases.

## Data Cleaning Features

The ingestion script handles:

- **Missing Values**: Gracefully handles NULL/empty values
- **Date Formats**: Supports multiple date formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
- **Decimal Precision**: Proper handling of monetary values
- **String Normalization**: Trims whitespace and handles empty strings
- **Boolean Conversion**: Converts various formats to Yes/No
- **Data Validation**: Enforces constraints and data types

## Schema Views

The schema includes useful views for reporting:

1. **vw_constituent_summary**: Aggregated giving and interaction data per constituent
2. **vw_active_opportunities**: Current pipeline with weighted amounts
3. **vw_transaction_reconciliation**: Financial reconciliation status

## Example Queries

### Top Donors
```sql
SELECT constituent_id, first_name, last_name, total_lifetime_giving
FROM constituents
ORDER BY total_lifetime_giving DESC
LIMIT 10;
```

### Campaign Performance
```sql
SELECT
    campaign_id,
    COUNT(*) as contribution_count,
    SUM(amount) as total_raised,
    AVG(amount) as average_gift
FROM contributions
WHERE campaign_id IS NOT NULL
GROUP BY campaign_id
ORDER BY total_raised DESC;
```

### Interactions Requiring Follow-up
```sql
SELECT
    i.interaction_id,
    c.first_name || ' ' || c.last_name as constituent_name,
    i.interaction_date,
    i.subject,
    i.staff_member
FROM interactions i
JOIN constituents c ON i.constituent_id = c.constituent_id
WHERE i.follow_up_required = 'Yes'
ORDER BY i.interaction_date;
```

## Data Quality

The ingestion script provides:
- Row counts per table
- Error reporting for failed records
- Data statistics (total giving, average gift, etc.)
- Constituent type breakdown
- Campaign performance metrics

## Extending the Schema

To add new tables:

1. Add table definition to `schema.sql`
2. Create corresponding ORM model in `models.py`
3. Add loader function in `load_data.py`
4. Update the main() function to load the new data

## License

This is a proof-of-concept for educational purposes.

## Support

For issues or questions, please refer to the inline documentation in the code files.
