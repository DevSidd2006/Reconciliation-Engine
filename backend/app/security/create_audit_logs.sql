-- Banking-Grade Audit Logs Table for Transaction Reconciliation Engine
-- This table stores comprehensive audit trail for compliance and security monitoring

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- User Information
    user_id TEXT,
    username TEXT,
    session_id TEXT,
    
    -- Request Information
    method TEXT,
    endpoint TEXT,
    ip_address TEXT,
    user_agent TEXT,
    
    -- Event Information
    event_type TEXT NOT NULL,
    action TEXT NOT NULL,
    resource TEXT,
    resource_id TEXT,
    
    -- Status and Results
    success BOOLEAN NOT NULL DEFAULT FALSE,
    status_code INTEGER,
    error_message TEXT,
    
    -- Security Context
    roles TEXT,
    permissions TEXT,
    
    -- Additional Context
    details JSONB,
    risk_score INTEGER DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_username ON audit_logs(username);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_endpoint ON audit_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_address ON audit_logs(ip_address);
CREATE INDEX IF NOT EXISTS idx_audit_logs_success ON audit_logs(success);
CREATE INDEX IF NOT EXISTS idx_audit_logs_risk_score ON audit_logs(risk_score);

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_timestamp ON audit_logs(user_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_timestamp ON audit_logs(event_type, timestamp);

-- Add comments for documentation
COMMENT ON TABLE audit_logs IS 'Banking-grade audit log for security compliance and monitoring';
COMMENT ON COLUMN audit_logs.risk_score IS 'Risk assessment score: 0=low, 25=medium, 50=high, 100=critical';