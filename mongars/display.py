import argparse
from email.header import decode_header

from .notify import notify_if_not_already


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


def show_unseens(args: argparse.Namespace, unseens: dict) -> str:
    if args.no_mail_no_zero and len(unseens) == 0:
        return ""
    if args.notify:
        notify_if_not_already(unseens)

    if args.show_from_subject:
        return "\n".join(unseens.values())

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
