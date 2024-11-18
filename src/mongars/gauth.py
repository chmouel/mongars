import argparse
import multiprocessing
import pathlib
import subprocess
import tempfile

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore

from .display import show_json, show_markdown, show_unseens
from .notifications import notify
from .passwordstore import get_item_from_pass

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

PASS_CRED_KEY = "google/{email}.mail.credential"
TOKEN_JSON_FILE = "~/.cache/mongars/token.{email}.json"


def gauth_get_creds(args: argparse.Namespace):
    creds = None
    token_json_file: pathlib.Path = pathlib.Path(
        args.gauth_pass_token_file.format(email=args.email)
    ).expanduser()
    if token_json_file.exists():
        creds = Credentials.from_authorized_user_file(token_json_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            gauth_pass_cred_key = args.gauth_pass_cred_key.format(email=args.email)
            try:
                cred_json = get_item_from_pass(gauth_pass_cred_key)
            except (subprocess.CalledProcessError, Exception) as err:
                raise Exception("No credentials found") from err
            if not cred_json:
                raise Exception(
                    f"No credentials found in pass key {gauth_pass_cred_key}"
                )

            with tempfile.NamedTemporaryFile() as tmpff:
                tmpff.write(cred_json.encode())
                tmpff.flush()
                flow = InstalledAppFlow.from_client_secrets_file(
                    pathlib.Path(tmpff.name),
                    SCOPES,
                )
                creds = flow.run_local_server(open_browser=False)
                if not creds:
                    raise Exception("Cannot run flow")
        token_json_file.parent.mkdir(parents=True, exist_ok=True)
        token_json_file.write_text(creds.to_json())
    return creds


def gauth_check_unseens(args: argparse.Namespace) -> list:
    creds = gauth_get_creds(args)
    service = build("gmail", "v1", credentials=creds)
    args.service = service
    results = (
        service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q="is:unread")
        .execute()
    )
    messages = results.get("messages", [])
    if not messages:
        return []
    ret = []
    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        email_data = msg["payload"]["headers"]
        row = {
            x["name"]: x["value"]
            for x in email_data
            if x["name"] in ("Subject", "From", "To", "Message-ID", "Date")
        }
        row["Snippet"] = msg["snippet"]
        row["ID"] = msg["id"]
        ret.append(row)

    return ret


def gauth_check_accounts(args: argparse.Namespace) -> str:
    unseens = gauth_check_unseens(args)

    if args.show_markdown:
        return show_markdown(args, unseens)
    if args.show_json:
        return show_json(args, unseens)

    proc = multiprocessing.Process(target=notify, args=(args, unseens))
    proc.start()
    proc.join()
    return show_unseens(args, unseens)
