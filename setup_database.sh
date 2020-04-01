#!/bin/sh

exec mysql < setup_database/db_setup.txt &
sleep 1
exec mysql -u testuser -p < setup_database/users_setup.txt &
sleep 10
exec mysql -u testuser -p < setup_database/posts_setup.txt
