#!/bin/sh

exec mysql < setup_database/db_setup.txt &
sleep 1
exec mysql --defaults-file=setup_database/testuser.txt < setup_database/users_setup.txt &
exec mysql --defaults-file=setup_database/testuser.txt < setup_database/submissions_setup.txt &
exec mysql --defaults-file=setup_database/testuser.txt < setup_database/comments_setup.txt &
