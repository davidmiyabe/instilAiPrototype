# Nonprofit CRM Data Layer

A complete data ingestion and schema layer for a nonprofit CRM proof-of-concept.

## Overview

This project provides a robust, normalized database schema for managing nonprofit constituent relationships, including donors, volunteers, board members, contributions, interactions, opportunities, and financial transactions.

## Features

- **Normalized SQL Schema**: Properly structured tables with relationships and constraints
- **Data Validation**: Built-in data cleaning and validation during ingestion
- **ORM Models**: SQLAlchemy models for easy database interaction
- **Flexible Database Support**: Works with SQLite and PostgreSQL
- **Comprehensive Indexing**: Optimized queries with strategic indexes
- **Data Quality Handling**: Graceful handling of missing/null values
- **🆕 AI-Driven Insights**: Intelligent donor analysis using Claude 3.5 Sonnet (see [INSIGHTS_README.md](INSIGHTS_README.md))
- **🆕 Donor Segmentation**: RFM (Recency, Frequency, Monetary) analysis and engagement scoring
- **🆕 REST API**: Flask-based API for insights and segmentation

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
├── test_insights.py       # Test suite for insights engine
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
├── README.md              # This file
├── INSIGHTS_README.md     # Detailed insights engine documentation
├── nonprofit_crm.db       # SQLite database (generated)
├── src/                   # Source code
│   ├── segmentation/      # Donor segmentation engine
│   │   └── engine.py      # RFM analysis and segmentation
│   └── insights/          # AI insights engine
│       ├── engine.py      # Claude-powered insights generation
│       ├── prompts.py     # AI prompt templates
│       └── data_summary.py # Database aggregation functions
├── api/                   # REST API
│   └── insights.py        # Flask API endpoints
└── /mnt/data/            # CSV data files (if using file-based loading)
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

## Usage

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

## AI-Driven Insights Engine

The project now includes an AI-powered insights engine that analyzes your donor data and generates strategic fundraising recommendations.

### Quick Start

1. **Install dependencies** (if not already installed):
```bash
pip install -r requirements.txt
```

2. **Set up your Anthropic API key**:
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

3. **Test the segmentation engine** (no API key needed):
```bash
python test_insights.py
```

4. **Start the API server**:
```bash
python api/insights.py
```

5. **Generate insights**:
```bash
curl http://localhost:5000/api/insights
```

### What You Get

The insights engine provides 4-6 strategic recommendations covering:

- **Giving Trends**: Patterns in contribution behavior and seasonality
- **Engagement Risks**: Donors at risk of lapsing or declining engagement
- **Upgrade Opportunities**: Potential for increased giving and major gifts
- **Portfolio Suggestions**: Strategic recommendations for donor management

Each insight includes:
- **Title**: Clear, compelling headline
- **Description**: Analysis with supporting data
- **Impact**: Quantified potential impact
- **Recommended Action**: Specific next steps

### Example Insight

```json
{
  "title": "Champions Segment Shows Strong Momentum",
  "description": "Your 2 Champion donors have contributed $27,500 (35.9% of total giving) with perfect engagement scores...",
  "impact": "Maintaining these relationships could secure $30,000+ in annual recurring revenue.",
  "recommended_action": "Schedule quarterly stewardship meetings with each Champion..."
}
```

### API Endpoints

- `GET /api/insights` - Generate AI-powered insights
- `GET /api/segmentation` - Get donor segmentation (RFM analysis)
- `GET /api/segmentation/rfm` - Get RFM scores
- `GET /api/segmentation/engagement` - Get engagement metrics
- `POST /api/insights/focused` - Get focused analysis on specific area

See [INSIGHTS_README.md](INSIGHTS_README.md) for complete documentation.

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
