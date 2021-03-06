[![Buy me a coffee](https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/orange_img.png)](https://www.buymeacoffee.com/t159YOryp)

# recruiter-email-responder

- Tired of constantly getting emails from recruiters who are simply too lazy
  to understand your terms?
- Did you at first give hints in your replies, mentioning your terms but they
  did't give a flying fuck?
- Did you already set up a vacation autoresponse but they use lists and your
  emails get delivered to the list response (/dev/null most of the time)?
- Do you get a fuckton of recurring irrelevant inquiries?

Then this is for you. If you set up your email server to pipe the email body
into this tool after filtering for the addresses (used with dovecot2/sieve
filters in my case), it will send replies to the `From` header, not the `Return-Path` one.

Am I a dick for implementing this? No more than the recruiters unwilling to
update their filters/mailing lists.

Nonetheless, this program will only send 1 reply per day, whereas they often
send tons of emails daily.

Used python3 modules:
- `smtplib` to send the email via `localhost:25`
- `sqlite3` to check the sender DB to not resend emails in a day
- `email` to construct the email.
- `syslog` for logging the sending of emails into syslog

External modules:
- `chardet`, to autodetect the input charset (which can vary)

## Requirements:

- A mailserver.
- Sqlite and its python bindings.
- `text-reply.txt` containing the text version of your reply
- `html-reply.html` containing the html version of your reply

## Setup:

- Install `python3` (do I need to say this?)
- Clone this repository into a random directory, reachable for dovecot2
- Change to that directory
- Install virtualenv and external modules by running `tools/install.sh`
- Initialize the sqlite db with running `tools/init-schema.sh`
- Copy your replies (mentioned above) into the same repo directory
- Edit your sieve configuration/procmailrc to pipe your given role into this tool. The executable is `email-responder.sh`, which uses the virtualenv created (not `email-responder.py`!).

