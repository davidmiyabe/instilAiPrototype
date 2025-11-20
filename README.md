# Nonprofit CRM Platform

A complete nonprofit CRM solution with data ingestion layer and modern web dashboard.

## Overview

This project provides a robust, normalized database schema for managing nonprofit constituent relationships, including donors, volunteers, board members, contributions, interactions, opportunities, and financial transactions. It includes a world-class dashboard UI built with Next.js for visualizing and exploring the data.

## Features

### Backend (Python)
- **Normalized SQL Schema**: Properly structured tables with relationships and constraints
- **Data Validation**: Built-in data cleaning and validation during ingestion
- **ORM Models**: SQLAlchemy models for easy database interaction
- **Flexible Database Support**: Works with SQLite and PostgreSQL
- **Comprehensive Indexing**: Optimized queries with strategic indexes
- **Data Quality Handling**: Graceful handling of missing/null values

### Frontend (Next.js Dashboard)
- **Modern UI**: Built with Next.js 15, Tailwind CSS, and shadcn/ui
- **AI Insights**: Real-time metrics and performance indicators
- **Segment Analysis**: Constituent segmentation with detailed analytics
- **Responsive Design**: Mobile-friendly interface with smooth animations
- **Type-Safe**: Full TypeScript support
- **Optimized Performance**: React Query for efficient data fetching

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
├── requirements.txt        # Python dependencies
├── nonprofit_crm.db       # SQLite database (generated)
└── /mnt/data/             # CSV data files
    ├── constituents.csv
    ├── contributions.csv
    ├── interactions.csv
    ├── opportunities.csv
    └── transactions.csv
```

## Installation

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) For PostgreSQL support:
```bash
pip install psycopg2-binary
```

### Frontend Setup

1. Install Node.js dependencies:
```bash
npm install
```

2. Build the dashboard:
```bash
npm run build
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

### Running the Dashboard

After loading data, start the dashboard:

**Development mode:**
```bash
npm run dev
```

**Production mode:**
```bash
npm run build
npm start
```

The dashboard will be available at `http://localhost:3000` and provides:
- **Key Insights**: Overview of constituent metrics, contributions, and engagement
- **Segment Analysis**: Detailed breakdown by constituent type (Donors, Volunteers, Board Members, etc.)
- **Interactive Navigation**: Click on any segment to view detailed analytics and top constituents
- **Real-time Data**: Automatic data fetching with loading states

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
