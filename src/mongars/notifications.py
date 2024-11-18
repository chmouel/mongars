import argparse
import datetime
import os
import pathlib
import shutil
import sqlite3
import subprocess
import typing

from google_auth_oauthlib.flow import webbrowser

DB_PATH = pathlib.Path(f"{os.environ.get('HOME')}/.cache/mongars/notified.db")
# pylint: disable=line-too-long
NOTIFY_SEND_TEMPLATE_COMMAND = """notify-send -a org.chmouel.mongars -c email.arrived -u low -A open="Open" -A archive="Archive" -i "{icon}" "{sender}" "{subject}" """
GMAIL_URL = "https://mail.google.com/mail/u/0"
NOTIFY_TIMEOUT = 2


def cleanup_str(toreplace: str) -> str:
    return (
        toreplace.replace('"', '\\"')
        .replace("'", "\\'")
        .replace("$", "\\$")
        .replace("\u200c", "")
    )


def search_id_uuid(iid: str, uuids: typing.List[dict]) -> dict:
    for uuid in uuids:
        if uuid["ID"] == iid:
            return uuid
    return {}


def wait_for_process(
    args: argparse.Namespace, processes: dict, uuids: typing.List[dict]
):
    for mid, (process, _) in processes.items():
        try:
            action, _ = process.communicate(timeout=args.notify_timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            continue
        match action.decode().strip():
            case "open":
                uuid = search_id_uuid(mid, uuids)
                url = f"""{args.gmail_url}/#search/"{uuid["Subject"]}\""""
                webbrowser.open(url)
            case "archive":
                args.service.users().messages().modify(
                    userId="me", id=mid, body={"removeLabelIds": ["INBOX"]}
                ).execute()


def notify(args: argparse.Namespace, uuids: typing.List[dict]):
    if os.fork() != 0:
        return
    if not shutil.which(args.notify_command_template.split(" ")[0]):
        return
    processes = {}
    for uuid in uuids:
        if not uuid.get("Message-ID"):
            continue
        if insert_or_exist(uuid["Message-ID"]):
            continue
        icon = "mail.png"
        if args.notify_icon_path and os.path.exists(args.notify_icon_path):
            icon = args.notify_icon_path
        if args.notify_command_template:
            # change all double quote or single quote or $ as unquoted
            subject = cleanup_str(uuid["Subject"])
            snippet = cleanup_str(uuid["Snippet"])
            sender = cleanup_str(uuid["From"])
            command = args.notify_command_template.format(
                icon=icon, subject=subject, snippet=snippet, sender=sender
            )
            # pylint: disable=consider-using-with
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            processes[uuid["ID"]] = (process, datetime.datetime.now())
    wait_for_process(args, processes, uuids)


def insert_or_exist(uuid: str) -> bool:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
    CREATE TABLE IF NOT EXISTS messages
        (ID INTEGER PRIMARY KEY, UUID TEXT, DATE DATETIME DEFAULT CURRENT_TIMESTAMP)
    """
    )
    curr = conn.cursor()
    curr.execute("SELECT 1 FROM messages where uuid=?", (uuid,))
    row = curr.fetchone()
    if row:
        return True

    conn.execute(
        "INSERT INTO messages (uuid) VALUES(?)",
        (uuid,),
    )
    conn.commit()
    conn.close()

    return False
