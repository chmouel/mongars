import argparse
import pathlib
import subprocess
import tempfile

from google.auth.transport.requests import Request  # type: ignore
from google.oauth2.credentials import Credentials  # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore
from googleapiclient.discovery import build  # type: ignore

from .display import show_json, show_markdown, show_unseens
from .passwordstore import get_item_from_pass, store_item_in_pass

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
]

PASS_TOKEN_KEY = "google/{email}.mail.token"
PASS_CRED_KEY = "google/{email}.mail.credential"


def gauth_get_creds(args: argparse.Namespace):
    creds = None
    token_json = ""
    try:
        token_json = get_item_from_pass(
            args.gauth_pass_token_key.format(email=args.email)
        )
    except subprocess.CalledProcessError:
        pass
    if token_json:
        with tempfile.NamedTemporaryFile() as tmpff:
            tmpff.write(token_json.encode())
            tmpff.flush()
            creds = Credentials.from_authorized_user_file(
                pathlib.Path(tmpff.name), SCOPES
            )
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

        store_item_in_pass(
            args.gauth_pass_token_key.format(email=args.email), creds.to_json()
        )
    return creds


def gauth_check_unseens(args: argparse.Namespace) -> list:
    creds = gauth_get_creds(args)
    service = build("gmail", "v1", credentials=creds)
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
        row["snippet"] = msg["snippet"]
        ret.append(row)

    return ret


def gauth_check_accounts(args: argparse.Namespace) -> str:
    unseens = gauth_check_unseens(args)
    if args.show_markdown:
        return show_markdown(args, unseens)
    if args.show_json:
        return show_json(args, unseens)

    return show_unseens(args, unseens)
