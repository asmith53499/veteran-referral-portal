-- Veteran Referral Portal Database Schema
-- This schema implements the zero-PII architecture with Row-Level Security (RLS)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create custom types for enums
CREATE TYPE program_code_enum AS ENUM (
    'CRISIS_INTERVENTION',
    'MENTAL_HEALTH',
    'HOUSING_ASSISTANCE',
    'SUBSTANCE_ABUSE',
    'EMPLOYMENT',
    'BENEFITS_NAVIGATION',
    'LEGAL_AID',
    'OTHER'
);

CREATE TYPE referral_type_enum AS ENUM (
    'CRISIS_HOTLINE',
    'CLINICAL_REFERRAL',
    'SELF_REFERRAL',
    'COMMUNITY_REFERRAL',
    'OTHER'
);

CREATE TYPE priority_level_enum AS ENUM (
    'HIGH',
    'MEDIUM',
    'LOW'
);

CREATE TYPE crisis_type_enum AS ENUM (
    'SUICIDE_RISK',
    'HOMELESSNESS',
    'SUBSTANCE_ABUSE',
    'DEPRESSION',
    'ANXIETY',
    'PTSD',
    'DOMESTIC_VIOLENCE',
    'FINANCIAL_CRISIS',
    'OTHER'
);

CREATE TYPE urgency_indicator_enum AS ENUM (
    'IMMEDIATE',
    'WITHIN_24H',
    'WITHIN_72H',
    'STANDARD'
);

CREATE TYPE outcome_status_enum AS ENUM (
    'RECEIVED',
    'ENGAGED',
    'WAITLIST',
    'COMPLETED',
    'UNREACHABLE',
    'DECLINED'
);

CREATE TYPE reason_code_enum AS ENUM (
    'NO_SHOW',
    'CONTACT_FAILED',
    'CAPACITY',
    'INELIGIBLE',
    'WITHDREW',
    'OTHER_NONPII'
);

-- Create organizations table (VSAs)
CREATE TABLE organizations (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    organization_type VARCHAR(100) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    county VARCHAR(100),
    service_areas TEXT[], -- Array of counties/states served
    programs program_code_enum[], -- Array of programs offered
    capacity_daily INTEGER,
    capacity_monthly INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Validation constraints
    CONSTRAINT valid_phone CHECK (contact_phone ~ '^\+?[1-9]\d{1,14}$'),
    CONSTRAINT valid_email CHECK (contact_email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT valid_state CHECK (state ~ '^[A-Z]{2}$'),
    CONSTRAINT valid_zip CHECK (zip_code ~ '^\d{5}(-\d{4})?$')
);

-- Create referrals table (main referral data)
CREATE TABLE referrals (
    referral_token UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    issued_at TIMESTAMPTZ NOT NULL,
    vsa_id VARCHAR(50) NOT NULL REFERENCES organizations(id),
    program_code program_code_enum NOT NULL,
    episode_id VARCHAR(100), -- VA's internal episode identifier
    referral_type referral_type_enum NOT NULL,
    priority_level priority_level_enum NOT NULL,
    crisis_type crisis_type_enum,
    urgency_indicator urgency_indicator_enum,
    expected_contact_date DATE,
    va_facility_code VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Validation constraints
    CONSTRAINT valid_expected_date CHECK (expected_contact_date >= CURRENT_DATE),
    CONSTRAINT valid_issued_date CHECK (issued_at <= NOW())
);

-- Create outcomes table (VSA outcome updates)
CREATE TABLE outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    referral_token UUID NOT NULL REFERENCES referrals(referral_token) ON DELETE CASCADE,
    vsa_id VARCHAR(50) NOT NULL REFERENCES organizations(id),
    status outcome_status_enum NOT NULL,
    first_contact_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    reason_code reason_code_enum,
    notes TEXT, -- Limited to non-PII context
    updated_by VARCHAR(100) NOT NULL, -- VSA staff identifier
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Validation constraints
    CONSTRAINT valid_contact_dates CHECK (
        first_contact_at IS NULL OR 
        closed_at IS NULL OR 
        first_contact_at <= closed_at
    ),
    CONSTRAINT valid_status_transitions CHECK (
        (status = 'RECEIVED' AND first_contact_at IS NULL) OR
        (status IN ('ENGAGED', 'WAITLIST', 'COMPLETED', 'UNREACHABLE', 'DECLINED') AND first_contact_at IS NOT NULL)
    )
);

-- Create audit log table (WORM - Write Once, Read Many)
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(50) NOT NULL,
    record_id VARCHAR(100) NOT NULL,
    action VARCHAR(20) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT,
    
    -- Validation constraints
    CONSTRAINT valid_action CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    CONSTRAINT valid_table CHECK (table_name IN ('referrals', 'outcomes', 'organizations'))
);

-- Create indexes for performance
CREATE INDEX idx_referrals_vsa_id ON referrals(vsa_id);
CREATE INDEX idx_referrals_program_code ON referrals(program_code);
CREATE INDEX idx_referrals_issued_at ON referrals(issued_at);
CREATE INDEX idx_referrals_priority_level ON referrals(priority_level);
CREATE INDEX idx_referrals_crisis_type ON referrals(crisis_type);

CREATE INDEX idx_outcomes_referral_token ON outcomes(referral_token);
CREATE INDEX idx_outcomes_vsa_id ON outcomes(vsa_id);
CREATE INDEX idx_outcomes_status ON outcomes(status);
CREATE INDEX idx_outcomes_updated_at ON outcomes(updated_at);

CREATE INDEX idx_audit_log_table_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at);
CREATE INDEX idx_audit_log_action ON audit_log(action);

-- Create composite indexes for common queries
CREATE INDEX idx_referrals_vsa_date ON referrals(vsa_id, issued_at);
CREATE INDEX idx_outcomes_vsa_status ON outcomes(vsa_id, status);

-- Enable Row Level Security
ALTER TABLE referrals ENABLE ROW LEVEL SECURITY;
ALTER TABLE outcomes ENABLE ROW LEVEL SECURITY;
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;

-- RLS Policies for referrals table
CREATE POLICY referrals_vsa_isolation ON referrals
    FOR ALL USING (vsa_id = current_setting('app.vsa_id', true));

CREATE POLICY referrals_va_access ON referrals
    FOR ALL USING (current_setting('app.user_role', true) = 'va_admin');

-- RLS Policies for outcomes table
CREATE POLICY outcomes_vsa_isolation ON outcomes
    FOR ALL USING (vsa_id = current_setting('app.vsa_id', true));

CREATE POLICY outcomes_va_access ON outcomes
    FOR ALL USING (current_setting('app.user_role', true) = 'va_admin');

-- RLS Policies for organizations table
CREATE POLICY organizations_vsa_own ON organizations
    FOR ALL USING (id = current_setting('app.vsa_id', true));

CREATE POLICY organizations_va_access ON organizations
    FOR ALL USING (current_setting('app.user_role', true) = 'va_admin');

-- Create functions for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, record_id, action, new_values, changed_by)
        VALUES (TG_TABLE_NAME, NEW.referral_token::VARCHAR, 'INSERT', to_jsonb(NEW), current_setting('app.user_id', true));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, new_values, changed_by)
        VALUES (TG_TABLE_NAME, NEW.referral_token::VARCHAR, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), current_setting('app.user_id', true));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, record_id, action, old_values, changed_by)
        VALUES (TG_TABLE_NAME, OLD.referral_token::VARCHAR, 'DELETE', to_jsonb(OLD), current_setting('app.user_id', true));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create audit triggers
CREATE TRIGGER referrals_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON referrals
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER outcomes_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON outcomes
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Create function to set application context
CREATE OR REPLACE FUNCTION set_app_context(
    p_vsa_id VARCHAR(50),
    p_user_id VARCHAR(100),
    p_user_role VARCHAR(50)
)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.vsa_id', p_vsa_id, false);
    PERFORM set_config('app.user_id', p_user_id, false);
    PERFORM set_config('app.user_role', p_user_role, false);
END;
$$ LANGUAGE plpgsql;

-- Create views for common queries
CREATE VIEW referral_summary AS
SELECT 
    r.referral_token,
    r.issued_at,
    r.vsa_id,
    o.name as vsa_name,
    r.program_code,
    r.referral_type,
    r.priority_level,
    r.crisis_type,
    r.urgency_indicator,
    r.expected_contact_date,
    r.va_facility_code,
    COALESCE(out.status, 'PENDING') as current_status,
    out.first_contact_at,
    out.closed_at,
    out.reason_code,
    r.created_at,
    r.updated_at
FROM referrals r
LEFT JOIN organizations o ON r.vsa_id = o.id
LEFT JOIN LATERAL (
    SELECT DISTINCT ON (referral_token) *
    FROM outcomes
    WHERE referral_token = r.referral_token
    ORDER BY referral_token, updated_at DESC
) out ON true;

-- Create materialized view for reporting (refresh as needed)
CREATE MATERIALIZED VIEW referral_analytics AS
SELECT 
    vsa_id,
    program_code,
    referral_type,
    priority_level,
    crisis_type,
    urgency_indicator,
    DATE_TRUNC('month', issued_at) as month,
    COUNT(*) as total_referrals,
    COUNT(CASE WHEN out.status = 'ENGAGED' THEN 1 END) as engaged_count,
    COUNT(CASE WHEN out.status = 'COMPLETED' THEN 1 END) as completed_count,
    COUNT(CASE WHEN out.status = 'UNREACHABLE' THEN 1 END) as unreachable_count,
    AVG(EXTRACT(EPOCH FROM (out.first_contact_at - r.issued_at))/3600) as avg_hours_to_contact
FROM referrals r
LEFT JOIN LATERAL (
    SELECT DISTINCT ON (referral_token) *
    FROM outcomes
    WHERE referral_token = r.referral_token
    ORDER BY referral_token, updated_at DESC
) out ON true
GROUP BY vsa_id, program_code, referral_type, priority_level, crisis_type, urgency_indicator, DATE_TRUNC('month', issued_at);

-- Create index on materialized view
CREATE INDEX idx_referral_analytics_lookup ON referral_analytics(vsa_id, month, program_code);

-- Grant permissions (adjust based on your user setup)
-- GRANT USAGE ON SCHEMA public TO vrp_app_user;
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO vrp_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO vrp_app_user;

-- Insert sample VSA organizations
INSERT INTO organizations (id, name, organization_type, contact_email, contact_phone, address_line1, city, state, zip_code, county, service_areas, programs, capacity_daily, capacity_monthly) VALUES
('VSA001', 'Veterans Crisis Support Center', 'NONPROFIT', 'contact@vetscrisis.org', '+15551234567', '123 Veterans Way', 'Atlanta', 'GA', '30301', 'Fulton', ARRAY['Fulton', 'DeKalb', 'Cobb'], ARRAY['CRISIS_INTERVENTION', 'MENTAL_HEALTH'], 50, 1000),
('VSA002', 'Georgia Veterans Mental Health Alliance', 'NONPROFIT', 'info@gavetsmentalhealth.org', '+15551234568', '456 Support Street', 'Atlanta', 'GA', '30302', 'Fulton', ARRAY['Fulton', 'DeKalb'], ARRAY['MENTAL_HEALTH', 'SUBSTANCE_ABUSE'], 30, 600),
('VSA003', 'Atlanta Veterans Housing Initiative', 'NONPROFIT', 'help@atlantavetshousing.org', '+15551234569', '789 Housing Avenue', 'Atlanta', 'GA', '30303', 'Fulton', ARRAY['Fulton', 'Clayton'], ARRAY['HOUSING_ASSISTANCE', 'BENEFITS_NAVIGATION'], 20, 400),
('VSA004', 'Georgia Veterans Employment Network', 'NONPROFIT', 'jobs@gavetsjobs.org', '+15551234570', '321 Career Drive', 'Atlanta', 'GA', '30304', 'Fulton', ARRAY['Fulton', 'DeKalb', 'Cobb'], ARRAY['EMPLOYMENT', 'BENEFITS_NAVIGATION'], 25, 500);

-- Create function to refresh materialized view
CREATE OR REPLACE FUNCTION refresh_referral_analytics()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW referral_analytics;
END;
$$ LANGUAGE plpgsql;

-- Create function to get referral statistics
CREATE OR REPLACE FUNCTION get_referral_stats(
    p_vsa_id VARCHAR(50) DEFAULT NULL,
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL
)
RETURNS TABLE (
    total_referrals BIGINT,
    engaged_count BIGINT,
    completed_count BIGINT,
    unreachable_count BIGINT,
    engagement_rate NUMERIC,
    completion_rate NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_referrals,
        COUNT(CASE WHEN out.status = 'ENGAGED' THEN 1 END) as engaged_count,
        COUNT(CASE WHEN out.status = 'COMPLETED' THEN 1 END) as completed_count,
        COUNT(CASE WHEN out.status = 'UNREACHABLE' THEN 1 END) as unreachable_count,
        ROUND(
            COUNT(CASE WHEN out.status = 'ENGAGED' THEN 1 END)::NUMERIC / 
            NULLIF(COUNT(*), 0) * 100, 2
        ) as engagement_rate,
        ROUND(
            COUNT(CASE WHEN out.status = 'COMPLETED' THEN 1 END)::NUMERIC / 
            NULLIF(COUNT(*), 0) * 100, 2
        ) as completion_rate
    FROM referrals r
    LEFT JOIN LATERAL (
        SELECT DISTINCT ON (referral_token) *
        FROM outcomes
        WHERE referral_token = r.referral_token
        ORDER BY referral_token, updated_at DESC
    ) out ON true
    WHERE (p_vsa_id IS NULL OR r.vsa_id = p_vsa_id)
      AND (p_start_date IS NULL OR r.issued_at >= p_start_date)
      AND (p_end_date IS NULL OR r.issued_at <= p_end_date);
END;
$$ LANGUAGE plpgsql;
