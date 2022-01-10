import argparse
import email
from email.header import decode_header
import imaplib
import logging
import sys

from .accounts import GOA
from .notify import notify_if_not_already


def get_unseen(mailbox: str, conn) -> dict:
    unseens = {}
    default_charset = 'ASCII'
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
    for msg in messages[0].decode().split(' '):
        _, response = conn.fetch(msg, '(BODY.PEEK[HEADER])')
        msg = email.message_from_bytes(response[0][1])
        msgfrom = ''.join([
            str(t[0], t[1] or default_charset)
            for t in decode_header(msg["From"])
        ])
        msg_subject = "No Subject"
        if msg["Subject"]:
            msg_subject = ''.join([
                str(t[0], t[1] or default_charset)
                for t in decode_header(msg["Subject"])
                ])
        unseens[msg.get("Message-Id")] = f'{msgfrom} - {msg_subject}'
    return unseens


def parse_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Show email count from Gnome Online Account')
    parser.add_argument("email")
    parser.add_argument("--verbose",
                        "-v",
                        action="store_true",
                        default=False,
                        help="Be verbose")
    parser.add_argument("--mailbox",
                        "-m",
                        default="INBOX",
                        help="Mailbox to check")
    parser.add_argument(
        "--no-mail-no-zero",
        action="store_true",
        help=
        "if we have no mail don't output anything (by default we output a 0)")
    parser.add_argument("--notify", action="store_true")
    parser.add_argument("--no-icon",
                        action="store_true",
                        default=False,
                        help="wether we output an icon")
    parser.add_argument("--icon",
                        default="",
                        help="icon to use by default (need to be a glyph)")
    parser.add_argument("--icon-color-unreads",
                        default="#ffd700",
                        help="icon color when there is unreads")
    parser.add_argument("--icon-color-normal",
                        help="icon color when there is unreads")
    parser.add_argument("--show-from-subject",
                        action="store_true",
                        help="Show from and subject of new emails")
    args = parser.parse_args(args)
    if args.verbose:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
    return args


# pylint: disable=too-many-return-statements
def check_accounts(args: argparse.Namespace) -> str:
    accounts = GOA.get_accounts()
    if not accounts:
        logging.debug("No account has been configured")
        return ""
    for account in accounts:
        if account["user"] != args.email:
            continue
        conn = imaplib.IMAP4_SSL(account["host"])
        # pylint: disable=cell-var-from-loop
        resp, _ = conn.authenticate('XOAUTH2', lambda _: account["oauth"])
        if resp != "OK":
            logging.debug("error authenticating to account")
            return ""
        unseens = get_unseen(args.mailbox, conn)
        if args.no_mail_no_zero and len(unseens) == 0:
            return ""

        if args.notify:
            notify_if_not_already(unseens)

        if args.show_from_subject:
            return "\n".join(unseens.values())

        if args.no_icon:
            return str(len(unseens))

        iconstring = f"{args.icon}"
        if len(unseens) == 0 and args.icon_color_normal:
            # pylint: disable=consider-using-f-string
            iconstring = "%%{F%s}%s%%{F-}" % (args.icon_color_normal,
                                              args.icon)
        elif len(unseens) > 0 and args.icon_color_unreads:
            # pylint: disable=consider-using-f-string
            iconstring = "%%{F%s}%s%%{F-}" % (
                args.icon_color_unreads,
                args.icon,
            )
        conn.close()
        return f"{iconstring} {str(len(unseens))}"

    logging.debug("account not found")
    return ""


def main():
    args = parse_args(sys.argv[1:])
    ret = None
    try:
        ret = check_accounts(args)
    # pylint: disable=broad-except
    except Exception as exp:
        if args.verbose:
            logging.exception(exp)
        return
    if ret:
        print(ret)
