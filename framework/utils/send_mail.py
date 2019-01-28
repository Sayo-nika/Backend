from framework.sayonika import Sayonika
from flask_mail import Mail, Message

def send_mail(mail_type, recipient, replacers=[], replacing_values=[]):
    """
       Sends Mail and replaces values from array of replacers and replacing values.

       mail_type is dependent on the template files in mail_templates/, so make sure
       you make the template first before proceeding to define mail_type.
    """
    smtp = Mail()
    smtp.init_app(Sayonika)

    # If this doesn't work, put the blame to ovy, he suggested this.
    with open(f"./framework/mail_templaes/{mail_type}.html", "r") as f:

        for (replacers, replacing_values) in zip(replacers, replacing_values):

            data = f.read().replace(replacers, replacing_values)

            msg = Message(sender=("Sayonika", "noreply@sayonika.moe"), recipients=[recipient])
            msg.html = data

            smtp.send(msg)
