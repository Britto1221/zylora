-- Execute only after integrating a verified authentication provider.
-- The application must set app.current_tenant_id for each request.

ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE site_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_credentials ENABLE ROW LEVEL SECURITY;

CREATE POLICY leads_tenant_isolation ON leads
USING (tenant_id::text = current_setting('app.current_tenant_id', true));

CREATE POLICY sites_tenant_isolation ON sites
USING (tenant_id::text = current_setting('app.current_tenant_id', true));

CREATE POLICY site_versions_tenant_isolation ON site_versions
USING (tenant_id::text = current_setting('app.current_tenant_id', true));

CREATE POLICY credit_accounts_tenant_isolation ON credit_accounts
USING (tenant_id::text = current_setting('app.current_tenant_id', true));

CREATE POLICY credit_transactions_tenant_isolation ON credit_transactions
USING (tenant_id::text = current_setting('app.current_tenant_id', true));

CREATE POLICY notification_jobs_tenant_isolation ON notification_jobs
USING (tenant_id::text = current_setting('app.current_tenant_id', true));

CREATE POLICY domains_tenant_isolation ON domains
USING (tenant_id::text = current_setting('app.current_tenant_id', true));

CREATE POLICY api_credentials_tenant_isolation ON api_credentials
USING (tenant_id::text = current_setting('app.current_tenant_id', true));
