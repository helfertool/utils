# Helfertool utils

## mail-cleaner

Helfertool can parse incoming mails and extract the non-delivery reports.
Therefore, an IMAP mailbox is required that contains these incoming mails.

The tool only marks the handled mails as read, but does not delete them.
If you also want to delete old mails, you can use the `mail-cleaner.py` script to achieve this.

It uses the same `helfertool.yaml` config file as Helfertool:

    ./mail-cleaner.py [--dry-run] --config /etc/helfertool/helfertool.yaml --days 90

This would delete all mails older than 90 days in the configured mailbox and folder.
