CREATE OR REPLACE FUNCTION zylora_is_super_admin() RETURNS boolean LANGUAGE sql STABLE AS $$
  SELECT COALESCE(current_setting('app.is_super_admin', true), 'false') = 'true'
$$;
CREATE OR REPLACE FUNCTION zylora_current_tenant() RETURNS uuid LANGUAGE sql STABLE AS $$
  SELECT NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
$$;
CREATE OR REPLACE FUNCTION zylora_public_tenant() RETURNS uuid LANGUAGE sql STABLE AS $$
  SELECT NULLIF(current_setting('app.public_tenant_id', true), '')::uuid
$$;

DO $$ DECLARE table_name text; BEGIN
  FOREACH table_name IN ARRAY ARRAY[
    'analytics_events','api_credentials','assets','audit_logs','change_requests','chat_conversations','chat_messages',
    'client_invitations','credit_accounts','credit_reservations','credit_transactions','document_chunks','documents',
    'domains','feature_flags','invoices','lead_notes','leads','notification_jobs','notification_settings','payments',
    'seo_audits','site_versions','sites','tenant_memberships','tenant_notes','tenants'
  ] LOOP
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
    EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', table_name);
  END LOOP;
END $$;

CREATE POLICY tenants_private ON tenants FOR ALL
USING (zylora_is_super_admin() OR id = zylora_current_tenant())
WITH CHECK (zylora_is_super_admin() OR id = zylora_current_tenant());

DO $$ DECLARE table_name text; BEGIN
  FOREACH table_name IN ARRAY ARRAY[
    'analytics_events','api_credentials','assets','audit_logs','change_requests','chat_conversations','chat_messages',
    'client_invitations','credit_accounts','credit_reservations','credit_transactions','document_chunks','documents',
    'domains','feature_flags','invoices','lead_notes','leads','notification_jobs','notification_settings','payments',
    'seo_audits','site_versions','sites','tenant_memberships','tenant_notes'
  ] LOOP
    EXECUTE format('CREATE POLICY %I ON %I FOR ALL USING (zylora_is_super_admin() OR tenant_id = zylora_current_tenant()) WITH CHECK (zylora_is_super_admin() OR tenant_id = zylora_current_tenant())', table_name || '_private', table_name);
  END LOOP;
END $$;

-- Public website lookup is limited to already-published, active records.
CREATE POLICY domains_public_read ON domains FOR SELECT USING (status = 'ACTIVE');
CREATE POLICY sites_public_read ON sites FOR SELECT USING (published_version_id IS NOT NULL AND is_active = true);
CREATE POLICY site_versions_public_read ON site_versions FOR SELECT USING (status = 'PUBLISHED');
CREATE POLICY feature_flags_public_read ON feature_flags FOR SELECT USING (tenant_id = zylora_public_tenant());
CREATE POLICY document_chunks_public_read ON document_chunks FOR SELECT USING (tenant_id = zylora_public_tenant());
CREATE POLICY notification_settings_public_read ON notification_settings FOR SELECT USING (tenant_id = zylora_public_tenant());
CREATE POLICY assets_public_read ON assets FOR SELECT USING (tenant_id = zylora_public_tenant() AND status = 'READY' AND scan_status = 'CLEAN');

-- Public writes are restricted to the tenant context set after published-site validation.
CREATE POLICY leads_public_insert ON leads FOR INSERT WITH CHECK (tenant_id = zylora_public_tenant());
CREATE POLICY notification_jobs_public_insert ON notification_jobs FOR INSERT WITH CHECK (tenant_id = zylora_public_tenant());
CREATE POLICY analytics_public_insert ON analytics_events FOR INSERT WITH CHECK (tenant_id = zylora_public_tenant());
CREATE POLICY chat_conversations_public ON chat_conversations FOR ALL USING (tenant_id = zylora_public_tenant()) WITH CHECK (tenant_id = zylora_public_tenant());
CREATE POLICY chat_messages_public ON chat_messages FOR ALL USING (tenant_id = zylora_public_tenant()) WITH CHECK (tenant_id = zylora_public_tenant());
