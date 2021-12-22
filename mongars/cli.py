import argparse
import imaplib
import logging

from .accounts import GOA


def get_unseen(mailbox: str, conn) -> list:
    resp, _ = conn.select(mailbox)
    if resp != "OK":
        logging.debug("cannot select mailbox %s", mailbox)
        return []
    ret, messages = conn.search(None, "(UNSEEN)")
    if ret != "OK":
        logging.debug("cannot search unseen")
        return []
    return messages[0].split()


def parse_args() -> argparse.Namespace:
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
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
    return args


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

        return f"{iconstring} {str(len(unseens))}"

    logging.debug("account not found")
    return ""


def main():
    args = parse_args()
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
