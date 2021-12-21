import email
import argparse
import imaplib
import typing

from .accounts import GOA


def get_unseen(mailbox: str, conn) -> typing.Union[str, list]:
    resp, _ = conn.select(mailbox)
    if resp != "OK":
        return "BADMBOX"
    ret, messages = conn.search(None, "(UNSEEN)")
    if ret != "OK":
        return "CANNOTSEARCH"
    return messages[0].split()

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Show email count from Gnome Online Account')
    parser.add_argument("email")
    parser.add_argument("--mailbox",
                        "-m",
                        default="INBOX",
                        help="Mailbox to check")
    args = parser.parse_args()
    return args


def check_accounts(args: argparse.Namespace) -> str:
    accounts = GOA.get_accounts()
    if not accounts:
        return "NO_ACCOUNT_CONFIGURED"
    for account in accounts:
        if account["user"] != args.email:
            continue
        conn = imaplib.IMAP4_SSL(account["host"])
        # pylint: disable=cell-var-from-loop
        resp, _ = conn.authenticate('XOAUTH2', lambda _: account["oauth"])
        if resp != "OK":
            return "AUTHERR"
        unseens = get_unseen(args.mailbox, conn)
        if isinstance(unseens, str):
            return unseens
        # python can be weird sometime empty bytes is defined when empty string are not
        if len(unseens) > 0:
            return str(len(unseens))
        return ""

    return "NOTFOUND"


def main():
    ret = check_accounts(parse_args())
    if ret:
        print(ret)
