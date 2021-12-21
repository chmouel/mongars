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

        if args.no_icon:
            return str(len(unseens))

        iconstring = f"{args.icon}"
        if len(unseens) == 0 and args.icon_color_normal:
            iconstring = "%%{F%s}%s%%{F-}" % (args.icon_color_normal,
                                              args.icon)
        elif len(unseens) > 0 and args.icon_color_unreads:
            iconstring = "%%{F%s}%s%%{F-}" % (
                args.icon_color_unreads,
                args.icon,
            )

        return f"{iconstring} {str(len(unseens))}"

    return "NOTFOUND"


def main():
    ret = check_accounts(parse_args())
    if ret:
        print(ret)
