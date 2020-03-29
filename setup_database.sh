#!/bin/sh

exec mysql < setup/db_setup.txt &
sleep 1
exec mysql -u testuser -p < setup/userinfo_setup.txt
