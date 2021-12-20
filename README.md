# mongars - count inbox emails

count inbox emails using Gnome Online Accounts

## Description

`mongars` will take an email account as configured in Gnome Online account (only
oauth based email account is supported) and will output how many unread emails
you have in there.

You just need to specify the email to check as an argument i.e:

```shell
mongars john.snow@gmail.com
```

by default it will count the unread messages in the `INBOX` folder, if you
woulld like to count another folder you can specify the -m option to it :

```shell
mongars -m Label1 john.snow@gmail.com
```

This currently only support oauth2 based accounts, imap account with username,
password are not currently supported (patch welcome but you probably want to use
something more secure).

## Running it without Gnome

If you run this without gnome environement, you have to configure the accounts
first in Gnone Online Account settings.

From your window manager or somewhere else you need to make sure to run the goa-daemon, for example on arch the path is `/usr/lib/goa-daemon` and from your startup script you will do :

```shell
/usr/lib/goa-daemon --replace &
```

different distros may have a different path, see also this bugzilla bug
[#1340203](https://bugzilla.redhat.com/show_bug.cgi?id=1340203))
