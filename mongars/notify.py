import pathlib

import gi

# pylint: disable=C0413, W1202
gi.require_version('GLib', '2.0')

from gi.repository import GLib as glib  # type: ignore

try:
    # pylint: disable=wrong-import-position
    from gi.repository import Notify
except ModuleNotFoundError:
    Notify = None  # pylint: disable = C0103

PACKAGE_NAME = "mongars"

CACHE_PATH = pathlib.Path(
    f"{glib.get_user_cache_dir()}/{PACKAGE_NAME}/notified")
MAX_ENTRY_CACHE = 200  #if you have more than 200, it is insane...


def get_store_cache(uid: str) -> bool:
    ret = False
    CACHE_PATH.parent.mkdir(exist_ok=True)
    cached_entries = []
    if CACHE_PATH.exists():
        cached_entries = CACHE_PATH.read_text().split("\n")[0:MAX_ENTRY_CACHE]
    if uid in cached_entries:
        ret = True
    else:
        cached_entries.insert(0, uid)
    CACHE_PATH.write_text("\n".join(cached_entries))
    return ret


def notify_if_not_already(uuids: dict):
    unnotified = []
    for uuid in uuids.keys():
        if not get_store_cache(uuid):
            unnotified.append(uuid)

    if not unnotified:
        return
    plural = 's' if len(unnotified) > 1 else ""
    header = f"{len(unnotified)} new email{plural}"
    summary = "\r• ".join([uuids[x] for x in unnotified])
    summary = f"• {summary}"
    notify(header, summary, "mail-unread")


def notify(header, summary, icon):
    if not Notify:
        return

    Notify.init(PACKAGE_NAME.capitalize())
    notification = Notify.Notification.new(header, summary, icon)
    notification.set_category('email')
    notification.show()
