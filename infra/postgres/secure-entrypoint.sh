#!/bin/sh
set -eu

CERT_DIR=/var/lib/postgresql/zylora-certs
install -d -m 700 -o postgres -g postgres "$CERT_DIR"
install -m 644 -o postgres -g postgres /run/secrets/postgres_server_crt "$CERT_DIR/server.crt"
install -m 600 -o postgres -g postgres /run/secrets/postgres_server_key "$CERT_DIR/server.key"
install -m 644 -o postgres -g postgres /run/secrets/postgres_ca_crt "$CERT_DIR/ca.crt"

exec /usr/local/bin/docker-entrypoint.sh "$@"
