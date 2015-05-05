#!/usr/bin/env sh

echo "CREATE TABLE email_usage (lastused timestamp, email character(100), mailcount unsigned integer);" | sqlite3 emails.db
