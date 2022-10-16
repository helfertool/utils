#!/usr/bin/env python3

import argparse
import yaml
import imaplib
import sys
import socket
import datetime
import locale

# command line arguments
parser = argparse.ArgumentParser(description="Cleanup old mails from IMAP folder")
parser.add_argument("--config", required=True, help="Path to Helfertool config (helfertool.yaml)")
parser.add_argument(
    "--days",
    required=True,
    type=int,
    help="Delete mails which are older than this number of days",
)
parser.add_argument("--dry-run", action="store_true", help="do not really delete the mails")

args = parser.parse_args()


# parse helfertool.yaml config file
try:
    with open(args.config, "r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
except (FileNotFoundError, IOError):
    print("Cannot read configuration file")
    sys.exit(1)
except yaml.parser.ParserError as e:
    print("Syntax error in configuration file")
    sys.exit(1)

try:
    tmp = config["mail"]["receive"]

    mail_host = tmp["host"]
    mail_port = tmp["port"]
    mail_user = tmp["user"]
    mail_password = tmp["password"]

    mail_use_tls = tmp.get("tls", False)
    mail_use_starttls = tmp.get("starttls", False)
    mail_folder = tmp.get("folder", "INBOX")
except KeyError:
    print("Incomplete configuration - receiving of mails not configured")
    sys.exit(1)


# connect to mail server
try:
    if mail_use_tls:
        imap_connection = imaplib.IMAP4_SSL(host=mail_host, port=mail_port)
    else:
        imap_connection = imaplib.IMAP4(host=mail_host, port=mail_port)

    if mail_use_starttls:
        imap_connection.starttls()
except (imaplib.IMAP4.error, ConnectionRefusedError, socket.gaierror):
    print("Invalid hostname, port or TLS settings")
    sys.exit(1)

# login
try:
    imap_connection.login(mail_user, mail_password)
except imaplib.IMAP4.error:
    print("Invalid username or password")
    sys.exit(1)

# select folder
try:
    ret, data = imap_connection.select(mail_folder)

    if ret != "OK":
        print("Invalid folder")
        sys.exit(1)
except imaplib.IMAP4.error:
    print("Invalid folder")
    sys.exit(1)

# search for old messages
timestamp = datetime.date.today() - datetime.timedelta(days=args.days)
locale.setlocale(locale.LC_TIME, "C")  # force english
timestamp_str = timestamp.strftime("%d-%b-%Y")

ret, data = imap_connection.uid("search", "BEFORE {}".format(timestamp_str))
if ret != "OK":
    print("Failed to receive messages")
    sys.exit(1)

msg_ids = data[0].strip().decode().split()

print("Number of messages received before {} ({} days): {}".format(timestamp_str, args.days, len(msg_ids)))

# delete old messages
if not args.dry_run:
    for msg_id in msg_ids:
        imap_connection.uid("store", msg_id, "+FLAGS", "\\Deleted")

    imap_connection.expunge()

    print("Deleted.")
else:
    print("NOT deleted - dry run.")

# close connection
imap_connection.close()
imap_connection.logout()
