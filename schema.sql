-- Nonprofit CRM Database Schema
-- PostgreSQL/SQLite compatible schema

-- Drop existing tables if they exist (in reverse dependency order)
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS contributions CASCADE;
DROP TABLE IF EXISTS interactions CASCADE;
DROP TABLE IF EXISTS opportunities CASCADE;
DROP TABLE IF EXISTS constituents CASCADE;

-- =============================================================================
-- CONSTITUENTS TABLE
-- =============================================================================
CREATE TABLE constituents (
    constituent_id INTEGER PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    constituent_type VARCHAR(50) NOT NULL,
    created_date DATE NOT NULL,
    total_lifetime_giving DECIMAL(12, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT chk_constituent_type CHECK (
        constituent_type IN ('Donor', 'Volunteer', 'Board Member', 'Major Donor', 'Staff', 'Other')
    ),
    CONSTRAINT chk_email_format CHECK (
        email IS NULL OR email LIKE '%@%'
    )
);

-- Indexes for constituents
CREATE INDEX idx_constituents_email ON constituents(email);
CREATE INDEX idx_constituents_type ON constituents(constituent_type);
CREATE INDEX idx_constituents_created_date ON constituents(created_date);
CREATE INDEX idx_constituents_name ON constituents(last_name, first_name);

-- =============================================================================
-- CONTRIBUTIONS TABLE
-- =============================================================================
CREATE TABLE contributions (
    contribution_id INTEGER PRIMARY KEY,
    constituent_id INTEGER NOT NULL,
    contribution_date DATE NOT NULL,
    amount DECIMAL(12, 2),
    contribution_type VARCHAR(50) NOT NULL,
    campaign_id VARCHAR(50),
    payment_method VARCHAR(50),
    acknowledgment_sent VARCHAR(3) DEFAULT 'No',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key relationships
    CONSTRAINT fk_contributions_constituent
        FOREIGN KEY (constituent_id)
        REFERENCES constituents(constituent_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Constraints
    CONSTRAINT chk_contribution_type CHECK (
        contribution_type IN ('Cash', 'In-Kind', 'Stock', 'Pledge', 'Planned Gift', 'Other')
    ),
    CONSTRAINT chk_amount_positive CHECK (
        amount IS NULL OR amount >= 0
    ),
    CONSTRAINT chk_acknowledgment CHECK (
        acknowledgment_sent IN ('Yes', 'No', '')
    )
);

-- Indexes for contributions
CREATE INDEX idx_contributions_constituent ON contributions(constituent_id);
CREATE INDEX idx_contributions_date ON contributions(contribution_date);
CREATE INDEX idx_contributions_campaign ON contributions(campaign_id);
CREATE INDEX idx_contributions_type ON contributions(contribution_type);
CREATE INDEX idx_contributions_amount ON contributions(amount DESC);

-- =============================================================================
-- INTERACTIONS TABLE
-- =============================================================================
CREATE TABLE interactions (
    interaction_id INTEGER PRIMARY KEY,
    constituent_id INTEGER NOT NULL,
    interaction_date DATE NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    subject VARCHAR(255),
    notes TEXT,
    staff_member VARCHAR(100),
    follow_up_required VARCHAR(3) DEFAULT 'No',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key relationships
    CONSTRAINT fk_interactions_constituent
        FOREIGN KEY (constituent_id)
        REFERENCES constituents(constituent_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Constraints
    CONSTRAINT chk_interaction_type CHECK (
        interaction_type IN ('Phone Call', 'Email', 'Meeting', 'Event', 'Letter', 'Text', 'Other')
    ),
    CONSTRAINT chk_follow_up CHECK (
        follow_up_required IN ('Yes', 'No', '')
    )
);

-- Indexes for interactions
CREATE INDEX idx_interactions_constituent ON interactions(constituent_id);
CREATE INDEX idx_interactions_date ON interactions(interaction_date DESC);
CREATE INDEX idx_interactions_type ON interactions(interaction_type);
CREATE INDEX idx_interactions_staff ON interactions(staff_member);
CREATE INDEX idx_interactions_follow_up ON interactions(follow_up_required)
    WHERE follow_up_required = 'Yes';

-- =============================================================================
-- OPPORTUNITIES TABLE
-- =============================================================================
CREATE TABLE opportunities (
    opportunity_id INTEGER PRIMARY KEY,
    constituent_id INTEGER NOT NULL,
    opportunity_name VARCHAR(255) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    expected_amount DECIMAL(12, 2),
    expected_close_date DATE,
    probability INTEGER,
    created_date DATE NOT NULL,
    assigned_to VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key relationships
    CONSTRAINT fk_opportunities_constituent
        FOREIGN KEY (constituent_id)
        REFERENCES constituents(constituent_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Constraints
    CONSTRAINT chk_opportunity_stage CHECK (
        stage IN ('Qualification', 'Cultivation', 'Proposal', 'Negotiation', 'Committed', 'Closed Won', 'Closed Lost')
    ),
    CONSTRAINT chk_probability_range CHECK (
        probability IS NULL OR (probability >= 0 AND probability <= 100)
    ),
    CONSTRAINT chk_expected_amount_positive CHECK (
        expected_amount IS NULL OR expected_amount >= 0
    )
);

-- Indexes for opportunities
CREATE INDEX idx_opportunities_constituent ON opportunities(constituent_id);
CREATE INDEX idx_opportunities_stage ON opportunities(stage);
CREATE INDEX idx_opportunities_close_date ON opportunities(expected_close_date);
CREATE INDEX idx_opportunities_assigned ON opportunities(assigned_to);
CREATE INDEX idx_opportunities_amount ON opportunities(expected_amount DESC);

-- =============================================================================
-- TRANSACTIONS TABLE
-- =============================================================================
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY,
    contribution_id INTEGER NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    payment_processor VARCHAR(50),
    processor_fee DECIMAL(10, 2) DEFAULT 0.00,
    net_amount DECIMAL(12, 2),
    reconciliation_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Foreign key relationships
    CONSTRAINT fk_transactions_contribution
        FOREIGN KEY (contribution_id)
        REFERENCES contributions(contribution_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    -- Constraints
    CONSTRAINT chk_transaction_type CHECK (
        transaction_type IN ('Payment', 'Refund', 'Pledge', 'In-Kind', 'Adjustment', 'Other')
    ),
    CONSTRAINT chk_transaction_status CHECK (
        status IN ('Pending', 'Processing', 'Completed', 'Failed', 'Cancelled', 'Refunded')
    ),
    CONSTRAINT chk_transaction_amount_positive CHECK (
        amount >= 0
    ),
    CONSTRAINT chk_processor_fee_positive CHECK (
        processor_fee IS NULL OR processor_fee >= 0
    )
);

-- Indexes for transactions
CREATE INDEX idx_transactions_contribution ON transactions(contribution_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date DESC);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_processor ON transactions(payment_processor);
CREATE INDEX idx_transactions_reconciliation ON transactions(reconciliation_date);

-- =============================================================================
-- VIEWS FOR REPORTING
-- =============================================================================

-- View: Constituent Summary with aggregated giving
CREATE VIEW vw_constituent_summary AS
SELECT
    c.constituent_id,
    c.first_name,
    c.last_name,
    c.email,
    c.constituent_type,
    COUNT(DISTINCT contrib.contribution_id) as total_contributions,
    COALESCE(SUM(contrib.amount), 0) as total_given,
    MAX(contrib.contribution_date) as last_gift_date,
    COUNT(DISTINCT i.interaction_id) as total_interactions,
    MAX(i.interaction_date) as last_interaction_date
FROM constituents c
LEFT JOIN contributions contrib ON c.constituent_id = contrib.constituent_id
LEFT JOIN interactions i ON c.constituent_id = i.constituent_id
GROUP BY c.constituent_id, c.first_name, c.last_name, c.email, c.constituent_type;

-- View: Active opportunities pipeline
CREATE VIEW vw_active_opportunities AS
SELECT
    o.opportunity_id,
    o.opportunity_name,
    o.stage,
    o.expected_amount,
    o.expected_close_date,
    o.probability,
    o.assigned_to,
    c.first_name || ' ' || c.last_name as constituent_name,
    c.email as constituent_email,
    ROUND(o.expected_amount * o.probability / 100.0, 2) as weighted_amount
FROM opportunities o
JOIN constituents c ON o.constituent_id = c.constituent_id
WHERE o.stage NOT IN ('Closed Won', 'Closed Lost')
ORDER BY o.expected_close_date;

-- View: Transaction reconciliation report
CREATE VIEW vw_transaction_reconciliation AS
SELECT
    t.transaction_id,
    t.transaction_date,
    t.reconciliation_date,
    CASE
        WHEN t.reconciliation_date IS NULL THEN 'Unreconciled'
        ELSE 'Reconciled'
    END as reconciliation_status,
    c.first_name || ' ' || c.last_name as constituent_name,
    contrib.campaign_id,
    t.amount,
    t.processor_fee,
    t.net_amount,
    t.payment_processor,
    t.status
FROM transactions t
JOIN contributions contrib ON t.contribution_id = contrib.contribution_id
JOIN constituents c ON contrib.constituent_id = c.constituent_id;

-- =============================================================================
-- ANALYTICS FUNCTIONS
-- =============================================================================

-- Comment: The following are example analytical queries that can be useful

-- Query 1: Top donors by total giving
-- SELECT constituent_id, first_name, last_name, total_lifetime_giving
-- FROM constituents
-- ORDER BY total_lifetime_giving DESC NULLS LAST
-- LIMIT 10;

-- Query 2: Campaign performance
-- SELECT
--     campaign_id,
--     COUNT(*) as contribution_count,
--     SUM(amount) as total_raised,
--     AVG(amount) as average_gift
-- FROM contributions
-- WHERE campaign_id IS NOT NULL
-- GROUP BY campaign_id
-- ORDER BY total_raised DESC;

-- Query 3: Interactions requiring follow-up
-- SELECT
--     i.interaction_id,
--     c.first_name || ' ' || c.last_name as constituent_name,
--     i.interaction_date,
--     i.subject,
--     i.staff_member
-- FROM interactions i
-- JOIN constituents c ON i.constituent_id = c.constituent_id
-- WHERE i.follow_up_required = 'Yes'
-- ORDER BY i.interaction_date;
