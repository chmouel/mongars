import logging
import typing

import gi  # type:ignore

gi.require_version("Secret", "1")
gi.require_version("GLib", "2.0")

from gi.repository import GLib  # noqa: E402 # type:ignore


class AccountError(Exception):
    pass


try:
    gi.require_version("Goa", "1.0")
    from gi.repository import Goa  # type:ignore
except (ValueError, ModuleNotFoundError) as exp:
    raise AccountError("No gnome online accounts support found") from exp


class GOA:
    @staticmethod
    def get_accounts() -> typing.Optional[list]:
        accounts: list = []
        for account in GOA.get_goa_mails_accounts():
            accounts.append(GOA.get_credentials(account))
        return accounts

    @staticmethod
    def get_credentials(account) -> dict:
        # not doing password based auth, maybe later
        try:
            oauth2_based = account.get_oauth2_based()
            auth_token = oauth2_based.call_get_access_token_sync(None)
            user_name = account.get_mail().props.imap_user_name
            imap_host = account.get_mail().props.imap_host
        except GLib.Error as error:
            # pylint: disable=no-member
            if error.code == 0:
                raise AccountError("Account Offline") from error
            if error.code == 4:
                raise AccountError(
                    "Locked or Invalid credentials for GOA account"
                ) from error
            logging.error(
                "Unknown GLIB exception getting GOA credentials", exc_info=True
            )
            raise AccountError("Unknown error") from error
        except Exception as error:
            logging.info("Unknown exception getting GOA credentials", exc_info=True)
            raise AccountError("Unknown error") from error

        return {
            "host": imap_host,
            "user": user_name,
            "oauth": f"user={user_name}\1auth=Bearer {auth_token[0]}\1\1".encode(),
        }

    @staticmethod
    def get_goa_mails_accounts() -> typing.Generator:
        client = Goa.Client.new_sync(None)
        accounts = client.get_accounts()
        for account in accounts:
            mail = account.get_mail()
            if (
                not mail
                or account.get_account().props.mail_disabled
                or not mail.props.imap_supported
            ):
                continue
            yield account
