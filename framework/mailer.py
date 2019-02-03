# Stdlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import os.path as osp
from typing import Dict

# External Libraries
import aiofiles
from flask_mail import Mail, Message

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
    account_suspended = ''
    mod_approved = ''
    mod_deleted = ''
    mod_rejected = ''
    mod_removed = ''
    mod_submitted = ''
    verify_email = ''


class Mailer(Mail):
    # XXX: switch to redis soon
    cached_templates = {}

    def __init__(self):
        super().__init__()
        self.executor = ThreadPoolExecutor(4)

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

    async def send_mail(self, mail_type: MailTemplates, recipient: str, replacers: Dict[str, str]) -> None:
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

        msg = Message(sender=("Sayonika", "noreply@sayonika.moe"), subject=MailSubjects.get(mail_type.value),
                      recipients=[recipient], html=template, charset='utf-8')
        loop = asyncio.get_running_loop()

        # Send the email in another thread as flask-mail is sync
        await loop.run_in_executor(self.executor, self.send, msg)
