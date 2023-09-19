import argparse
import email
import imaplib
import logging

from .accounts import GOA
from .display import decode_str, show_unseens


def imap_check_accounts(args: argparse.Namespace) -> str:
    accounts = GOA.get_accounts()
    if not accounts:
        logging.debug("No account has been configured")
        return ""

    for account in accounts:
        if account["user"] != args.email:
            continue
        conn = imaplib.IMAP4_SSL(account["host"])
        unseens = imap_get_unseens(args.mailbox, conn)
        ret = show_unseens(args, unseens)
        conn.close()
        return ret

    logging.debug("account not found")
    return ""


def imap_get_unseens(mailbox: str, conn) -> dict:
    unseens = {}
    resp, _ = conn.select(mailbox)
    if resp != "OK":
        logging.debug("cannot select mailbox %s", mailbox)
        return {}
    ret, messages = conn.search(None, "(UNSEEN)")
    if ret != "OK":
        logging.debug("cannot search unseen")
        return unseens
    if not messages[0]:
        return unseens
    for msg in messages[0].decode().split(" "):
        _, response = conn.fetch(msg, "(BODY.PEEK[HEADER])")
        msg = email.message_from_bytes(response[0][1])

        msgfrom = decode_str(msg["From"])
        msg_subject = decode_str(msg["Subject"]) if msg.get("Subject") else "No Subject"
        unseens[msg.get("Message-Id")] = f"{msgfrom} - {msg_subject}"
    return unseens
