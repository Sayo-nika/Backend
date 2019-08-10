# Stdlib
from enum import Enum
import os.path as osp
from typing import Dict

# External Libraries
import aiofiles
import aiohttp

TEMPLATES_PATH = "./framework/mail_templates/__.html"


class MailTemplates(Enum):
    AccountSuspended = "account_suspended"
    ModApproved = "mod_approved"
    ModDeleted = "mod_deleted"
    ModRejected = "mod_rejected"
    ModRemoved = "mod_removed"
    ModSubmitted = "mod_submitted"
    VerifyEmail = "verify_email"


class MailSubjects:
    account_suspended = "Your account has beeen suspended"
    mod_approved = "Your mod has been approved"
    mod_deleted = "Your mod has been deleted"
    mod_rejected = "Your mod has been rejected"
    mod_removed = "Your mod has been removed"
    mod_submitted = "Your mod has been submitted"
    verify_email = "Verify your email"


class EmailFailed(Exception):
    pass


class Mailer:
    """Sending mail templates via Mailgun."""
    # XXX: switch to redis soon
    cached_templates = {}

    def __init__(self, settings: dict):
        # `settings` is the dict of all ENV vars starting with SAYONIKA_
        self.mailgun_key = settings["MAILGUN_KEY"]

    async def _get_template(self, template: MailTemplates) -> str:
        template_name = template.value
        template_path = TEMPLATES_PATH.replace("__", template_name)

        # Get from cache early if possible
        if template_name in self.cached_templates:
            return self.cached_templates[template_name]

        if not osp.exists(template_path):
            raise FileNotFoundError(f"Template `{template_name}` doesn't exist")

        async with aiofiles.open(template_path) as f:
            data = await f.read()

        self.cached_templates[template_name] = data

        return data

    async def send_mail(self, mail_type: MailTemplates, recipient: str, replacers: Dict[str, str],
                        session: aiohttp.ClientSession) -> None:
        """
        Send mail using a template, along with optionally replacing some values.
        Templates can be found in `framework/mail_templates`.
        """
        if not isinstance(mail_type, MailTemplates):
            raise TypeError("mail_type isn't a valid type")

        template = await self._get_template(mail_type)

        for (replace_string, replace_value) in replacers.items():
            # Five pairs of braces are needed, as `{{}}` escapes into `{}`, so we need to double that up and then also
            # interpolate our variable into them
            template = template.replace(f"{{{{{replace_string}}}}}", replace_value)

        msg = {"from": "Sayonika <noreply@sayonika.moe>",
               "subject": getattr(MailSubjects, mail_type.value),
               "to": [recipient],
               "html": template}

        async with session.post(
                "https://api.mailgun.net/v3/sayonika.moe/messages",
                auth=aiohttp.BasicAuth("api", self.mailgun_key),
                data=msg) as resp:
            if resp.status == 200:
                return True
            raise EmailFailed
