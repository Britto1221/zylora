# Leads

Public leads support identity, contact details, requested service, preferred
contact method, message, consent, campaign metadata, source, and honeypot spam
protection.

The API commits the lead and its notification jobs together. Notification or
Redis failures occur after the public success response and cannot erase the lead.

The dashboard supports filtering, status transitions, notes, history, and CSV
export. Consent timestamps and notification states are retained for auditability.
