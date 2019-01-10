#!/usr/local/bin/python3

import sys
import os
import smtplib
import sqlite3
import datetime
import syslog
import codecs
import chardet

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.parser import Parser
from email.utils import parseaddr
from email.header import decode_header, make_header

# CWD to our dir, just to be on the safe side
my_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(my_dir)

input_bytes = sys.stdin.buffer.read()  # This is bytes

encoding_result = chardet.detect(input_bytes)

syslog.syslog(
    syslog.LOG_DEBUG | syslog.LOG_MAIL,
    'Mail encoding: %s' % encoding_result)

input_decoded = input_bytes.decode(
    encoding_result['encoding'], errors='replace')

original_headers = Parser().parsestr(input_decoded)
# with open('email1.txt') as fp:
#     original_headers = Parser().parsestr(fp.read())

sender_address = parseaddr(original_headers['From'])[1]
receiver_address = parseaddr(original_headers['To'])[1] \
    if not sender_address.endswith('@linkedin.com') \
    else parseaddr(original_headers['Reply-To'])[1]


def remove_spam_flag(subject):
    parsed_subject = decode_header(subject)
    result = tuple()
    for item in parsed_subject:
        # Mystical, sometimes it's bytes, sometimes str, handle that
        item_zero = item[0]
        item_one = item[1]
        if type(item_one) is bytes:
            item_one = item_one.decode('ascii', errors='replace')
        if item_one is None:
            # If the encoding is None, we assume it's ascii
            item_one = 'ascii'
        if type(item_zero) is bytes:
            item_zero = item_zero.decode(item_one, errors='replace')
        result += (
            item_zero.replace('*****SPAM***** ', ''),
            item_one),  # Note it's a tuple
    return result

# For debug
# print (remove_spam_flag(original_headers['Subject']))

conn = sqlite3.connect(
    os.path.join(my_dir, 'emails.db'),
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
cursor = conn.cursor()
cursor.execute(
    'SELECT * FROM email_usage WHERE email = ?',
    (
        sender_address,
    )
)
rows = cursor.fetchall()
if len(rows):
    last_used_ts = rows[0][0]
    one_day_before = datetime.datetime.now() - datetime.timedelta(days=1)
    cursor.execute(
        (
            'UPDATE email_usage SET mailcount = mailcount + 1, '
            'lastused = CURRENT_TIMESTAMP WHERE email = ?'
        ),
        (
            sender_address,
        )
    )
    conn.commit()
    if last_used_ts >= one_day_before:
        cursor.close()
        conn.close()
        syslog.syslog(
            syslog.LOG_INFO | syslog.LOG_MAIL,
            'Not sending recruiter autoreply to %s, last sent at %s' % (
                sender_address, last_used_ts))
        sys.exit(0)

if len(rows) == 0:
    cursor.execute(
        (
            'INSERT INTO email_usage (lastused, email, mailcount)'
            ' VALUES (?, ?, ?)'
        ),
        (
            datetime.datetime.now(),
            sender_address,
            1
        )
    )
    conn.commit()
cursor.close()
conn.close()

# Prepare and send the email
syslog.syslog(
    syslog.LOG_INFO | syslog.LOG_MAIL,
    'Sending recruiter autoreply to %s' % sender_address)

msg = MIMEMultipart('alternative')
msg['Subject'] = 'Re: %s' % make_header(
    remove_spam_flag(original_headers['Subject']))
msg['From'] = original_headers['To']
msg['To'] = original_headers['From']
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
    receiver_address,
    sender_address,
    msg.as_string())
s.quit()
