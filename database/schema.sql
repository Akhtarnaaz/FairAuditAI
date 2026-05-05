-- ══════════════════════════════════════════════════════════════
-- AI Bias & Fairness Auditor — Database Schema
-- PostgreSQL / Supabase compatible
-- ══════════════════════════════════════════════════════════════

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Users ─────────────────────────────────────────────────────
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);

-- ── Models ────────────────────────────────────────────────────
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_by_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(20) NOT NULL CHECK (model_type IN ('classification', 'regression', 'generation')),
    model_filepath VARCHAR(500),
    api_endpoint VARCHAR(500),
    model_version VARCHAR(50) DEFAULT '1.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_models_user ON models(created_by_user_id);

-- ── Datasets ──────────────────────────────────────────────────
CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    uploaded_by_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    dataset_name VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    num_rows INTEGER,
    num_columns INTEGER,
    schema_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_datasets_user ON datasets(uploaded_by_user_id);

-- ── Audit Runs ────────────────────────────────────────────────
CREATE TABLE audit_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_id UUID NOT NULL REFERENCES models(id) ON DELETE CASCADE,
    dataset_id UUID NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
    counterfactual_config JSONB,
    variation_strategy VARCHAR(20) DEFAULT 'systematic',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    num_test_cases INTEGER DEFAULT 0,
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_runs_user ON audit_runs(admin_user_id);
CREATE INDEX idx_audit_runs_status ON audit_runs(status);

-- ── Fairness Scores ───────────────────────────────────────────
CREATE TABLE fairness_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_run_id UUID NOT NULL REFERENCES audit_runs(id) ON DELETE CASCADE,
    dimension VARCHAR(50) NOT NULL,
    fairness_score FLOAT NOT NULL,
    disparity_ratio FLOAT NOT NULL,
    demographic_parity_diff FLOAT,
    confidence_lower FLOAT,
    confidence_upper FLOAT,
    sample_size INTEGER,
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_fairness_audit ON fairness_scores(audit_run_id);

-- ── Bias Explanations ─────────────────────────────────────────
CREATE TABLE bias_explanations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_run_id UUID NOT NULL REFERENCES audit_runs(id) ON DELETE CASCADE,
    dimension VARCHAR(50) NOT NULL,
    explanation_text TEXT NOT NULL,
    root_cause VARCHAR(255),
    severity VARCHAR(10) NOT NULL CHECK (severity IN ('low', 'medium', 'high')),
    affected_metric VARCHAR(100),
    legal_implications TEXT
);

CREATE INDEX idx_explanations_audit ON bias_explanations(audit_run_id);

-- ── Mitigation Recommendations ────────────────────────────────
CREATE TABLE mitigation_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_run_id UUID NOT NULL REFERENCES audit_runs(id) ON DELETE CASCADE,
    dimension VARCHAR(50) NOT NULL,
    recommendation_type VARCHAR(20) NOT NULL CHECK (recommendation_type IN ('data_level', 'feature_level', 'output_level', 'model_level')),
    recommendation_text TEXT NOT NULL,
    effort_level VARCHAR(10) NOT NULL CHECK (effort_level IN ('low', 'medium', 'high')),
    impact_level VARCHAR(10) NOT NULL CHECK (impact_level IN ('low', 'medium', 'high', 'very_high')),
    priority INTEGER NOT NULL
);

CREATE INDEX idx_mitigations_audit ON mitigation_recommendations(audit_run_id);

-- ── Audit Reports ─────────────────────────────────────────────
CREATE TABLE audit_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_run_id UUID NOT NULL REFERENCES audit_runs(id) ON DELETE CASCADE,
    pdf_filepath VARCHAR(500),
    csv_filepath VARCHAR(500),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    downloaded_count INTEGER DEFAULT 0
);

CREATE INDEX idx_reports_audit ON audit_reports(audit_run_id);
