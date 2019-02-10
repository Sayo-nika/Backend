# Stdlib
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
    account_suspended = 'Your account has beeen suspended'
    mod_approved = 'Your mod has been approved'
    mod_deleted = 'Your mod has been deleted'
    mod_rejected = 'Your mod has been rejected'
    mod_removed = 'Your mod has been removed'
    mod_submitted = 'Your mod has been submitted'
    verify_email = 'Verify your email'


class Mailer(Mail):
    # XXX: switch to redis soon
    cached_templates = {}

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

        msg = Message(sender=("Sayonika", "noreply@sayonika.moe"), subject=getattr(MailSubjects, mail_type.value),
                      recipients=[recipient], html=template, charset='utf-8')

        self.send(msg)
