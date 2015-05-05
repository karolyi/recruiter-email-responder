#!/usr/bin/env sh

echo "CREATE TABLE email_usage (lastused timestamp, email character(100), mailcount unsigned integer);" | sqlite3 emails.db
# auth-userdb user will run the python code
chown vmail emails.db
# change the containing directory's user to the one running the script.
chown vmail:vmail .
