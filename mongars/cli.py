import argparse
import logging
import sys

from .gauth import PASS_CRED_KEY, PASS_TOKEN_KEY, gauth_check_accounts


def parse_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show email count from Gnome Online Account"
    )
    parser.add_argument("email")
    parser.add_argument(
        "--verbose", "-v", action="store_true", default=False, help="Be verbose"
    )
    parser.add_argument("--mailbox", "-m", default="INBOX", help="Mailbox to check")
    parser.add_argument(
        "--no-mail-no-zero",
        action="store_true",
        help="if we have no mail don't output anything (by default we output a 0)",
    )
    parser.add_argument("--notify", action="store_true")
    parser.add_argument(
        "--no-icon", action="store_true", default=False, help="wether we output an icon"
    )
    parser.add_argument(
        "--icon", default="", help="icon to use by default (need to be a glyph)"
    )
    parser.add_argument(
        "--icon-color-unreads",
        default="#ffd700",
        help="icon color when there is unreads",
    )
    parser.add_argument("--icon-color-normal", help="icon color when there is unreads")
    parser.add_argument(
        "--show-from-subject",
        action="store_true",
        help="Show from and subject of new emails",
    )

    parser.add_argument(
        "--show-markdown",
        "-M",
        action="store_true",
        help="Show as a markdown of all your events",
    )

    parser.add_argument(
        "--show-json",
        "-J",
        action="store_true",
        help="Show as a json for waybar",
    )
    parser.add_argument(
        "--gauth",
        action="store_true",
        help="use gauth, you need to have creds stored in password store",
    )
    parser.add_argument(
        "--gauth-pass-token-key",
        default=PASS_TOKEN_KEY,
        help="path to the key in the password store for storing token",
    )
    parser.add_argument(
        "--gauth-pass-cred-key",
        default=PASS_CRED_KEY,
        help="path to the key in the password store for storing creds",
    )

    args = parser.parse_args(args)
    if args.verbose:
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
    return args


def main():
    args = parse_args(sys.argv[1:])
    ret = None
    try:
        if args.gauth:
            ret = gauth_check_accounts(args)
        else:
            from .imap import imap_check_accounts

            ret = imap_check_accounts(args)
    # pylint: disable=broad-except
    except Exception as exp:
        if args.verbose:
            logging.exception(exp)
        return
    if ret:
        print(ret)
