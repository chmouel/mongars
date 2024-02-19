import argparse
import html
import json
import shutil
import subprocess
import textwrap
from email.header import decode_header
from typing import Union


def decode_str(header):
    ret = []
    for thehe in decode_header(header):
        if thehe[1]:
            ret.append(thehe[0].decode(thehe[1]))
        else:
            if isinstance(thehe[0], str):
                ret.append(thehe[0])
            else:
                ret.append(thehe[0].decode())
    return "".join(ret)


def show_markdown(args: argparse.Namespace, unseens: list) -> str:
    if not unseens:
        return ""
    ret = f"# Email on {args.email}\n\n## Unread emails {len(unseens)}\n"
    for unseen in unseens:
        from_email = "<" in unseen["From"] and unseen["From"] or f"<{unseen['From']}>"
        to_email = "<" in unseen["To"] and unseen["To"] or f"<{unseen['To']}>"
        snippet_truncated = textwrap.fill(
            unseen["Snippet"],
            width=80,
        )
        snippet_truncated = html.unescape(snippet_truncated)
        ret += f"""
## Subject: {unseen['Subject']}
* **From**: {from_email}
* **To**: {to_email}
* **Date**: {unseen['Date']}

```
{snippet_truncated}
```
"""
    if shutil.which("gum") and not args.no_gum_output:
        cmdline = "gum format"
        output = subprocess.run(
            cmdline,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=True,
            check=True,
            input=ret.encode(),
        )
        return output.stdout.decode().strip()
    return ret


def show_json(args: argparse.Namespace, unseens: Union[list, dict]) -> str:
    if not unseens:
        return "{}"
    ret = {"text": f"{args.icon} {len(unseens)}", "tooltip": ""}
    for unseen in unseens[:5]:
        subject_wrap = textwrap.shorten(unseen["Subject"], width=50)
        ret["tooltip"] += f"• {unseen['From']}: {subject_wrap}\n"
    ret["tooltip"] = html.escape(ret["tooltip"])
    return json.dumps(ret)


def show_unseens(args: argparse.Namespace, unseens: Union[list, dict]) -> str:
    if args.no_mail_no_zero and len(unseens) == 0:
        return ""
    if args.show_from_subject:
        if isinstance(unseens, list):
            return "\n".join([x["Subject"] for x in unseens])
        return "\n".join(unseens.values())  # type: ignore

    if args.no_icon:
        return str(len(unseens))

    iconstring = f"{args.icon}"
    if len(unseens) == 0 and args.icon_color_normal:
        # pylint: disable=consider-using-f-string
        iconstring = "%%{F%s}%s%%{F-}" % (args.icon_color_normal, args.icon)
    elif len(unseens) > 0 and args.icon_color_unreads:
        # pylint: disable=consider-using-f-string
        iconstring = "%%{F%s}%s%%{F-}" % (
            args.icon_color_unreads,
            args.icon,
        )
    return f"{iconstring} {str(len(unseens))}"
