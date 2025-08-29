# Veteran Referral Outcomes Portal

A secure, privacy-preserving system that bridges the data gap between the Veterans Crisis Line (VCL/988) and Veteran Service Organizations (VSOs/VSAs) by enabling standardized outcome tracking without sharing personally identifiable information (PII).

## Project Overview

**Problem:** VA cannot currently track what happens to veterans after they're referred to community VSAs, creating accountability and resource allocation gaps.

**Solution:** Tokenized referral system where VA mints referral tokens, VSAs update outcomes via a secure portal, and aggregate reporting provides transparency without PII exposure.

**Key Benefits:**
- Zero PII in shared systems
- Standardized outcome tracking
- Aggregate reporting for VA stakeholders
- Improved veteran outcomes through better coordination

## CSV Referral Intake Structure

The system accepts referral data via CSV files from VA systems (before Medora API integration). All fields are structured to prevent PII leakage.

### File Format
- **Naming Convention:** `referrals_YYYYMMDD_HHMMSS.csv`
- **Encoding:** UTF-8
- **Delimiter:** Comma (,)
- **Header Row:** Required

### Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `referral_token` | UUID/HMAC | Unique referral identifier minted by VA | `abc123-def456-ghi789` |
| `issued_at` | ISO 8601 | Timestamp when referral was created | `2024-01-15T10:30:00Z` |
| `vsa_id` | String | Unique identifier for receiving VSA | `VSA001` |
| `program_code` | Enum | Standardized program type | `CRISIS_INTERVENTION` |
| `episode_id` | String | VA's internal episode identifier | `EP12345` |
| `referral_type` | Enum | How the referral originated | `CRISIS_HOTLINE` |
| `priority_level` | Enum | Referral urgency level | `HIGH` |

### Optional Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `crisis_type` | Enum | Specific crisis category | `SUICIDE_RISK` |
| `urgency_indicator` | Enum | Contact timeline requirement | `IMMEDIATE` |
| `expected_contact_date` | Date | When VSA should attempt contact | `2024-01-16` |
| `va_facility_code` | String | VA facility identifier | `VA001` |

### Accepted Values

#### `program_code`
- `CRISIS_INTERVENTION` - Immediate crisis response
- `MENTAL_HEALTH` - Ongoing mental health support
- `HOUSING_ASSISTANCE` - Homelessness and housing support
- `SUBSTANCE_ABUSE` - Addiction treatment and recovery
- `EMPLOYMENT` - Job training and placement
- `BENEFITS_NAVIGATION` - VA benefits assistance
- `LEGAL_AID` - Legal representation and advocacy
- `OTHER` - Additional support categories

#### `referral_type`
- `CRISIS_HOTLINE` - Referral from 988 crisis line
- `CLINICAL_REFERRAL` - Referral from VA clinician
- `SELF_REFERRAL` - Veteran self-referral
- `COMMUNITY_REFERRAL` - Referral from community partner
- `OTHER` - Additional referral sources

#### `priority_level`
- `HIGH` - Requires immediate attention (< 1 hour)
- `MEDIUM` - Standard priority (within 24 hours)
- `LOW` - Lower priority (within 72 hours)

#### `crisis_type`
- `SUICIDE_RISK` - Active suicide ideation or attempt
- `HOMELESSNESS` - Housing insecurity or homelessness
- `SUBSTANCE_ABUSE` - Active addiction or overdose risk
- `DEPRESSION` - Major depressive episode
- `ANXIETY` - Severe anxiety or panic disorder
- `PTSD` - Post-traumatic stress disorder
- `DOMESTIC_VIOLENCE` - Domestic abuse or violence
- `FINANCIAL_CRISIS` - Financial hardship or eviction
- `OTHER` - Additional crisis categories

#### `urgency_indicator`
- `IMMEDIATE` - Contact required within 1 hour
- `WITHIN_24H` - Contact required within 24 hours
- `WITHIN_72H` - Contact required within 72 hours
- `STANDARD` - Contact required within 1 week

### Sample CSV

See `data/sample_referrals.csv` for a complete example with realistic data.

## Validation Rules

- **No PII allowed** - System rejects files containing names, SSNs, phone numbers, addresses
- **Unique tokens** - Each `referral_token` must be unique
- **Valid VSA IDs** - `vsa_id` must match registered VSAs in the system
- **Enum validation** - All enum fields must contain accepted values
- **Timestamp format** - All timestamps must be valid ISO 8601 format
- **Required fields** - All required fields must be present and non-empty

## Intake Process

1. VA staff exports CSV from their system (Medora/EHR)
2. CSV uploaded via secure portal or API endpoint
3. System validates format, content, and PII-free requirements
4. Valid referrals loaded into database
5. Invalid referrals logged with detailed error reporting
6. Confirmation report sent back to VA with processing results

## Security Features

- **Zero PII storage** - No personally identifiable information in shared systems
- **Structured data only** - No free-text fields that could contain PII
- **Token-based tracking** - Referrals tracked by UUIDs, not veteran information
- **Encrypted storage** - All data encrypted at rest and in transit
- **Audit logging** - Complete audit trail of all data processing

## Next Steps

1. Build MVP with synthetic data and 2-3 VSA pilot partners
2. Prepare documentation for iEX 2025
3. Engage VA primes for pilot sponsorship
4. Pursue grant + SaaS hybrid funding model

## Tech Stack

- **Backend:** FastAPI (Python) with Pydantic schemas
- **Frontend:** React + Next.js + Tailwind CSS
- **Database:** PostgreSQL with Row-Level Security
- **Infrastructure:** AWS (Terraform IaC), ECS Fargate
- **Security:** SAML/OIDC, mTLS, OAuth2, KMS encryption

## Getting Started

See individual component directories for setup instructions:
- `backend/` - FastAPI backend setup
- `frontend/` - React portal setup
- `database/` - Database schema and migrations
- `infrastructure/` - AWS deployment configuration
