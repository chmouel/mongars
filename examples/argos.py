#!/usr/bin/env python
# integrate with argos/pew https://github.com/p-e-w/argos config your ACCOUNTS
# array and copy this file in ~/.config/argos/email.l.120s.py
# see project documentation for more details
import subprocess

import mongars.cli as mong

ACCOUNTS = {
    "Work": ("workemail@work.com", "https://mail.company.com", "red"),
    "Gmail": ("personalemail@gmail.com", "https://mail.google.com/", "blue"),
}

UNREAD_ICON = "mail-unread-symbolic"
READ_ICON = "mail-read-symbolic"


def check_accounts(accounts):
    ret = {}
    totals = 0
    for account in accounts.items():
        email = account[1][0]
        args = mong.parse_args(["--show-from-subject", email])
        emails = mong.check_accounts(args)
        ret[email] = [x for x in emails.split("\n") if x.strip()]
        totals += len(ret[email])
    return totals, ret


# use NetworkManager to checks if we are online
def check_online() -> bool:
    try:
        subprocess.run("nm-online -t 1", shell=True, check=True, stdout=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    if not check_online():
        print(f"? | iconName={READ_ICON} color=red")
        return

    totals, emails = check_accounts(ACCOUNTS)
    icon = UNREAD_ICON if totals > 0 else READ_ICON

    print(f"{totals} | iconName={icon}")
    for account in ACCOUNTS.items():
        print("---")
        accountmail = account[1][0]
        print(f"{account[0]} - {len(emails[accountmail])} | href={account[1][1]} ")
        # print("---")
        # for newmail in emails[accountmail]:
        #     print(f"{newmail} | color={account[1][2]}")
    print("---\nRefresh | refresh=true")


main()
