import argparse
import logging
import os
import sys

from .gauth import PASS_CRED_KEY, TOKEN_JSON_FILE, gauth_check_accounts
from .notifications import GMAIL_URL, NOTIFY_SEND_TEMPLATE_COMMAND, NOTIFY_TIMEOUT


def parse_args(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show email count and notifications using Gmail API or Gnome Online Account"  # pylint: disable=line-too-long
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
        "--gauth-pass-token-file",
        default=TOKEN_JSON_FILE,
        help="path to the temporary file where the token is stored",
    )
    parser.add_argument(
        "--gauth-pass-cred-key",
        default=PASS_CRED_KEY,
        help="path to the key in the password store for storing creds",
    )
    parser.add_argument(
        "--no-gum-output",
        action="store_true",
        help="Don't pipe to gum the markdown output, just print it",
    )

    parser.add_argument(
        "--notify-command-template",
        default=NOTIFY_SEND_TEMPLATE_COMMAND,
    )

    parser.add_argument(
        "--notify-timeout",
        default=NOTIFY_TIMEOUT,
    )

    parser.add_argument("--gmail-url", default=GMAIL_URL)

    parser.add_argument(
        "--notify-icon-path",
        default=f"{os.environ.get('HOME')}/.local/share/icons/gmail.png",
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
