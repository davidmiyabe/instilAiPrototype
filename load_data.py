#!/usr/bin/env python3
"""
Nonprofit CRM Data Ingestion Script

This script reads CSV files, cleans and normalizes the data,
and loads it into the database using the ORM models.
"""

import csv
import sys
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import IntegrityError

from models import (
    Base,
    Constituent,
    Contribution,
    Interaction,
    Opportunity,
    Transaction,
    init_database,
)


# =============================================================================
# DATA CLEANING UTILITIES
# =============================================================================

def clean_string(value: Any) -> Optional[str]:
    """
    Clean and normalize string values.

    Args:
        value: Input value to clean

    Returns:
        Cleaned string or None if empty
    """
    if value is None or value == '':
        return None
    return str(value).strip()


def clean_decimal(value: Any) -> Optional[Decimal]:
    """
    Clean and convert to Decimal.

    Args:
        value: Input value to convert

    Returns:
        Decimal value or None if invalid
    """
    if value is None or value == '':
        return None

    try:
        # Remove currency symbols and commas
        cleaned = str(value).replace('$', '').replace(',', '').strip()
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def clean_integer(value: Any) -> Optional[int]:
    """
    Clean and convert to integer.

    Args:
        value: Input value to convert

    Returns:
        Integer value or None if invalid
    """
    if value is None or value == '':
        return None

    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def clean_date(value: Any) -> Optional[datetime.date]:
    """
    Clean and convert to date.

    Args:
        value: Input value to convert (supports multiple formats)

    Returns:
        Date object or None if invalid
    """
    if value is None or value == '':
        return None

    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y/%m/%d',
        '%m-%d-%Y',
    ]

    value_str = str(value).strip()

    for fmt in date_formats:
        try:
            return datetime.strptime(value_str, fmt).date()
        except ValueError:
            continue

    return None


def clean_boolean(value: Any, true_values: List[str] = None) -> str:
    """
    Convert various boolean representations to 'Yes' or 'No'.

    Args:
        value: Input value to convert
        true_values: List of values that should be considered True

    Returns:
        'Yes', 'No', or '' for empty values
    """
    if value is None or value == '':
        return ''

    if true_values is None:
        true_values = ['yes', 'y', 'true', '1', 't']

    return 'Yes' if str(value).lower().strip() in true_values else 'No'


# =============================================================================
# CSV READERS
# =============================================================================

def read_csv_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    Read a CSV file and return list of dictionaries.

    Args:
        file_path: Path to the CSV file

    Returns:
        List of dictionaries representing rows
    """
    if not file_path.exists():
        print(f"⚠ Warning: File not found: {file_path}")
        return []

    rows = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    return rows


# =============================================================================
# DATA LOADERS
# =============================================================================

def load_constituents(session: Session, file_path: Path) -> int:
    """
    Load constituents from CSV into database.

    Args:
        session: Database session
        file_path: Path to constituents CSV file

    Returns:
        Number of records loaded
    """
    print(f"\n📊 Loading constituents from {file_path}...")

    rows = read_csv_file(file_path)
    loaded_count = 0
    error_count = 0

    for row in rows:
        try:
            # Calculate total_lifetime_giving from the CSV if provided
            total_lifetime = clean_decimal(row.get('total_lifetime_giving'))

            constituent = Constituent(
                constituent_id=clean_integer(row['constituent_id']),
                first_name=clean_string(row['first_name']) or 'Unknown',
                last_name=clean_string(row['last_name']) or 'Unknown',
                email=clean_string(row.get('email')),
                phone=clean_string(row.get('phone')),
                address=clean_string(row.get('address')),
                city=clean_string(row.get('city')),
                state=clean_string(row.get('state')),
                zip_code=clean_string(row.get('zip_code')),
                constituent_type=clean_string(row['constituent_type']) or 'Other',
                created_date=clean_date(row['created_date']) or datetime.now().date(),
                total_lifetime_giving=total_lifetime or Decimal('0.00'),
            )

            session.add(constituent)
            loaded_count += 1

        except (KeyError, IntegrityError) as e:
            error_count += 1
            print(f"  ⚠ Error loading constituent {row.get('constituent_id')}: {e}")
            session.rollback()

    session.commit()
    print(f"  ✓ Loaded {loaded_count} constituents ({error_count} errors)")
    return loaded_count


def load_contributions(session: Session, file_path: Path) -> int:
    """
    Load contributions from CSV into database.

    Args:
        session: Database session
        file_path: Path to contributions CSV file

    Returns:
        Number of records loaded
    """
    print(f"\n📊 Loading contributions from {file_path}...")

    rows = read_csv_file(file_path)
    loaded_count = 0
    error_count = 0

    for row in rows:
        try:
            contribution = Contribution(
                contribution_id=clean_integer(row['contribution_id']),
                constituent_id=clean_integer(row['constituent_id']),
                contribution_date=clean_date(row['contribution_date']) or datetime.now().date(),
                amount=clean_decimal(row.get('amount')),
                contribution_type=clean_string(row['contribution_type']) or 'Other',
                campaign_id=clean_string(row.get('campaign_id')),
                payment_method=clean_string(row.get('payment_method')),
                acknowledgment_sent=clean_boolean(row.get('acknowledgment_sent')),
                notes=clean_string(row.get('notes')),
            )

            session.add(contribution)
            loaded_count += 1

        except (KeyError, IntegrityError) as e:
            error_count += 1
            print(f"  ⚠ Error loading contribution {row.get('contribution_id')}: {e}")
            session.rollback()

    session.commit()
    print(f"  ✓ Loaded {loaded_count} contributions ({error_count} errors)")
    return loaded_count


def load_interactions(session: Session, file_path: Path) -> int:
    """
    Load interactions from CSV into database.

    Args:
        session: Database session
        file_path: Path to interactions CSV file

    Returns:
        Number of records loaded
    """
    print(f"\n📊 Loading interactions from {file_path}...")

    rows = read_csv_file(file_path)
    loaded_count = 0
    error_count = 0

    for row in rows:
        try:
            interaction = Interaction(
                interaction_id=clean_integer(row['interaction_id']),
                constituent_id=clean_integer(row['constituent_id']),
                interaction_date=clean_date(row['interaction_date']) or datetime.now().date(),
                interaction_type=clean_string(row['interaction_type']) or 'Other',
                subject=clean_string(row.get('subject')),
                notes=clean_string(row.get('notes')),
                staff_member=clean_string(row.get('staff_member')),
                follow_up_required=clean_boolean(row.get('follow_up_required')),
            )

            session.add(interaction)
            loaded_count += 1

        except (KeyError, IntegrityError) as e:
            error_count += 1
            print(f"  ⚠ Error loading interaction {row.get('interaction_id')}: {e}")
            session.rollback()

    session.commit()
    print(f"  ✓ Loaded {loaded_count} interactions ({error_count} errors)")
    return loaded_count


def load_opportunities(session: Session, file_path: Path) -> int:
    """
    Load opportunities from CSV into database.

    Args:
        session: Database session
        file_path: Path to opportunities CSV file

    Returns:
        Number of records loaded
    """
    print(f"\n📊 Loading opportunities from {file_path}...")

    rows = read_csv_file(file_path)
    loaded_count = 0
    error_count = 0

    for row in rows:
        try:
            opportunity = Opportunity(
                opportunity_id=clean_integer(row['opportunity_id']),
                constituent_id=clean_integer(row['constituent_id']),
                opportunity_name=clean_string(row['opportunity_name']) or 'Unnamed Opportunity',
                stage=clean_string(row['stage']) or 'Qualification',
                expected_amount=clean_decimal(row.get('expected_amount')),
                expected_close_date=clean_date(row.get('expected_close_date')),
                probability=clean_integer(row.get('probability')),
                created_date=clean_date(row['created_date']) or datetime.now().date(),
                assigned_to=clean_string(row.get('assigned_to')),
                notes=clean_string(row.get('notes')),
            )

            session.add(opportunity)
            loaded_count += 1

        except (KeyError, IntegrityError) as e:
            error_count += 1
            print(f"  ⚠ Error loading opportunity {row.get('opportunity_id')}: {e}")
            session.rollback()

    session.commit()
    print(f"  ✓ Loaded {loaded_count} opportunities ({error_count} errors)")
    return loaded_count


def load_transactions(session: Session, file_path: Path) -> int:
    """
    Load transactions from CSV into database.

    Args:
        session: Database session
        file_path: Path to transactions CSV file

    Returns:
        Number of records loaded
    """
    print(f"\n📊 Loading transactions from {file_path}...")

    rows = read_csv_file(file_path)
    loaded_count = 0
    error_count = 0

    for row in rows:
        try:
            transaction = Transaction(
                transaction_id=clean_integer(row['transaction_id']),
                contribution_id=clean_integer(row['contribution_id']),
                transaction_date=clean_date(row['transaction_date']) or datetime.now().date(),
                transaction_type=clean_string(row['transaction_type']) or 'Other',
                amount=clean_decimal(row['amount']) or Decimal('0.00'),
                status=clean_string(row['status']) or 'Pending',
                payment_processor=clean_string(row.get('payment_processor')),
                processor_fee=clean_decimal(row.get('processor_fee')) or Decimal('0.00'),
                net_amount=clean_decimal(row.get('net_amount')),
                reconciliation_date=clean_date(row.get('reconciliation_date')),
            )

            session.add(transaction)
            loaded_count += 1

        except (KeyError, IntegrityError) as e:
            error_count += 1
            print(f"  ⚠ Error loading transaction {row.get('transaction_id')}: {e}")
            session.rollback()

    session.commit()
    print(f"  ✓ Loaded {loaded_count} transactions ({error_count} errors)")
    return loaded_count


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main execution function for data ingestion.
    """
    print("=" * 80)
    print("🚀 Nonprofit CRM Data Ingestion")
    print("=" * 80)

    # Database configuration
    DATABASE_URL = "sqlite:///nonprofit_crm.db"
    # For PostgreSQL, use:
    # DATABASE_URL = "postgresql://username:password@localhost/nonprofit_crm"

    # CSV file paths
    DATA_DIR = Path("/mnt/data")
    csv_files = {
        'constituents': DATA_DIR / "constituents.csv",
        'contributions': DATA_DIR / "contributions.csv",
        'interactions': DATA_DIR / "interactions.csv",
        'opportunities': DATA_DIR / "opportunities.csv",
        'transactions': DATA_DIR / "transactions.csv",
    }

    # Check if data directory exists
    if not DATA_DIR.exists():
        print(f"❌ Error: Data directory not found: {DATA_DIR}")
        sys.exit(1)

    # Create database engine and initialize
    print(f"\n🔧 Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, echo=False)

    print("🔧 Initializing database schema...")
    init_database(engine)

    # Create session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # Load data in order (respecting foreign key dependencies)
        counts = {}

        # 1. Load constituents first (no dependencies)
        counts['constituents'] = load_constituents(
            session, csv_files['constituents']
        )

        # 2. Load contributions (depends on constituents)
        counts['contributions'] = load_contributions(
            session, csv_files['contributions']
        )

        # 3. Load interactions (depends on constituents)
        counts['interactions'] = load_interactions(
            session, csv_files['interactions']
        )

        # 4. Load opportunities (depends on constituents)
        counts['opportunities'] = load_opportunities(
            session, csv_files['opportunities']
        )

        # 5. Load transactions (depends on contributions)
        counts['transactions'] = load_transactions(
            session, csv_files['transactions']
        )

        # Print summary
        print("\n" + "=" * 80)
        print("📈 DATA INGESTION SUMMARY")
        print("=" * 80)
        print(f"  Constituents:  {counts['constituents']:>6} records")
        print(f"  Contributions: {counts['contributions']:>6} records")
        print(f"  Interactions:  {counts['interactions']:>6} records")
        print(f"  Opportunities: {counts['opportunities']:>6} records")
        print(f"  Transactions:  {counts['transactions']:>6} records")
        print("  " + "-" * 40)
        print(f"  TOTAL:         {sum(counts.values()):>6} records")
        print("=" * 80)

        # Generate additional statistics
        print("\n📊 DATABASE STATISTICS")
        print("=" * 80)

        # Total giving
        from sqlalchemy import func
        total_giving = session.query(
            func.sum(Contribution.amount)
        ).scalar() or Decimal('0.00')
        print(f"  Total Contributions: ${total_giving:,.2f}")

        # Average gift
        avg_gift = session.query(
            func.avg(Contribution.amount)
        ).filter(
            Contribution.amount.isnot(None)
        ).scalar() or Decimal('0.00')
        print(f"  Average Gift:        ${avg_gift:,.2f}")

        # Constituent types breakdown
        from sqlalchemy import distinct
        print("\n  Constituent Types:")
        type_counts = session.query(
            Constituent.constituent_type,
            func.count(Constituent.constituent_id)
        ).group_by(
            Constituent.constituent_type
        ).all()

        for const_type, count in type_counts:
            print(f"    {const_type:<20} {count:>4}")

        # Campaign performance
        print("\n  Campaign Performance:")
        campaign_stats = session.query(
            Contribution.campaign_id,
            func.count(Contribution.contribution_id).label('count'),
            func.sum(Contribution.amount).label('total')
        ).filter(
            Contribution.campaign_id.isnot(None)
        ).group_by(
            Contribution.campaign_id
        ).order_by(
            func.sum(Contribution.amount).desc()
        ).all()

        for campaign_id, count, total in campaign_stats[:5]:
            total_val = total or Decimal('0.00')
            print(f"    {campaign_id:<15} {count:>3} gifts  ${total_val:>10,.2f}")

        print("=" * 80)
        print("✅ Data ingestion completed successfully!")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error during data ingestion: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
