"""
Nonprofit CRM API Server
FastAPI application for serving dashboard data
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from typing import List, Dict
import os

from models import (
    Base, Constituent, Contribution, Interaction,
    Opportunity, Transaction
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///nonprofit_crm.db")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create FastAPI app
app = FastAPI(title="Nonprofit CRM API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "Nonprofit CRM API", "version": "1.0.0"}


@app.get("/api/v1/dashboard/stats")
def get_dashboard_stats():
    """Get dashboard statistics"""
    db = next(get_db())

    try:
        # Total constituents
        total_constituents = db.query(func.count(Constituent.constituent_id)).scalar()
        active_constituents = total_constituents  # All constituents are considered active for now

        # Total contributions and amount
        total_contributions = db.query(func.sum(Contribution.amount)).filter(
            Contribution.amount.isnot(None)
        ).scalar() or 0

        # Average contribution
        average_contribution = db.query(func.avg(Contribution.amount)).filter(
            Contribution.amount.isnot(None)
        ).scalar() or 0

        # Recent interactions (last 30 days)
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_interactions = db.query(func.count(Interaction.interaction_id)).filter(
            Interaction.interaction_date >= thirty_days_ago
        ).scalar()

        # Contributions this year
        year_start = datetime(datetime.now().year, 1, 1).date()
        contributions_this_year = db.query(func.sum(Contribution.amount)).filter(
            Contribution.contribution_date >= year_start,
            Contribution.amount.isnot(None)
        ).scalar() or 0

        # Contributions this month
        month_start = datetime(datetime.now().year, datetime.now().month, 1).date()
        contributions_this_month = db.query(func.sum(Contribution.amount)).filter(
            Contribution.contribution_date >= month_start,
            Contribution.amount.isnot(None)
        ).scalar() or 0

        # Open opportunities (active stages)
        open_opportunities = db.query(func.count(Opportunity.opportunity_id)).filter(
            Opportunity.stage.in_(['Qualification', 'Cultivation', 'Proposal', 'Negotiation'])
        ).scalar()

        # Weighted pipeline value
        weighted_pipeline = db.query(func.sum(Opportunity.expected_amount)).filter(
            Opportunity.stage.in_(['Qualification', 'Cultivation', 'Proposal', 'Negotiation']),
            Opportunity.expected_amount.isnot(None)
        ).scalar() or 0

        return {
            "total_constituents": total_constituents,
            "active_constituents": active_constituents,
            "total_contributions": float(total_contributions),
            "average_contribution": float(average_contribution),
            "recent_interactions": recent_interactions,
            "contributions_this_year": float(contributions_this_year),
            "contributions_this_month": float(contributions_this_month),
            "open_opportunities": open_opportunities,
            "weighted_pipeline": float(weighted_pipeline)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/api/v1/dashboard/recent-activity")
def get_recent_activity():
    """Get recent activity feed"""
    db = next(get_db())

    try:
        # Get recent contributions (last 10)
        contributions = db.query(Contribution).join(Constituent).order_by(
            Contribution.contribution_date.desc()
        ).limit(10).all()

        recent_contributions = [
            {
                "id": contrib.contribution_id,
                "amount": float(contrib.amount or 0),
                "date": contrib.contribution_date.isoformat(),
                "constituent_name": contrib.constituent.full_name,
                "constituent_id": contrib.constituent_id,
                "type": contrib.contribution_type,
                "campaign_id": contrib.campaign_id
            }
            for contrib in contributions
        ]

        # Get recent interactions (last 10)
        interactions = db.query(Interaction).join(Constituent).order_by(
            Interaction.interaction_date.desc()
        ).limit(10).all()

        recent_interactions = [
            {
                "id": interaction.interaction_id,
                "subject": interaction.subject or interaction.interaction_type,
                "type": interaction.interaction_type,
                "date": interaction.interaction_date.isoformat(),
                "constituent_name": interaction.constituent.full_name,
                "constituent_id": interaction.constituent_id,
                "staff_member": interaction.staff_member
            }
            for interaction in interactions
        ]

        return {
            "recent_contributions": recent_contributions,
            "recent_interactions": recent_interactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/api/v1/constituents")
def get_constituents(skip: int = 0, limit: int = 100):
    """Get all constituents with pagination"""
    db = next(get_db())

    try:
        constituents = db.query(Constituent).offset(skip).limit(limit).all()
        total = db.query(func.count(Constituent.constituent_id)).scalar()

        return {
            "total": total,
            "constituents": [
                {
                    "constituent_id": c.constituent_id,
                    "full_name": c.full_name,
                    "email": c.email,
                    "phone": c.phone,
                    "constituent_type": c.constituent_type,
                    "total_lifetime_giving": float(c.total_lifetime_giving or 0)
                }
                for c in constituents
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/api/v1/constituents/{constituent_id}")
def get_constituent(constituent_id: int):
    """Get a specific constituent with related data"""
    db = next(get_db())

    try:
        constituent = db.query(Constituent).filter_by(
            constituent_id=constituent_id
        ).first()

        if not constituent:
            raise HTTPException(status_code=404, detail="Constituent not found")

        return {
            "constituent_id": constituent.constituent_id,
            "first_name": constituent.first_name,
            "last_name": constituent.last_name,
            "full_name": constituent.full_name,
            "email": constituent.email,
            "phone": constituent.phone,
            "address": constituent.address,
            "city": constituent.city,
            "state": constituent.state,
            "zip_code": constituent.zip_code,
            "constituent_type": constituent.constituent_type,
            "total_lifetime_giving": float(constituent.total_lifetime_giving or 0),
            "created_date": constituent.created_date.isoformat(),
            "contributions_count": len(constituent.contributions),
            "interactions_count": len(constituent.interactions),
            "opportunities_count": len(constituent.opportunities)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
