# recruiter-email-responder

- Tired of constantly getting emails from recruiters who are simply too lazy
  to understand your requirements? Without end?
- You've already set up a vacation response but they use lists and your emails
  get delivered to the list response (/dev/null most of the time)?

Then this is for you. If you set up your email server to pipe the email into
this tool after filtering for the addresses (used with dovecot2/sieve filters),
it will send replies to the `From` header, not the `Return-Path` one.

Am I a dick to implement this? Not less than the recruiters not willing to
update their filters/mailing lists.

Nonetheless, this program will only send 1 reply per day, whereas they often
send tons of emails daily.

Used python3 modules:
    - `smtplib` to send the email via localhost:25
    - `sqlite3` to check the sender DB to not resend emails in a day
    - `email` to construct the email.

## Requirements:

Pretty much nothing other than `python3`. Modules come shipped.

- `text-reply.txt` containing the text version of your reply
- `html-reply.html` containing the html version of your reply

## Setup:

- Install `python3` (do I need to say this?)
- Install this repository into a random directory, reachable for dovecot2
- Copy your replies (mentioned above) into the same repo directory
- Edit your sieve configuration to pipe your given role into this tool.

