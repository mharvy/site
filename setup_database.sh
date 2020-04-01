#!/bin/sh

exec mysql < setup_database/db_setup.txt &
sleep 1
exec mysql -u testuser -p < setup_database/userinfo_setup.txt
