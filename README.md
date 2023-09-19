# mongars - count inbox emails

count inbox emails using Gnome Online Accounts

## Description

`mongars` will take an email account as configured in Gnome Online account (only
oauth based email account is supported) or via the GMAIL Api and will output how many unread emails
you have in there.

## Usage

### Gmail API

You need to [generate a OAUTH
credentials.json](https://developers.google.com/workspace/guides/create-credentials)
via the google API console.

When it's done using [pass](https://www.passwordstore.org/) you need to insert it in your pass store:

```shell
pass insert -m google/$EMAIL.mail.credential
INSERT YOUR CREDENTIALS HERE
```

Run `mongars` for the first time with the flag `--gauth` and your `$EMAIL` as
argument:

```shell
mongars --gauth $EMAIL
```

it will start your webbrowser to allow it to access to read your email
on your `$EMAIL.` It stores and refresh the token in the password store key
`google/$EMAIL.mail.token`

you can define the pass key to other values by defining the flags
`--gauth-pass-token-key` and `--gauth-pass-cred-key`

You can output a markdown formatted (optionally) with `gum` if you pass the
option `-M/--show-markdown`

![Screenshot_2023-09-19-14 13 14(1)](https://github.com/chmouel/mongars/assets/98980/fcd49e1f-fbc6-45ed-bd9c-d6780dbcbd5a)


You can output as json for waybar with `-J/--show-json` and it will show a tooltip of your last 5 message and subject snippet.

![](https://github.com/chmouel/mongars/assets/98980/79f200a6-1b71-4654-b424-65c36a85e2e5)


### Gnome Online Accounts

You just need to specify the email to check as an argument i.e:

```shell
mongars john.snow@gmail.com
```

By default it will output the number of messages from your mailbox with an icon of different
colours if there is unreads message or not.

The `INBOX` folder is the default folder, if you would like to count another folder you can specify the `-m` option to it :

```shell
mongars -m Label1 john.snow@gmail.com
```

You can further customize the colour output which uses lemonbar formatting with :

* `--icon`: the glyph icon default to ``
* `--icon-color-unreads`: the color when unreads, default to a yellow `#ffd700` set this to empty if you don't want any color formatting.
* `--icon-color-normal`: the normal colors. (no default)

By default if you have no mail it will output a 0 unless you specify the flag `--no-mail-no-zero`

If you don't want any icons you can simply use the `--no-icon` and it will just output the number.

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
exec = mongars email@gmail.com
interval = 30
click-left = xdg-open https://mail.google.com/
exec-if = grep -q email@gmail.com ~/.config/goa-1.0/accounts.conf 2>/dev/null && ping -c1 mail.google.com
```


## Waybar
```json
    "custom/email": {
        "format": " {} ",
        "interval": 15,
        "exec": "mongars email@gmail.com --no-mail-no-zero --no-icon",
        "on-click": "xdg-open https://mail.google.com"
    },
```

and you can style it in `style.css` file :

```css
#custom-email {
	color: #b22222;
}
```

#### Waybar as Json with Gauth

The gauth method support output to json, here is an example integrating it:

```json
{
    "custom/email-work": {
        "format": "{} ",
        "return-type": "json",
        "tooltip": "true",
        "tooltip-format": "{tooltip}",
        "interval": 15,
        "exec": "poetry run mongars --gauth myemail@gmail.com -J",
        "on-click-middle": "kitty -T \"Email for myemail@gmail.com\" bash -c \"mongars --gauth myemail@gmail.com -M|less -R\"",
        "on-click": "xdg-open https://mail.google.com/"
    },
}
```

## License

[Apache 2.0](./LICENSE)

## Authors

© 2021 Chmouel Boudjnah ([@chmouel](https://twitter.com/chmouel)) - https://chmouel.com
