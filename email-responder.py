#!/usr/bin/env python3

import sys
import os
import smtplib
import sqlite3
import datetime
import syslog

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser

# CWD to our dir, just to be on the safe side
my_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(my_dir)

original_headers = Parser().parsestr(sys.stdin.read())
# with open('email1.txt') as fp:
#     original_headers = Parser().parsestr(fp.read())

conn = sqlite3.connect(
    'emails.db',
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cursor = conn.cursor()
cursor.execute(
    'SELECT * FROM email_usage WHERE email = ?',
    (
        original_headers['From'],
    )
)
rows = cursor.fetchall()
if len(rows):
    last_used_ts = rows[0][0]
    one_day_before = datetime.datetime.now() - datetime.timedelta(days=1)
    cursor.execute(
        (
            'UPDATE email_usage SET mailcount = mailcount + 1 '
            'WHERE email = ?'
        ),
        (
            original_headers['From'],
        )
    )
    conn.commit()
    if last_used_ts >= one_day_before:
        cursor.close()
        conn.close()
        syslog.syslog(
            'Not sending recruiter autoreply to %s, last sent at %s' % (
                original_headers['From'], last_used_ts)
        )
        sys.exit(0)

if len(rows) == 0:
    cursor.execute(
        (
            'INSERT INTO email_usage (lastused, email, mailcount)'
            ' VALUES (?, ?, ?)'
        ),
        (
            datetime.datetime.now(),
            original_headers['From'],
            1
        )
    )
    conn.commit()
cursor.close()
conn.close()


# Prepare and send the email
syslog.syslog('Sending recruiter autoreply to %s' % original_headers['From'])

msg = MIMEMultipart('alternative')
msg['Subject'] = 'Re: %s' % original_headers['Subject']
msg['From'] = original_headers['To']
msg['To'] = original_headers['From']
if original_headers['Message-Id']:
    msg['References'] = original_headers['Message-Id']

with open('text-reply.txt') as fp:
    text_reply = fp.read()

with open('html-reply.html') as fp:
    html_reply = fp.read()

part1 = MIMEText(text_reply, 'plain')
part2 = MIMEText(html_reply, 'html')

msg.attach(part1)
msg.attach(part2)

s = smtplib.SMTP('localhost')
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
s.sendmail(
    original_headers['To'],
    original_headers['From'],
    msg.as_string())
s.quit()
