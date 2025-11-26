"""
Seed sample data for testing the API
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from models import (
    create_database_engine, get_session,
    Constituent, Contribution, Interaction, Opportunity
)

def seed_sample_data():
    """Add sample data to the database"""

    engine = create_database_engine("sqlite:///nonprofit_crm.db")
    session = get_session(engine)

    try:
        # Create sample constituents
        constituents = [
            Constituent(
                first_name="John",
                last_name="Smith",
                email="john.smith@example.com",
                phone="555-0101",
                constituent_type="Donor",
                created_date=date(2023, 1, 1),
                total_lifetime_giving=Decimal("15000.00")
            ),
            Constituent(
                first_name="Sarah",
                last_name="Johnson",
                email="sarah.j@example.com",
                phone="555-0102",
                constituent_type="Volunteer",
                created_date=date(2023, 1, 15),
                total_lifetime_giving=Decimal("2500.00")
            ),
            Constituent(
                first_name="Michael",
                last_name="Brown",
                email="m.brown@example.com",
                phone="555-0103",
                constituent_type="Board Member",
                created_date=date(2023, 2, 1),
                total_lifetime_giving=Decimal("50000.00")
            ),
            Constituent(
                first_name="Emily",
                last_name="Davis",
                email="emily.davis@example.com",
                phone="555-0104",
                constituent_type="Major Donor",
                created_date=date(2023, 2, 15),
                total_lifetime_giving=Decimal("100000.00")
            ),
            Constituent(
                first_name="Robert",
                last_name="Wilson",
                email="r.wilson@example.com",
                phone="555-0105",
                constituent_type="Donor",
                created_date=date(2023, 3, 1),
                total_lifetime_giving=Decimal("5000.00")
            ),
        ]

        session.add_all(constituents)
        session.flush()  # Flush to get IDs

        # Create sample contributions
        contributions = [
            Contribution(
                constituent_id=constituents[0].constituent_id,
                contribution_date=date.today() - timedelta(days=5),
                amount=Decimal("1000.00"),
                contribution_type="Cash",
                campaign_id="CAMP001",
                payment_method="Credit Card",
                acknowledgment_sent="Yes"
            ),
            Contribution(
                constituent_id=constituents[0].constituent_id,
                contribution_date=date.today() - timedelta(days=30),
                amount=Decimal("500.00"),
                contribution_type="Cash",
                campaign_id="CAMP001",
                payment_method="Check",
                acknowledgment_sent="Yes"
            ),
            Contribution(
                constituent_id=constituents[2].constituent_id,
                contribution_date=date.today() - timedelta(days=2),
                amount=Decimal("5000.00"),
                contribution_type="Cash",
                campaign_id="CAMP002",
                payment_method="Wire Transfer",
                acknowledgment_sent="No"
            ),
            Contribution(
                constituent_id=constituents[3].constituent_id,
                contribution_date=date.today() - timedelta(days=1),
                amount=Decimal("25000.00"),
                contribution_type="Stock",
                campaign_id="CAMP003",
                payment_method="Stock Transfer",
                acknowledgment_sent="No"
            ),
        ]

        session.add_all(contributions)

        # Create sample interactions
        interactions = [
            Interaction(
                constituent_id=constituents[0].constituent_id,
                interaction_date=date.today() - timedelta(days=3),
                interaction_type="Phone Call",
                subject="Thank you call for recent donation",
                staff_member="Jane Fundraiser",
                follow_up_required="No"
            ),
            Interaction(
                constituent_id=constituents[2].constituent_id,
                interaction_date=date.today() - timedelta(days=1),
                interaction_type="Meeting",
                subject="Board meeting attendance",
                staff_member="Executive Director",
                follow_up_required="Yes"
            ),
            Interaction(
                constituent_id=constituents[3].constituent_id,
                interaction_date=date.today(),
                interaction_type="Email",
                subject="Major gift proposal follow-up",
                staff_member="Development Director",
                follow_up_required="Yes"
            ),
        ]

        session.add_all(interactions)

        # Create sample opportunities
        opportunities = [
            Opportunity(
                constituent_id=constituents[3].constituent_id,
                opportunity_name="Capital Campaign Leadership Gift",
                stage="Negotiation",
                expected_amount=Decimal("50000.00"),
                expected_close_date=date.today() + timedelta(days=30),
                probability=75,
                created_date=date.today() - timedelta(days=60),
                assigned_to="Development Director"
            ),
            Opportunity(
                constituent_id=constituents[0].constituent_id,
                opportunity_name="Annual Fund Upgrade",
                stage="Proposal",
                expected_amount=Decimal("10000.00"),
                expected_close_date=date.today() + timedelta(days=45),
                probability=50,
                created_date=date.today() - timedelta(days=30),
                assigned_to="Jane Fundraiser"
            ),
        ]

        session.add_all(opportunities)

        # Commit all changes
        session.commit()

        print("✅ Sample data seeded successfully!")
        print(f"   - {len(constituents)} constituents")
        print(f"   - {len(contributions)} contributions")
        print(f"   - {len(interactions)} interactions")
        print(f"   - {len(opportunities)} opportunities")

    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_sample_data()
