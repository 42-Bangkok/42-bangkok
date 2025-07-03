#!/usr/bin/env fish

# Script to create frontend and backend databases in PostgreSQL
# Uses fixed credentials from docker-compose.yml

# PostgreSQL connection details
set db_host "db"
set db_port "5432"
set db_user "postgres"
set db_pass "postgres"
set db_name "postgres"

echo "Creating frontend and backend databases..."
echo "Using PostgreSQL at $db_host:$db_port with user $db_user"

# Connect to PostgreSQL and run the SQL commands
# Using PGPASSWORD to avoid password prompt
set -x PGPASSWORD $db_pass
psql -h $db_host -p $db_port -U $db_user -c "CREATE DATABASE frontend;"
psql -h $db_host -p $db_port -U $db_user -c "CREATE DATABASE backend;"
set -e PGPASSWORD
