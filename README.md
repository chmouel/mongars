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

I only tested it with Google/Gmail accounts (enteprise and personal) so let me
know if it works or not on other oauth2 based email accounts.

## Install

### Arch

You can install this [from aur](https://aur.archlinux.org/packages/mongars) with your aurhelper, like yay :

```
yay -S mongars
```

### pip

With pip from pypip - https://pypi.org/project/mongars/

```
pip install --user mongars
```

(make sure $HOME/.local/bin is in your PATH)

### Manual

Checkout this repository, [install poetry](https://python-poetry.org/docs/#installation) and run it with :

```shell
poetry install mongars
poetry run mongars
```

## Running it without Gnome

If you run this outside of gnome environement (ie: from a windows manager), you have to configure the accounts
first in Gnone Online Account settings from gnome and then you can use it from your windows manager.

From your window manager start scripts or [somewhere else](https://wiki.archlinux.org/title/Xinit)  you need to make sure to run the goa-daemon, for example on arch the path is `/usr/lib/goa-daemon` and from your startup script you will do :

```shell
/usr/lib/goa-daemon --replace &
```

different distros may have a different path, see also this bugzilla bug
[#1340203](https://bugzilla.redhat.com/show_bug.cgi?id=1340203))

## Polybar

You can easily integrate this with [Polybar](https://github.com/polybar/polybar) :

```ini
[module/email]
type = custom/script
format-prefix = " "
exec = mongars email@gmail.com
format-prefix-foreground = #ffd700
interval = 5
click-left = xdg-open https://mail.google.com/
```

It will only shows up when you have emails.

Sames goes for the integration with other bars like [waybar](https://github.com/Alexays/Waybar/)

## License

[Apache](./LICENSE)

## Authors

© 2021 Chmouel Boudjnah ([@chmouel](https://twitter.com/chmouel)) - https://chmouel.com
