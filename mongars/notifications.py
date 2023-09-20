import argparse
import os
import pathlib
import shutil
import sqlite3
import typing

DB_PATH = pathlib.Path(f"{os.environ.get('HOME')}/.cache/mongars/notified.db")
MAX_ENTRY_CACHE = 200  # if you have more than 200, it is insane...


def cleanup_str(toreplace: str) -> str:
    return (
        toreplace.replace('"', '\\"')
        .replace("'", "\\'")
        .replace("$", "\\$")
        .replace("\u200c", "")
    )


def notify(args: argparse.Namespace, uuids: typing.List[dict]):
    if not shutil.which(args.notify_command_template.split(" ")[0]):
        return
    for uuid in uuids:
        if not uuid.get("Message-ID"):
            continue
        if insert_or_exist(uuid["Message-ID"]):
            continue
        icon = "unknown"
        if args.notify_icon_path and os.path.exists(args.notify_icon_path):
            icon = args.notify_icon_path
        if args.notify_command_template:
            # change all double quote or single quote or $ as unquoted
            subject = cleanup_str(uuid["Subject"])
            snippet = cleanup_str(uuid["snippet"])
            command = args.notify_command_template.format(
                icon=icon, subject=subject, snippet=snippet
            )
            os.system(command)


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
