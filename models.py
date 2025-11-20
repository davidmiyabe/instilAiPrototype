"""
Nonprofit CRM ORM Models
SQLAlchemy models for the nonprofit CRM database
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    Numeric,
    ForeignKey,
    CheckConstraint,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()


class Constituent(Base):
    """
    Represents donors, volunteers, board members, and other constituents
    in the nonprofit CRM system.
    """
    __tablename__ = 'constituents'

    constituent_id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)
    constituent_type = Column(String(50), nullable=False)
    created_date = Column(Date, nullable=False)
    total_lifetime_giving = Column(Numeric(12, 2), default=Decimal('0.00'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contributions = relationship(
        "Contribution",
        back_populates="constituent",
        cascade="all, delete-orphan"
    )
    interactions = relationship(
        "Interaction",
        back_populates="constituent",
        cascade="all, delete-orphan"
    )
    opportunities = relationship(
        "Opportunity",
        back_populates="constituent",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            constituent_type.in_([
                'Donor', 'Volunteer', 'Board Member',
                'Major Donor', 'Staff', 'Other'
            ]),
            name='chk_constituent_type'
        ),
        Index('idx_constituents_email', 'email'),
        Index('idx_constituents_type', 'constituent_type'),
        Index('idx_constituents_created_date', 'created_date'),
        Index('idx_constituents_name', 'last_name', 'first_name'),
    )

    def __repr__(self):
        return f"<Constituent(id={self.constituent_id}, name='{self.first_name} {self.last_name}', type='{self.constituent_type}')>"

    @property
    def full_name(self) -> str:
        """Returns the full name of the constituent."""
        return f"{self.first_name} {self.last_name}"


class Contribution(Base):
    """
    Represents monetary and in-kind contributions from constituents.
    """
    __tablename__ = 'contributions'

    contribution_id = Column(Integer, primary_key=True)
    constituent_id = Column(
        Integer,
        ForeignKey('constituents.constituent_id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )
    contribution_date = Column(Date, nullable=False)
    amount = Column(Numeric(12, 2), nullable=True)
    contribution_type = Column(String(50), nullable=False)
    campaign_id = Column(String(50), nullable=True)
    payment_method = Column(String(50), nullable=True)
    acknowledgment_sent = Column(String(3), default='No')
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    constituent = relationship("Constituent", back_populates="contributions")
    transactions = relationship(
        "Transaction",
        back_populates="contribution",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            contribution_type.in_([
                'Cash', 'In-Kind', 'Stock', 'Pledge',
                'Planned Gift', 'Other'
            ]),
            name='chk_contribution_type'
        ),
        CheckConstraint(
            "amount IS NULL OR amount >= 0",
            name='chk_amount_positive'
        ),
        CheckConstraint(
            acknowledgment_sent.in_(['Yes', 'No', '']),
            name='chk_acknowledgment'
        ),
        Index('idx_contributions_constituent', 'constituent_id'),
        Index('idx_contributions_date', 'contribution_date'),
        Index('idx_contributions_campaign', 'campaign_id'),
        Index('idx_contributions_type', 'contribution_type'),
        Index('idx_contributions_amount', 'amount'),
    )

    def __repr__(self):
        return f"<Contribution(id={self.contribution_id}, constituent_id={self.constituent_id}, amount=${self.amount}, date={self.contribution_date})>"


class Interaction(Base):
    """
    Represents interactions (meetings, calls, emails, events) with constituents.
    """
    __tablename__ = 'interactions'

    interaction_id = Column(Integer, primary_key=True)
    constituent_id = Column(
        Integer,
        ForeignKey('constituents.constituent_id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )
    interaction_date = Column(Date, nullable=False)
    interaction_type = Column(String(50), nullable=False)
    subject = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    staff_member = Column(String(100), nullable=True)
    follow_up_required = Column(String(3), default='No')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    constituent = relationship("Constituent", back_populates="interactions")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            interaction_type.in_([
                'Phone Call', 'Email', 'Meeting', 'Event',
                'Letter', 'Text', 'Other'
            ]),
            name='chk_interaction_type'
        ),
        CheckConstraint(
            follow_up_required.in_(['Yes', 'No', '']),
            name='chk_follow_up'
        ),
        Index('idx_interactions_constituent', 'constituent_id'),
        Index('idx_interactions_date', 'interaction_date'),
        Index('idx_interactions_type', 'interaction_type'),
        Index('idx_interactions_staff', 'staff_member'),
    )

    def __repr__(self):
        return f"<Interaction(id={self.interaction_id}, constituent_id={self.constituent_id}, type='{self.interaction_type}', date={self.interaction_date})>"


class Opportunity(Base):
    """
    Represents fundraising opportunities and pipeline management.
    """
    __tablename__ = 'opportunities'

    opportunity_id = Column(Integer, primary_key=True)
    constituent_id = Column(
        Integer,
        ForeignKey('constituents.constituent_id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )
    opportunity_name = Column(String(255), nullable=False)
    stage = Column(String(50), nullable=False)
    expected_amount = Column(Numeric(12, 2), nullable=True)
    expected_close_date = Column(Date, nullable=True)
    probability = Column(Integer, nullable=True)
    created_date = Column(Date, nullable=False)
    assigned_to = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    constituent = relationship("Constituent", back_populates="opportunities")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            stage.in_([
                'Qualification', 'Cultivation', 'Proposal', 'Negotiation',
                'Committed', 'Closed Won', 'Closed Lost'
            ]),
            name='chk_opportunity_stage'
        ),
        CheckConstraint(
            "probability IS NULL OR (probability >= 0 AND probability <= 100)",
            name='chk_probability_range'
        ),
        CheckConstraint(
            "expected_amount IS NULL OR expected_amount >= 0",
            name='chk_expected_amount_positive'
        ),
        Index('idx_opportunities_constituent', 'constituent_id'),
        Index('idx_opportunities_stage', 'stage'),
        Index('idx_opportunities_close_date', 'expected_close_date'),
        Index('idx_opportunities_assigned', 'assigned_to'),
        Index('idx_opportunities_amount', 'expected_amount'),
    )

    def __repr__(self):
        return f"<Opportunity(id={self.opportunity_id}, name='{self.opportunity_name}', stage='{self.stage}', amount=${self.expected_amount})>"

    @property
    def weighted_amount(self) -> Optional[Decimal]:
        """Calculate weighted amount based on probability."""
        if self.expected_amount and self.probability:
            return self.expected_amount * Decimal(self.probability) / Decimal(100)
        return None


class Transaction(Base):
    """
    Represents financial transactions related to contributions.
    """
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, primary_key=True)
    contribution_id = Column(
        Integer,
        ForeignKey('contributions.contribution_id', ondelete='RESTRICT', onupdate='CASCADE'),
        nullable=False
    )
    transaction_date = Column(Date, nullable=False)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), nullable=False)
    payment_processor = Column(String(50), nullable=True)
    processor_fee = Column(Numeric(10, 2), default=Decimal('0.00'))
    net_amount = Column(Numeric(12, 2), nullable=True)
    reconciliation_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    contribution = relationship("Contribution", back_populates="transactions")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            transaction_type.in_([
                'Payment', 'Refund', 'Pledge', 'In-Kind',
                'Adjustment', 'Other'
            ]),
            name='chk_transaction_type'
        ),
        CheckConstraint(
            status.in_([
                'Pending', 'Processing', 'Completed',
                'Failed', 'Cancelled', 'Refunded'
            ]),
            name='chk_transaction_status'
        ),
        CheckConstraint(
            "amount >= 0",
            name='chk_transaction_amount_positive'
        ),
        CheckConstraint(
            "processor_fee IS NULL OR processor_fee >= 0",
            name='chk_processor_fee_positive'
        ),
        Index('idx_transactions_contribution', 'contribution_id'),
        Index('idx_transactions_date', 'transaction_date'),
        Index('idx_transactions_status', 'status'),
        Index('idx_transactions_processor', 'payment_processor'),
        Index('idx_transactions_reconciliation', 'reconciliation_date'),
    )

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, contribution_id={self.contribution_id}, amount=${self.amount}, status='{self.status}')>"


# =============================================================================
# DATABASE UTILITIES
# =============================================================================

def create_database_engine(database_url: str):
    """
    Create a SQLAlchemy engine for the given database URL.

    Args:
        database_url: Database connection string
                     Examples:
                     - SQLite: 'sqlite:///nonprofit_crm.db'
                     - PostgreSQL: 'postgresql://user:pass@localhost/dbname'

    Returns:
        SQLAlchemy Engine instance
    """
    return create_engine(database_url, echo=False)


def init_database(engine):
    """
    Initialize the database by creating all tables.

    Args:
        engine: SQLAlchemy Engine instance
    """
    Base.metadata.create_all(engine)
    print("✓ Database tables created successfully")


def get_session(engine) -> Session:
    """
    Create a new database session.

    Args:
        engine: SQLAlchemy Engine instance

    Returns:
        SQLAlchemy Session instance
    """
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


# =============================================================================
# QUERY UTILITIES
# =============================================================================

def get_constituent_summary(session: Session, constituent_id: int) -> dict:
    """
    Get a summary of a constituent's giving and interactions.

    Args:
        session: Database session
        constituent_id: ID of the constituent

    Returns:
        Dictionary with constituent summary data
    """
    constituent = session.query(Constituent).filter_by(
        constituent_id=constituent_id
    ).first()

    if not constituent:
        return None

    total_contributions = session.query(func.count(Contribution.contribution_id)).filter(
        Contribution.constituent_id == constituent_id
    ).scalar()

    total_given = session.query(func.sum(Contribution.amount)).filter(
        Contribution.constituent_id == constituent_id
    ).scalar() or Decimal('0.00')

    total_interactions = session.query(func.count(Interaction.interaction_id)).filter(
        Interaction.constituent_id == constituent_id
    ).scalar()

    return {
        'constituent_id': constituent.constituent_id,
        'full_name': constituent.full_name,
        'email': constituent.email,
        'constituent_type': constituent.constituent_type,
        'total_contributions': total_contributions,
        'total_given': float(total_given),
        'total_interactions': total_interactions,
        'total_lifetime_giving': float(constituent.total_lifetime_giving or 0)
    }


def get_campaign_performance(session: Session) -> List[dict]:
    """
    Get performance metrics for all campaigns.

    Args:
        session: Database session

    Returns:
        List of dictionaries with campaign performance data
    """
    from sqlalchemy import func

    results = session.query(
        Contribution.campaign_id,
        func.count(Contribution.contribution_id).label('count'),
        func.sum(Contribution.amount).label('total'),
        func.avg(Contribution.amount).label('average')
    ).filter(
        Contribution.campaign_id.isnot(None)
    ).group_by(
        Contribution.campaign_id
    ).order_by(
        func.sum(Contribution.amount).desc()
    ).all()

    return [
        {
            'campaign_id': r.campaign_id,
            'contribution_count': r.count,
            'total_raised': float(r.total or 0),
            'average_gift': float(r.average or 0)
        }
        for r in results
    ]


# Database session management for FastAPI
from sqlalchemy.orm import sessionmaker

# Create engine (will be initialized by the FastAPI app)
engine = None
SessionLocal = None


def init_db(database_url: str = "sqlite:///nonprofit_crm.db"):
    """
    Initialize the database engine and session factory.

    Args:
        database_url: Database connection string
    """
    global engine, SessionLocal
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency function for FastAPI to get database sessions.

    Yields:
        Database session
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
