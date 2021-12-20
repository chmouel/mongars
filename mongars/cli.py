# pylint: disable=unused-import
import argparse
import sys

from imapclient import IMAPClient

from .accounts import GOA


def get_unseen(server) -> int:
    x = server.folder_status('INBOX', [b'UNSEEN'])
    return x[b'UNSEEN']

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Show email count from Gnome Online Account')
    parser.add_argument("email")
    parser.add_argument("--mailbox", "-m", default="INBOX", help="Mailbox to check")
    args = parser.parse_args()
    return args

def check_accounts(args: argparse.Namespace):
    accounts = GOA.get_accounts()
    if not accounts:
        return
    found = False
    for account in accounts:
        if account["user"] != args.email:
            continue
        found = True
        with IMAPClient(account["host"]) as server:
            server.oauth2_login(account["user"], account["token"])
            server.select_folder(args.mailbox, readonly=True)
            unreads = get_unseen(server)
            if unreads > 0:
                print(unreads)
    if not found:
        print("NOTFOUND")

def main():
    check_accounts(parse_args())
