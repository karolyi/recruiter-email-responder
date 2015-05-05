#!/usr/local/bin/python3

import sys
import os
import smtplib
import sqlite3
import datetime
import syslog
import codecs

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
from email import header
from email.utils import parseaddr

# CWD to our dir, just to be on the safe side
my_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(my_dir)


def join_first_items(item_list):
    result_list = []
    for item in item_list:
        if type(item[0]) is bytes:
            result_list.append(item[0].decode('utf-8'))
        elif type(item[0]) is str:
            result_list.append(item[0])
    return ''.join(result_list)


def make_address(header_item):
    parsed = parseaddr(header_item)
    result = ''
    if parsed[0]:
        result += '"%s" <%s>' % (
            join_first_items(header.decode_header(parsed[0])),
            parsed[1])
    else:
        result += parsed[1]
    return result

# original_headers = Parser().parsestr(sys.stdin.read())
with open('email1.txt') as fp:
    original_headers = Parser().parsestr(fp.read())

decoded_from = join_first_items(
    header.decode_header(original_headers['From']))
decoded_to = join_first_items(
    header.decode_header(original_headers['To']))
decoded_subject = join_first_items(
    header.decode_header(original_headers['Subject']))

smtp_to = make_address(original_headers['From'])
smtp_from = make_address(original_headers['To'])

conn = sqlite3.connect(
    os.path.join(my_dir, 'emails.db'),
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cursor = conn.cursor()
cursor.execute(
    'SELECT * FROM email_usage WHERE email = ?',
    (
        decoded_from,
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
            decoded_from,
        )
    )
    conn.commit()
    if last_used_ts >= one_day_before:
        cursor.close()
        conn.close()
        syslog.syslog(
            'Not sending recruiter autoreply to %s, last sent at %s' % (
                decoded_from, last_used_ts)
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
            decoded_from,
            1
        )
    )
    conn.commit()
cursor.close()
conn.close()

# Prepare and send the email
syslog.syslog('Sending recruiter autoreply to %s' % decoded_from)

msg = MIMEMultipart('alternative')
msg['Subject'] = 'Re: %s' % decoded_subject
msg['From'] = decoded_to
msg['To'] = decoded_from
if original_headers['Message-Id']:
    msg['References'] = original_headers['Message-Id']

with codecs.open('text-reply.txt', 'r', 'utf-8') as fp:
    text_reply = fp.read()

with codecs.open('html-reply.html', 'r', 'utf-8') as fp:
    html_reply = fp.read()

part1 = MIMEText(text_reply, 'plain')
part2 = MIMEText(html_reply, 'html')

msg.attach(part1)
msg.attach(part2)

s = smtplib.SMTP('localhost')
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
s.sendmail(
    smtp_from,
    smtp_to,
    msg.as_string())
s.quit()
